//@author kaikozlov
//@category Seed
// Verified yc 2024 RAV4 Prime meter findings; see docs/variants/yc-r4p-2024-meter.md.
// Relocation bytes and GP/TP/EP belong to the device profile, not this script.
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class SeedR4pMeterDiagnostics extends GhidraScript {
  private Function ensure(long value, String name) throws Exception {
    Address address = toAddr(value);
    Listing listing = currentProgram.getListing();
    Instruction containing = listing.getInstructionContaining(address);
    if (containing != null && !containing.getMinAddress().equals(address))
      listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
    CodeUnit unit = listing.getCodeUnitContaining(address);
    if (unit != null && !(unit instanceof Instruction))
      listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
    if (listing.getInstructionAt(address) == null && !disassemble(address))
      throw new IllegalStateException("disassembly failed " + address);
    Function function = getFunctionAt(address);
    if (function == null) function = createFunction(address, name);
    if (function == null) throw new IllegalStateException("function creation failed " + address);
    if (name != null && !name.equals(function.getName()))
      function.setName(name, SourceType.USER_DEFINED);
    return function;
  }

  private long u32(long address) throws Exception {
    return Integer.toUnsignedLong(currentProgram.getMemory().getInt(toAddr(address)));
  }

  private int u16(long address) throws Exception {
    return Short.toUnsignedInt(currentProgram.getMemory().getShort(toAddr(address)));
  }

  private int u8(long address) throws Exception {
    return Byte.toUnsignedInt(currentProgram.getMemory().getByte(toAddr(address)));
  }

  private void expect(long address, long actual, long expected) {
    if (actual != expected)
      throw new IllegalStateException(String.format("meter geometry drift at %08x: %x != %x",
          address, actual, expected));
  }

  private void word(long address, long expected) throws Exception {
    expect(address, u32(address), expected);
  }

  private void half(long address, int expected) throws Exception {
    expect(address, u16(address), expected);
  }

  private void byteValue(long address, int expected) throws Exception {
    expect(address, u8(address), expected);
  }

  private void label(long address, String name) throws Exception {
    Symbol symbol = currentProgram.getSymbolTable().getSymbol(name, toAddr(address), null);
    if (symbol == null)
      symbol = currentProgram.getSymbolTable().createLabel(toAddr(address), name,
          SourceType.USER_DEFINED);
    symbol.setPrimary();
  }

  private void data(long address, DataType type, String name) throws Exception {
    Address start = toAddr(address);
    Address end = start.add(type.getLength() - 1L);
    // These are verified tables/arrays, including any spurious function entries
    // created there by early speculative analysis. Never retain them as code.
    List<Address> bogus = new ArrayList<>();
    FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(
        new AddressSet(start, end), true);
    while (functions.hasNext()) bogus.add(functions.next().getEntryPoint());
    for (Address entry : bogus) currentProgram.getFunctionManager().removeFunction(entry);
    currentProgram.getListing().clearCodeUnits(start, end, false);
    createData(start, type);
    label(address, name);
  }

  private void bytes(long address, int size, String name) throws Exception {
    data(address, new ArrayDataType(ByteDataType.dataType, size, 1), name);
  }

  private DataType pointer() {
    return new PointerDataType(ByteDataType.dataType, 4, currentProgram.getDataTypeManager());
  }

  private void pinTables() throws Exception {
    // 2389A searches 74 rows using DID at +18, stride 20. Pin the first,
    // last, and independently verified 1101/2041/2831 rows before following pointers.
    half(0x1568CAL, 0x010b);
    half(0x156E7EL, 0x2a22);
    word(0x156A0CL, 0x27476); word(0x156A10L, 0x2849c); half(0x156A1EL, 0x1101);
    word(0x156B24L, 0x276ae); word(0x156B28L, 0x2881c);
    word(0x156B2CL, 0x28ca6); half(0x156B36L, 0x2041);
    word(0x156CDCL, 0x277f4); word(0x156CE8L, 0x293f4); half(0x156CEEL, 0x2831);
    StructureDataType did = new StructureDataType("R4pMeterDidRow", 0);
    did.add(pointer(), "support", null);
    did.add(pointer(), "read", null);
    did.add(pointer(), "write", null);
    did.add(pointer(), "io_control", null);
    did.add(UnsignedShortDataType.dataType, "flags", null);
    did.add(UnsignedShortDataType.dataType, "did", null);
    data(0x1568B8L, new ArrayDataType(did, 74, 20), "r4p_diagnostic_did_table");
    int previous = -1;
    for (int row = 0; row < 74; row++) {
      long base = 0x1568B8L + row * 20L;
      int id = u16(base + 18);
      if (id <= previous) throw new IllegalStateException("unordered meter DID row " + row);
      previous = id;
      for (int field = 0; field < 4; field++) {
        long callback = u32(base + field * 4L);
        if (callback == 0) continue;
        if ((callback & 1) != 0 || callback < 0x272e2 || callback > 0x29ac4)
          throw new IllegalStateException("invalid meter DID callback at " + toAddr(base));
        ensure(callback, null); // Table membership proves existence, not a semantic name.
        currentProgram.getReferenceManager().addMemoryReference(toAddr(base + field * 4L),
            toAddr(callback), RefType.DATA, SourceType.USER_DEFINED, 0);
      }
    }

    // Application SID27: two 16-byte subfunction rows; no 01/02 aliases.
    word(0x172414L, 0xaf3e0); word(0x17241CL, 0x172343); byteValue(0x172420L, 3);
    word(0x172424L, 0xaf3f4); word(0x17242CL, 0x172344); byteValue(0x172430L, 4);
    StructureDataType sub = new StructureDataType("R4pMeterSecuritySubfunction", 0);
    sub.add(pointer(), "handler", null);
    sub.add(pointer(), "reserved", null);
    sub.add(pointer(), "policy", null);
    sub.add(ByteDataType.dataType, "subfunction", null);
    sub.add(new ArrayDataType(ByteDataType.dataType, 3, 1), "flags", null);
    data(0x172414L, new ArrayDataType(sub, 2, 16), "r4p_app_sid27_subfunctions_03_04");
    word(0x172628L, 0x172414); byteValue(0x17262CL, 0x27);
    byteValue(0x1727E0L, 2); word(0x1727E4L, 0); word(0x1727F4L, 16); word(0x1727F8L, 16);
    bytes(0x1727E0L, 32, "r4p_app_security_access_configuration");

    // BootFlash and its initialized runtime copy have identical 32-byte SID27
    // registration rows. Runtime source row is BootFlash offset 774C, not 7754.
    for (long base : new long[] {0x0100774CL, 0xFEDD4EF4L}) {
      byteValue(base, 0x27); byteValue(base + 1, 2);
      word(base + 4, 0xfedcbf02L); word(base + 12, 0xfedcbf38L);
      word(base + 16, 0xfedcbe6cL); word(base + 20, 0xfedcbe86L);
      word(base + 28, 0xfedcbf68L);
      bytes(base, 32, base < 0x10000000L ? "r4p_boot_sid27_registration_rom" :
          "r4p_boot_sid27_registration_runtime");
    }
    for (long base : new long[] {0x010078DAL, 0xFEDD5082L}) {
      byteValue(base, 1); byteValue(base + 1, 2);
      half(base + 2, 16); half(base + 4, 16);
      bytes(base, 8, base < 0x10000000L ? "r4p_boot_sid27_configuration_rom" :
          "r4p_boot_sid27_configuration_runtime");
    }
    word(0xD11CL, 0xfedd7ff0L); word(0xD124L, 0xfedd7800L); word(0xD128L, 0x800);
    bytes(0xD11CL, 16, "r4p_payload_ram_descriptor_rom");
    word(0xFEDD4B08L, 0xfedd7ff0L); word(0xFEDD4B10L, 0xfedd7800L);
    word(0xFEDD4B14L, 0x800);
    bytes(0xFEDD4B08L, 16, "r4p_payload_ram_descriptor_runtime");
  }

  private void keyData() throws Exception {
    word(0xD344L, 0xfedd4d4cL); word(0xFEDD4D30L, 0xfedd4d4cL);
    word(0xD2ACL, 0xfedd4d3cL); word(0xFEDD4C98L, 0xfedd4d3cL);
    data(0xD344L, pointer(), "r4p_boot_sa_root_pointer_rom");
    data(0xFEDD4D30L, pointer(), "r4p_boot_sa_root_pointer");
    data(0xD2ACL, pointer(), "r4p_payload_root_pointer_rom");
    data(0xFEDD4C98L, pointer(), "r4p_payload_root_pointer");
    bytes(0xD360L, 16, "r4p_boot_sa_root_rom");
    bytes(0xFEDD4D4CL, 16, "r4p_boot_sa_root");
    bytes(0xD350L, 16, "r4p_payload_root_rom");
    bytes(0xFEDD4D3CL, 16, "r4p_payload_root");
    bytes(0x165730L, 32, "r4p_app_sa_xorshift_initializers");
    bytes(0x165750L, 16, "r4p_app_sa_nibble_sbox");
    data(0x165760L, new ArrayDataType(new ArrayDataType(ByteDataType.dataType, 16, 1),
        11, 16), "r4p_app_sa_round_keys");
    bytes(0x165810L, 128, "r4p_app_sa_bit_permutation");
    bytes(0xD370L, 16, "r4p_boot_seed_zero_input_rom");
    bytes(0xD380L, 16, "r4p_boot_seed_zero_iv_rom");
    bytes(0xFEDD543CL, 16, "r4p_boot_seed_zero_input");
    bytes(0xFEDD544CL, 16, "r4p_boot_seed_zero_iv");
    bytes(0xFEDD546DL, 256, "r4p_aes_encryption_sbox");
    // Mutable state labels describe the reprogramming phase, not app-RAM values.
    label(0xFEDD3506L, "r4p_reprog_did0201");
    label(0xFEDD3516L, "r4p_reprog_did0202");
    label(0xFEDD3554L, "r4p_boot_sa_aes_context");
    label(0xFEDD7800L, "r4p_authenticated_payload_start");
    label(0xFEDD7FF0L, "r4p_authenticated_payload_tag");
  }

  private void namedFunctions() throws Exception {
    long[] addresses = {
      0x2389a,0x23c36,0x2849c,0x2881c,0x2db32,0x2d380,0x2adf2,0x5ce50,
      0x1f88c,0x1f8be,0x16390,0x162de,
      0x19710,0x19732,0x19784,0x7a98c,0x7a9b8,0x7aa30,0xaf3e0,0xaf3f4,
      0xfedc6ca0L,0xfedc6dc2L,0xfedc6d56L,0xfedc6d8eL,0xfedc6c54L,0xfedc6bc8L,
      0xfedcbe6cL,0xfedcbd8aL,0xfedcb90cL,
      0xfedc5ff0L,0xfedc4bc2L,0xfedc6054L,0xfedc60a6L,0xfedc5e90L,0xfedc5eacL,
      0xfedc4948L,0xfedc49d4L,0xfedc4a68L,0xfedc4c48L,0xfedc4c70L,
      0xfedc6228L,0xfedc625eL,0xfedc6294L,0xfedc6412L,0xfedc6460L,
      0xfedd0b1eL,0xfedd0bbeL,0xfedd0d66L,0xfedd0eccL,0xfedd1020L,
      0xfedd03d8L,0xfedd04c4L,0xfedd0196L,0xfedd02b4L,
      0xfedc592cL,0xfedc5946L,0xfedc5954L,
      0x7982c,0x797da,0xa7cd4,0xa4502,0xa4280,0x9c618,0x9c66a,0x768b4,
      0x1537a,0x15734,0x15a8e,0x15bd2,0x15d70,0x6230e,0x62fb4,0x62f80,
      0x62e9c,0x62e66,0x6310a,0x12f08,0x4f944
    };
    String[] names = {
      "did_support_lookup","did_read_dispatch","did1101_read","did2041_read",
      "did1101_read_service","did2041_read_service","did2041_masked_setting_get",
      "did2041_support_build","multidisplay_control_commit","multidisplay_control_return",
      "display_mailbox_write","display_mailboxes_serialize",
      "app_sa_reset","app_sa_seed_generate","app_sa_key_verify","app_sa_xorshift128",
      "app_sa_seed_expand","app_sa_response_transform","app_sa_sub03_request_seed",
      "app_sa_sub04_send_key","boot_sa_request_seed","boot_sa_send_key",
      "boot_sa_derive_working_key","boot_sa_encrypt_seed","boot_sa_seed_generate",
      "boot_sa_seed_dynamic_aes","boot_sa_dispatch","boot_sa_request_dispatch",
      "boot_sa_subfunction_validate","payload_decrypt_key_derive","payload_auth_key_derive",
      "payload_cbc_setup","payload_decryption_setup","payload_decrypt_block",
      "payload_decrypt_step","payload_cmac_feed_iv","payload_cmac_feed_plaintext",
      "payload_cmac_tag_compare","payload_authentication_setup","payload_auth_region_select",
      "did0201_write","did0202_write","reprog_wdbi_dispatch","did0201_read","did0202_read",
      "aes_cmac_subkeys","aes_cmac_update","aes_cmac_key_setup","aes_cbc_decrypt_block",
      "aes_cbc_key_iv_setup","aes128_expand_key","aes128_key_setup","aes128_encrypt_block",
      "aes128_decrypt_block","aes128_key_setup_adapter","aes128_encrypt_block_adapter",
      "aes128_decrypt_block_adapter","byte_fill","byte_copy","can_rx_channel_dispatch",
      "can_rx_accept_copy","can_rx_timeout_tick","can_rx_status","can_signal_extract",
      "can3b7_b2_bits2_3_get","raw_spi_packet_build","spi_dma_transfer_start",
      "spi_packet_exchange","spi_packet_publish","spi_packet_transmit","rx_record_capture",
      "rx_records_assemble","rx_record_sample_select","rx_record_fragment_update",
      "rx_record_halfwords_unpack","rx_record_publish","processed_spi_packet_build",
      "can411_3b7_composite_build"
    };
    if (addresses.length != names.length) throw new IllegalStateException("meter names drift");
    for (int i = 0; i < addresses.length; i++) ensure(addresses[i], "r4p_" + names[i]);
    getFunctionAt(toAddr(0x768B4L)).setComment(
        "Extracts (CAN 3B7 byte 2 >> 2) & 3. Application caller and brake-graphic predicate unresolved.");
    getFunctionAt(toAddr(0x7AA30L)).setComment(
        "Application SID27 03/04 response: ten nibble-substitution/bit-permutation rounds, then final XOR. Not AES.");
  }

  private void signature(long address, DataType result, String[] names, DataType... types)
      throws Exception {
    if (names.length != types.length) throw new IllegalStateException("signature arity drift");
    Function function = ensure(address, null);
    Variable[] params = new Variable[types.length];
    for (int i = 0; i < types.length; i++)
      params[i] = new ParameterImpl(names[i], types[i], currentProgram);
    function.updateFunction(Function.DEFAULT_CALLING_CONVENTION_STRING,
        new ReturnParameterImpl(result, currentProgram),
        Function.FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
        SourceType.USER_DEFINED, params);
    function.setNoReturn(false);
  }

  private void signatures() throws Exception {
    DataType p = pointer(), b = ByteDataType.dataType, u = UnsignedIntegerDataType.dataType;
    for (long a : new long[] {0xFEDD04C4L, 0xFEDC592CL, 0xFEDD0D66L, 0xFEDC58F2L})
      signature(a, u, new String[] {"key", "key_length", "context"}, p,b,p);
    for (long a : new long[] {0xFEDD0196L,0xFEDD02B4L,0xFEDC5946L,0xFEDC5954L,
        0xFEDD0ECCL,0xFEDC7AF0L,0xFEDD0910L})
      signature(a, u, new String[] {"input", "output", "length", "context"}, p,p,b,p);
    for (long a : new long[] {0xFEDD1020L,0xFEDC7AC0L,0xFEDD0A68L})
      signature(a, u, new String[] {"key", "key_length", "iv", "iv_length", "context"}, p,b,p,b,p);
    for (long a : new long[] {0xFEDD0BBEL,0xFEDC5918L})
      signature(a, u, new String[] {"input", "tag", "length", "final_block", "context"}, p,p,b,u,p);
    for (long a : new long[] {0xFEDD0B1EL,0xFEDC590CL})
      signature(a, u, new String[] {"context"}, p);
    signature(0xFEDD03D8L, VoidDataType.dataType, new String[] {"key", "round_keys"}, p,p);
    signature(0x7AA30L, VoidDataType.dataType, new String[] {"seed", "response"}, p,p);
    signature(0x7A9B8L, VoidDataType.dataType, new String[] {"entropy", "seed"}, u,p);
    signature(0x7A98CL, u, new String[0]);
    signature(0x7982CL, VoidDataType.dataType, new String[] {"destination", "value", "length"}, p,b,u);
    signature(0x797DAL, VoidDataType.dataType, new String[] {"destination", "source", "length"}, p,p,u);
  }

  private void repairReturningFill() throws Exception {
    Function fill = ensure(0x7982CL, "r4p_byte_fill");
    fill.setNoReturn(false);
    fill.setBody(new AddressSet(toAddr(0x7982CL), toAddr(0x7983DL)));
    List<Instruction> calls = new ArrayList<>();
    ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(fill.getEntryPoint());
    while (refs.hasNext()) {
      Reference ref = refs.next();
      if (!ref.getReferenceType().isCall()) continue;
      Instruction call = getInstructionAt(ref.getFromAddress());
      if (call != null) calls.add(call);
    }
    Set<Function> callers = new HashSet<>();
    for (Instruction call : calls) {
      Function caller = getFunctionContaining(call.getAddress());
      if (caller != null) callers.add(caller);
      call.setFlowOverride(FlowOverride.NONE);
      Address next = call.getAddress().add(call.getLength());
      call.setFallThrough(next);
      if (getInstructionAt(next) == null && !disassemble(next))
        throw new IllegalStateException("fill continuation disassembly failed " + next);
    }
    for (Function caller : callers) CreateFunctionCmd.fixupFunctionBody(currentProgram, caller, monitor);
    // Exact retained disassembly bounds prevent a late noReturn pass from
    // stranding the crucial DID callbacks or the application's permutation rounds.
    long[][] bounds = {{0x2881c,0x28867},{0x28868,0x288a9},{0x2d380,0x2d3d5},
        {0x2db32,0x2db87},{0x7aa30,0x7ab09},{0x2389a,0x23929}};
    for (long[] bound : bounds) {
      Function function = ensure(bound[0], null);
      Address start = toAddr(bound[0]), end = toAddr(bound[1]);
      // An analyzer may have made an orphan continuation into a default function.
      List<Address> fragments = new ArrayList<>();
      FunctionIterator it = currentProgram.getFunctionManager().getFunctions(new AddressSet(start,end), true);
      while (it.hasNext()) {
        Function other = it.next();
        if (other.equals(function)) continue;
        if (other.getSymbol().getSource() != SourceType.DEFAULT)
          throw new IllegalStateException("named function inside verified meter body " + other.getEntryPoint());
        fragments.add(other.getEntryPoint());
      }
      for (Address fragment : fragments) currentProgram.getFunctionManager().removeFunction(fragment);
      disassemble(start);
      function.setNoReturn(false);
      function.setBody(new AddressSet(start,end));
    }
  }

  @Override public void run() throws Exception {
    if (!"v850e3:LE:32:default".equals(currentProgram.getLanguageID().getIdAsString()))
      throw new IllegalStateException("meter requires v850e3, not the broad SIMD profile");
    pinTables();
    keyData();
    namedFunctions();
    signatures();
    repairReturningFill();
    println("SeedR4pMeterDiagnostics: pinned DID/SecurityAccess tables, key consumers and receive/display paths");
  }
}
