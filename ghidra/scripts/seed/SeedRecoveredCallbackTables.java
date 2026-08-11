//@author kaikozlov
//@category Analysis
// Persist callback functions whose table schema, dispatcher, exact bodies, and
// indirect call path were independently validated from firmware bytes.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

import java.security.MessageDigest;

public class SeedRecoveredCallbackTables extends GhidraScript {
    private static final long TABLE = 0x2b3f0L;
    private static final int STRIDE = 8;
    private static final long DISPATCHER = 0x97160L;
    private static final long INDIRECT_CALL = 0x971a2L;

    private static final class Entry {
        final int selector;
        final long target;
        final int size;
        final String sha256;

        Entry(int selector, long target, int size, String sha256) {
            this.selector = selector;
            this.target = target;
            this.size = size;
            this.sha256 = sha256;
        }

        String name() {
            return String.format("xcp_command_%02x_handler", selector);
        }
    }

    private static final Entry[] ENTRIES = {
        new Entry(0xfb, 0x9729aL, 74,
            "65e792f96dc7cd1e08df9ced0309109b115144e3797b9ed9014afed4a23f6cf9"),
        new Entry(0xfa, 0x972faL, 96,
            "4a0e238c48e006ca4ac32418f048b5732b72d6ce57fc5fa418e9593fc7c0eeaf"),
        new Entry(0xf5, 0x97432L, 100,
            "b0cc2e993a01ef4c6bd49a8aeb8096f51cfd4447150a89bf153cbe1ec8df15a0"),
        new Entry(0xf3, 0x97546L, 168,
            "8931f1c77b2df68fdc6633ac1981978e82675d29ad91c6e8472349e2327569bd"),
        new Entry(0xeb, 0x975eeL, 122,
            "5e84ef82874096886d694b6f88d6083cd2fffa3728a0c10086442940f170161d"),
        new Entry(0xea, 0x97668L, 104,
            "666f9153b152fbd6e152322b49e61fb414080d88ac476934df7ea6a6f063fc4d"),
        new Entry(0xe4, 0x976f4L, 106,
            "14367502c37c230022c4c3d55fded0377095e663d89fbe83efc0834efa84050b"),
    };

    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        ReferenceManager references = currentProgram.getReferenceManager();

        requireDispatcher(listing, functions);
        ensureLabel(TABLE, "xcp_command_dispatch_table");

        int created = 0;
        int existing = 0;
        int clearedData = 0;
        for (int index = 0; index < ENTRIES.length; index++) {
            Entry entry = ENTRIES[index];
            Address record = toAddr(TABLE + index * STRIDE);
            Address pointerField = record.add(4);
            Address target = toAddr(entry.target);
            Address bodyEnd = target.add(entry.size - 1L);

            requireRecord(index, record, entry);
            requireBodyHash(entry);

            Function containing = functions.getFunctionContaining(target);
            if (containing != null && !containing.getEntryPoint().equals(target)) {
                throw new IllegalStateException(String.format(
                    "0x%x is an alternate entry into %s @ %s",
                    entry.target, containing.getName(), containing.getEntryPoint()));
            }

            var dataIterator = listing.getDefinedData(
                new AddressSet(target, bodyEnd), true);
            while (dataIterator.hasNext()) {
                Data data = dataIterator.next();
                if (data.getMinAddress().compareTo(target) < 0
                        || data.getMaxAddress().compareTo(bodyEnd) > 0) {
                    throw new IllegalStateException(String.format(
                        "validated body 0x%x overlaps external data %s..%s",
                        entry.target, data.getMinAddress(), data.getMaxAddress()));
                }
                listing.clearCodeUnits(data.getMinAddress(), data.getMaxAddress(), false);
                clearedData++;
            }

            Instruction instruction = listing.getInstructionContaining(target);
            if (instruction != null && !instruction.getAddress().equals(target)) {
                throw new IllegalStateException(String.format(
                    "validated target 0x%x is inside instruction %s",
                    entry.target, instruction.getAddress()));
            }
            if (listing.getInstructionAt(target) == null && !disassemble(target)) {
                throw new IllegalStateException(String.format(
                    "failed to disassemble callback 0x%x", entry.target));
            }

            Function function = functions.getFunctionAt(target);
            if (function == null) {
                function = createFunction(target, entry.name());
                if (function == null) {
                    throw new IllegalStateException(String.format(
                        "failed to create callback function 0x%x", entry.target));
                }
                created++;
            } else {
                existing++;
                if (!entry.name().equals(function.getName())) {
                    function.setName(entry.name(), SourceType.USER_DEFINED);
                }
            }
            if (function.getBody().getNumAddresses() != entry.size) {
                throw new IllegalStateException(String.format(
                    "callback 0x%x body size=%d expected=%d",
                    entry.target, function.getBody().getNumAddresses(), entry.size));
            }
            if (!"__stdcall".equals(function.getCallingConventionName())) {
                function.setCallingConvention("__stdcall");
            }

            for (var reference : references.getReferencesFrom(pointerField)) {
                if (reference.getToAddress().equals(target)
                        && reference.getReferenceType().isData()) {
                    references.delete(reference);
                }
            }
            references.addMemoryReference(
                pointerField, target, RefType.DATA, SourceType.USER_DEFINED, 0);
            ensureLabel(pointerField.getOffset(),
                String.format("xcp_command_%02x_callback_ptr", entry.selector));
        }

