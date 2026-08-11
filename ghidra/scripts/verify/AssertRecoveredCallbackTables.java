//@author kaikozlov
//@category Verification
// Assert the durable 0x2B3F0 callback-table recovery without mutating Ghidra.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;

public class AssertRecoveredCallbackTables extends GhidraScript {
    private static final long TABLE = 0x2b3f0L;
    private static final int[] SELECTORS = {0xfb, 0xfa, 0xf5, 0xf3, 0xeb, 0xea, 0xe4};
    private static final long[] TARGETS = {
        0x9729aL, 0x972faL, 0x97432L, 0x97546L, 0x975eeL, 0x97668L, 0x976f4L,
    };
    private static final int[] SIZES = {74, 96, 100, 168, 122, 104, 106};
    private static final String[] HASHES = {
        "65e792f96dc7cd1e08df9ced0309109b115144e3797b9ed9014afed4a23f6cf9",
        "4a0e238c48e006ca4ac32418f048b5732b72d6ce57fc5fa418e9593fc7c0eeaf",
        "b0cc2e993a01ef4c6bd49a8aeb8096f51cfd4447150a89bf153cbe1ec8df15a0",
        "8931f1c77b2df68fdc6633ac1981978e82675d29ad91c6e8472349e2327569bd",
        "5e84ef82874096886d694b6f88d6083cd2fffa3728a0c10086442940f170161d",
        "666f9153b152fbd6e152322b49e61fb414080d88ac476934df7ea6a6f063fc4d",
        "14367502c37c230022c4c3d55fded0377095e663d89fbe83efc0834efa84050b",
    };
    private final List<String> failures = new ArrayList<>();

    @Override
    public void run() throws Exception {
        requireLabel(TABLE, "xcp_command_dispatch_table");
        Instruction indirect = getInstructionAt(toAddr(0x971a2L));
        require(indirect != null && "jarl".equals(indirect.getMnemonicString())
            && indirect.getFlowType().isCall() && indirect.getFlowType().isComputed(),
            "dispatcher computed jarl at 0x971a2");

        for (int index = 0; index < TARGETS.length; index++) {
            Address record = toAddr(TABLE + index * 8L);
            Address pointerField = record.add(4);
            Address target = toAddr(TARGETS[index]);
            int selector = currentProgram.getMemory().getByte(record) & 0xff;
            long pointer = currentProgram.getMemory().getInt(pointerField) & 0xffffffffL;
            require(selector == SELECTORS[index], String.format(
                "record %d selector 0x%02x", index, SELECTORS[index]));
            require(pointer == TARGETS[index], String.format(
                "record %d target 0x%x", index, TARGETS[index]));

            Function function = getFunctionAt(target);
            String expectedName = String.format("xcp_command_%02x_handler", SELECTORS[index]);
            require(function != null, "function " + expectedName + " exists");
            if (function != null) {
                require(expectedName.equals(function.getName()),
                    expectedName + " exact name");
                require(function.getSymbol().getSource() == SourceType.USER_DEFINED,
                    expectedName + " name provenance");
                require(function.getBody().getNumAddresses() == SIZES[index],
                    expectedName + " exact body size");
                require("__stdcall".equals(function.getCallingConventionName()),
                    expectedName + " calling convention");
            }
            require(HASHES[index].equals(bodyHash(TARGETS[index], SIZES[index])),
                expectedName + " body hash");
            requireReference(pointerField, target, expectedName);
            requireLabel(pointerField.getOffset(),
                String.format("xcp_command_%02x_callback_ptr", SELECTORS[index]));
        }

        if (!failures.isEmpty()) {
            throw new IllegalStateException(
                "recovered callback-table assertions failed: " + String.join("; ", failures));
        }
        println("AssertRecoveredCallbackTables: PASS entries=" + TARGETS.length);
    }

    private void require(boolean condition, String message) {
        if (!condition) {
            failures.add(message);
            println("FAIL: " + message);
        }
    }

    private void requireReference(Address from, Address to, String name) {
        for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(from)) {
            if (reference.getToAddress().equals(to)
                    && reference.getReferenceType().isData()
                    && reference.getSource() == SourceType.USER_DEFINED) {
                return;
            }
        }
        require(false, name + " pointer reference");
    }

    private void requireLabel(long address, String name) {
        for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(toAddr(address))) {
            if (name.equals(symbol.getName()) && symbol.getSource() == SourceType.USER_DEFINED) {
                return;
            }
        }
        require(false, "label " + name + " at " + toAddr(address));
    }

    private String bodyHash(long address, int size) throws Exception {
        byte[] bytes = new byte[size];
        currentProgram.getMemory().getBytes(toAddr(address), bytes);
        StringBuilder result = new StringBuilder();
        for (byte value : MessageDigest.getInstance("SHA-256").digest(bytes)) {
            result.append(String.format("%02x", value & 0xff));
        }
        return result.toString();
    }
}
