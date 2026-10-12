/*
 * RH850 simulator fixture for the production TSS3 request-signer core.
 *
 * The fixture drives the same freestanding C core that the RAM-resident
 * helper links in (tss3_request_signer_core.h). ORACLE_SIM_TEST_COMPACT
 * additionally pulls the optional compact codec into this single build so
 * both codecs are exercised; the production helper selects codecs with
 * ORACLE_COMPACT_CODEC alone. tss3_request_signer_core_sim.S provides only
 * the entry stack and the simulator stop label.
 */
#define ORACLE_SIM_TEST_COMPACT 1
#include "../../../exploit/ram_runtime/request_signer/tss3_request_signer_core.h"

volatile uint32_t oracle_sim_failure;
volatile uint32_t oracle_sim_passes;
volatile uint32_t oracle_sim_result;

static SignerState state;
static SignerScratch scratch;
static uint8_t record[20] __attribute__((aligned(4)));

static void clear_bytes(uint8_t *p, uint32_t n) {
  uint32_t i;
  for (i = 0; i < n; ++i) p[i] = 0;
}

static uint32_t load32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
         ((uint32_t)p[3] << 24);
}

static uint16_t load16(const uint8_t *p) {
  return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static void store32(uint8_t *p, uint32_t v) {
  p[0] = (uint8_t)v;
  p[1] = (uint8_t)(v >> 8);
  p[2] = (uint8_t)(v >> 16);
  p[3] = (uint8_t)(v >> 24);
}

static void make_fragment(uint8_t tag, uint8_t base) {
  uint32_t i;
  clear_bytes(record, sizeof(record));
  record[12] = tag;
  for (i = 0; i < 7; ++i) record[13 + i] = (uint8_t)(base + i);
}

static uint8_t expected_domain[30];

static void make_compact(uint8_t b1, uint8_t b2, uint8_t b3, uint8_t b4,
                         uint8_t b5, uint8_t b6, uint8_t b7) {
  clear_bytes(record, sizeof(record));
  record[12] = 0xc0;
  record[13] = b1;
  record[14] = b2;
  record[15] = b3;
  record[16] = b4;
  record[17] = b5;
  record[18] = b6;
  record[19] = b7;
}

static void build_compact_domain(uint8_t b1, uint8_t b2, uint8_t b3, uint8_t b4,
                                 uint8_t b5, uint8_t lat, uint8_t seq) {
  static const uint8_t tmpl[30] = {
      0x00, 0x8a,
      0x00, 0x00, 0x00, 0x08, 0x80, 0x00, 0x2d, 0x47,
      0x00, 0x00, 0x00, 0x00, 0x00,
      0x7f, 0xff, 0x00, 0x7f, 0xff,
      0x00, 0x00, 0xc0, 0x00,
      0x10, 0x00, 0x32, 0x00,
      0x00, 0x00};
  uint32_t i;
  for (i = 0; i < 30; ++i) expected_domain[i] = tmpl[i];
  expected_domain[10] = b1;
  expected_domain[11] = b2;
  expected_domain[12] = b3;
  expected_domain[13] = b1;
  expected_domain[14] = b2;
  expected_domain[20] = b4;
  expected_domain[21] = b5;
  expected_domain[23] = lat;
  expected_domain[26] = (lat == 11) ? 100 : 50;
  expected_domain[28] = seq & 0x3f;
}

static int bytes_equal(const uint8_t *a, const uint8_t *b, uint32_t n) {
  uint32_t i;
  for (i = 0; i < n; ++i) {
    if (a[i] != b[i]) return 0;
  }
  return 1;
}

#define CHECK(code, expr) \
  do {                    \
    if (!(expr)) {        \
      oracle_sim_failure = (code); \
      return;             \
    }                     \
    oracle_sim_passes++;  \
  } while (0)

void oracle_core_sim_main(void) {
  /* Byte views over the typed state/scratch objects keep every checked
     runtime offset visible while the fixture itself stays well-defined. */
  uint8_t *const sb = (uint8_t *)&state;
  uint8_t *const sc = (uint8_t *)&scratch;
  static const uint8_t app_expected[28] = {
      0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
      14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27};
  static const uint8_t response_success[8] = {0xc9, 0x07, 0x00, 0xf8,
                                              0xbd, 0x64, 0xe2, 0xa5};
  static const uint8_t response_error[8] = {0xc9, 0x42, 0x01, 0xbd, 0, 0, 0, 0};
  static const uint8_t response_busy[8] = {0xc9, 0x55, 0x02, 0xaa, 0, 0, 0, 0};

  oracle_sim_failure = 0;
  oracle_sim_passes = 0;
  oracle_sim_result = 0;
  clear_bytes(sb, sizeof(state));
  clear_bytes(sc, sizeof(scratch));

  /* Proven four-frame codec: ordered fragments preserve all 28 bytes. */
  make_fragment(0x87, 0);
  CHECK(101, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_PENDING);
  CHECK(102, sb[6] == 0x07 && sb[7] == 1);
  CHECK(103, sc[16] == 0x00 && sc[17] == 0x8a &&
                 bytes_equal(&sc[18], &app_expected[0], 7));

  make_fragment(0x9a, 7);
  CHECK(104, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_PENDING);
  CHECK(105, sb[6] == 0xa7 && sb[7] == 2 &&
                 bytes_equal(&sc[25], &app_expected[7], 7));

  make_fragment(0xa7, 14);
  CHECK(106, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_PENDING);
  CHECK(107, sb[7] == 3 && bytes_equal(&sc[32], &app_expected[14], 7));

  make_fragment(0xba, 21);
  CHECK(108, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_COMMITTED);
  CHECK(109, sb[6] == 0xa7 &&
                 bytes_equal(&sc[18], app_expected, sizeof(app_expected)));

  /* A mismatched continuation resets assembly without committing. */
  clear_bytes(sb, sizeof(state));
  make_fragment(0x83, 0);
  CHECK(110, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_PENDING);
  make_fragment(0x94, 7);
  CHECK(111, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_PENDING);
  make_fragment(0xa2, 14);
  CHECK(112, oracle_core_assemble_fragment(record + 12, &state, &scratch) ==
                  ORACLE_CORE_REJECTED && sb[7] == 0);

  clear_bytes(sb, sizeof(state));
  clear_bytes(sc, sizeof(scratch));

  /* Canonical inactive shape reconstructs exactly. */
  make_compact(0x12, 0x34, 0x56, 0x9a, 0x78, 0x00, 0xa7);
  build_compact_domain(0x12, 0x34, 0x56, 0x9a, 0x78, 0x00, 0xa7);
  CHECK(1, oracle_core_assemble_compact(record + 12, &state, &scratch) ==
               ORACLE_CORE_COMMITTED && sb[6] == 0xa7);
  CHECK(2, bytes_equal(&sc[16], expected_domain, 30));

  /* Active LTA/LCA shape derives assist gain 100. */
  clear_bytes(sc, sizeof(scratch));
  make_compact(0x00, 0x11, 0x22, 0xbb, 0xcc, 0x0b, 0x3f);
  build_compact_domain(0x00, 0x11, 0x22, 0xbb, 0xcc, 0x0b, 0x3f);
  CHECK(3, oracle_core_assemble_compact(record + 12, &state, &scratch) ==
               ORACLE_CORE_COMMITTED && sb[6] == 0x3f);
  CHECK(4, expected_domain[26] == 100 && expected_domain[23] == 11 &&
               bytes_equal(&sc[16], expected_domain, 30));

  /* Rejected frames leave state and scratch untouched. */
  clear_bytes(sb, sizeof(state));
  clear_bytes(sc, sizeof(scratch));
  sb[6] = 0x5a;
  sb[7] = 0xa5;
  sc[16] = 0x69;
  sc[45] = 0x96;
  make_compact(0, 0, 0, 0, 0, 0x0b, 0x00);
  CHECK(5, oracle_core_assemble_compact(record + 12, &state, &scratch) ==
               ORACLE_CORE_PENDING && sc[16] == 0x69 && sc[45] == 0x96 &&
               sb[6] == 0x5a && sb[7] == 0xa5);
  make_compact(0, 0, 0, 0, 0, 0x05, 0x42);
  CHECK(6, oracle_core_assemble_compact(record + 12, &state, &scratch) ==
               ORACLE_CORE_PENDING && sc[16] == 0x69 && sc[45] == 0x96 &&
               sb[6] == 0x5a && sb[7] == 0xa5);

  clear_bytes(sb, sizeof(state));
  clear_bytes(sc, sizeof(scratch));
  CHECK(7, oracle_core_advance_freshness(&state, &scratch, 0x1234,
                                         0x00034567) == 1);
  CHECK(8, load32(&sb[24]) == 0x00034567 && load16(&sb[28]) == 0x1234 &&
               sb[30] == 1 && sb[31] == 1 && sb[34] == 0x07);
  CHECK(9, load32(&sc[0]) == 0x1234 && load32(&sc[4]) == 0x00034567 &&
               load16(&sc[8]) == 1 && sc[10] == 3 && sc[11] == 0x2e &&
               load32(&sc[100]) == 0x2e);

  CHECK(10, oracle_core_advance_freshness(&state, &scratch, 0x1234,
                                          0x00034567) == 2);
  CHECK(11, sb[30] == 2 && sb[34] == 0x0b);
  sb[30] = 0xff;
  CHECK(12, oracle_core_advance_freshness(&state, &scratch, 0x1234,
                                          0x00034567) == 0);
  CHECK(13, sb[30] == 0 && sb[34] == 0x03);
  CHECK(14, oracle_core_advance_freshness(&state, &scratch, 0x1235,
                                          0x00034567) == 1);
  CHECK(15, sb[30] == 1 && load16(&sb[28]) == 0x1235);
  CHECK(16, oracle_core_advance_freshness(&state, &scratch, 0x1235,
                                          0x00034568) == 1);
  CHECK(17, sb[30] == 1 && sb[34] == 0x04);

  clear_bytes(sb, sizeof(state));
  clear_bytes(sc, sizeof(scratch));
  store32(&sb[12], 41);
  sb[34] = 0x0b;
  sc[52] = 0xd6;
  sc[53] = 0x4e;
  sc[54] = 0x2a;
  sc[55] = 0x5e;
  CHECK(18, oracle_core_pack_response(&state, &scratch, 0x07, 0, 1, 0, 16) == 0);
  CHECK(19, load32(&sb[12]) == 42);
  CHECK(20, bytes_equal(&sc[80], response_success, sizeof(response_success)));

  clear_bytes(sc, sizeof(scratch));
  CHECK(21, oracle_core_pack_response(&state, &scratch, 0x42, 0, 0, 0, 16) == 1);
  CHECK(22, load32(&sb[12]) == 42 &&
               bytes_equal(&sc[80], response_error, sizeof(response_error)));

  clear_bytes(sc, sizeof(scratch));
  CHECK(23, oracle_core_pack_response(&state, &scratch, 0x55, 2, 1, 0, 16) == 2);
  CHECK(24, load32(&sb[12]) == 42 &&
               bytes_equal(&sc[80], response_busy, sizeof(response_busy)));

  oracle_sim_result = 0x08a0c0de;
}