        println(String.format(
            "SeedRecoveredCallbackTables: entries=%d created=%d existing=%d cleared_data=%d",
            ENTRIES.length, created, existing, clearedData));
    }

    private void requireDispatcher(Listing listing, FunctionManager functions) throws Exception {
        Function dispatcher = functions.getFunctionAt(toAddr(DISPATCHER));
        if (dispatcher == null) {
            throw new IllegalStateException("missing callback dispatcher at 0x97160");
        }
        requireBytes(0x9718cL, "01f0c3f225960c75d2f16090f2998a0d02ed");
        requireBytes(0x9719eL, "1b301a38fdc760f901eac505410a670af6ed");
        Instruction indirect = listing.getInstructionAt(toAddr(INDIRECT_CALL));
        if (indirect == null || !"jarl".equals(indirect.getMnemonicString())
                || !indirect.getFlowType().isCall() || !indirect.getFlowType().isComputed()) {
            throw new IllegalStateException("0x971a2 is not the validated computed jarl");
        }
    }

    private void requireRecord(int index, Address record, Entry entry) throws Exception {
        if ((currentProgram.getMemory().getByte(record) & 0xff) != entry.selector
                || currentProgram.getMemory().getByte(record.add(1)) != 0
                || currentProgram.getMemory().getByte(record.add(2)) != 0
                || currentProgram.getMemory().getByte(record.add(3)) != 0) {
            throw new IllegalStateException("unexpected selector/padding at " + record);
        }
        long pointer = currentProgram.getMemory().getInt(record.add(4)) & 0xffffffffL;
        if (pointer != entry.target) {
            throw new IllegalStateException(String.format(
                "record %d pointer=0x%x expected=0x%x", index, pointer, entry.target));
        }
    }

    private void requireBodyHash(Entry entry) throws Exception {
        byte[] bytes = new byte[entry.size];
        currentProgram.getMemory().getBytes(toAddr(entry.target), bytes);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        StringBuilder actual = new StringBuilder();
        for (byte value : digest.digest(bytes)) actual.append(String.format("%02x", value & 0xff));
        if (!entry.sha256.equals(actual.toString())) {
            throw new IllegalStateException(String.format(
                "callback 0x%x body hash=%s expected=%s",
                entry.target, actual, entry.sha256));
        }
    }

    private void requireBytes(long address, String expectedHex) throws Exception {
        byte[] actual = new byte[expectedHex.length() / 2];
        currentProgram.getMemory().getBytes(toAddr(address), actual);
        StringBuilder actualHex = new StringBuilder();
        for (byte value : actual) actualHex.append(String.format("%02x", value & 0xff));
        if (!expectedHex.equals(actualHex.toString())) {
            throw new IllegalStateException(String.format("byte mismatch at 0x%x", address));
        }
    }

    private void ensureLabel(long address, String name) throws Exception {
        SymbolTable symbols = currentProgram.getSymbolTable();
        for (Symbol symbol : symbols.getSymbols(toAddr(address))) {
            if (name.equals(symbol.getName())) return;
        }
        symbols.createLabel(toAddr(address), name, SourceType.USER_DEFINED);
    }
}
