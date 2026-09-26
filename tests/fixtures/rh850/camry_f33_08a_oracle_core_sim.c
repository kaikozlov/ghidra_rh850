typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

extern u32 oracle_sim_fragment(const u8 *record, u8 *state, u8 *scratch);
extern u32 oracle_sim_freshness(u8 *state, u8 *scratch, u32 trip, u32 reset);
extern u32 oracle_sim_response(u8 *state, u8 *scratch, u32 seq, const u8 *result);

volatile u32 oracle_sim_failure;
volatile u32 oracle_sim_passes;
volatile u32 oracle_sim_result;

static u8 state[0x24];
static u8 scratch[0x68];
static u8 record[20];
static u8 result_args[8];

static void clear_bytes(u8 *p, u32 n) {
  u32 i;
  for (i = 0; i < n; ++i) p[i] = 0;
}

static u32 load32(const u8 *p) {
  return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static u16 load16(const u8 *p) {
  return (u16)((u16)p[0] | ((u16)p[1] << 8));
}

static void store32(u8 *p, u32 v) {
  p[0] = (u8)v; p[1] = (u8)(v >> 8); p[2] = (u8)(v >> 16); p[3] = (u8)(v >> 24);
}

static void make_fragment(u8 tag, u8 base) {
  u32 i;
  clear_bytes(record, sizeof(record));
  record[12] = tag;
  for (i = 0; i < 7; ++i) record[13 + i] = (u8)(base + i);
}

static int bytes_equal(const u8 *a, const u8 *b, u32 n) {
  u32 i;
  for (i = 0; i < n; ++i) {
    if (a[i] != b[i]) return 0;
  }
  return 1;
}

#define CHECK(code, expr) do {   if (!(expr)) { oracle_sim_failure = (code); return; }   oracle_sim_passes++; } while (0)

void oracle_core_sim_main(void) {
  static const u8 app_expected[28] = {
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,
    14,15,16,17,18,19,20,21,22,23,24,25,26,27
  };
  static const u8 response_success[8] = {0xc9,0x07,0x00,0xf8,0xbd,0x64,0xe2,0xa5};
  static const u8 response_error[8] = {0xc9,0x42,0x01,0xbd,0,0,0,0};
  static const u8 response_busy[8] = {0xc9,0x55,0x02,0xaa,0,0,0,0};

  oracle_sim_failure = 0;
  oracle_sim_passes = 0;
  oracle_sim_result = 0;
  clear_bytes(state, sizeof(state));
  clear_bytes(scratch, sizeof(scratch));

  make_fragment(0x87, 0);
  CHECK(1, oracle_sim_fragment(record, state, scratch) == 0);
  CHECK(2, state[6] == 0x07 && state[7] == 1);
  CHECK(3, scratch[16] == 0x00 && scratch[17] == 0x8a &&
           bytes_equal(&scratch[18], &app_expected[0], 7));

  make_fragment(0x9a, 7);
  CHECK(4, oracle_sim_fragment(record, state, scratch) == 0);
  CHECK(5, state[6] == 0xa7 && state[7] == 2 &&
           bytes_equal(&scratch[25], &app_expected[7], 7));

  make_fragment(0xa7, 14);
  CHECK(6, oracle_sim_fragment(record, state, scratch) == 0);
  CHECK(7, state[7] == 3 && bytes_equal(&scratch[32], &app_expected[14], 7));

  make_fragment(0xba, 21);
  CHECK(8, oracle_sim_fragment(record, state, scratch) == 1);
  CHECK(9, state[6] == 0xa7 &&
           bytes_equal(&scratch[18], app_expected, sizeof(app_expected)));

  clear_bytes(state, sizeof(state));
  make_fragment(0x83, 0);
  CHECK(10, oracle_sim_fragment(record, state, scratch) == 0);
  make_fragment(0x94, 7);
  CHECK(11, oracle_sim_fragment(record, state, scratch) == 0);
  make_fragment(0xa2, 14);
  CHECK(12, oracle_sim_fragment(record, state, scratch) == 2 && state[7] == 0);

  clear_bytes(state, sizeof(state));
  clear_bytes(scratch, sizeof(scratch));
  CHECK(13, oracle_sim_freshness(state, scratch, 0x1234, 0x00034567) == 1);
  CHECK(14, load32(&state[24]) == 0x00034567 && load16(&state[28]) == 0x1234 &&
            state[30] == 1 && state[31] == 1 && state[34] == 0x07);
  CHECK(15, load32(&scratch[0]) == 0x1234 && load32(&scratch[4]) == 0x00034567 &&
            load16(&scratch[8]) == 1 && scratch[10] == 3 && scratch[11] == 0x2e &&
            load32(&scratch[100]) == 0x2e);

  CHECK(16, oracle_sim_freshness(state, scratch, 0x1234, 0x00034567) == 2);
  CHECK(17, state[30] == 2 && state[34] == 0x0b);
  state[30] = 0xff;
  CHECK(18, oracle_sim_freshness(state, scratch, 0x1234, 0x00034567) == 0);
  CHECK(19, state[30] == 0 && state[34] == 0x03);
  CHECK(20, oracle_sim_freshness(state, scratch, 0x1235, 0x00034567) == 1);
  CHECK(21, state[30] == 1 && load16(&state[28]) == 0x1235);
  CHECK(22, oracle_sim_freshness(state, scratch, 0x1235, 0x00034568) == 1);
  CHECK(23, state[30] == 1 && state[34] == 0x04);

  clear_bytes(state, sizeof(state));
  clear_bytes(scratch, sizeof(scratch));
  store32(&state[12], 41);
  state[34] = 0x0b;
  scratch[52] = 0xd6; scratch[53] = 0x4e; scratch[54] = 0x2a; scratch[55] = 0x5e;
  store32(result_args, 0);
  result_args[4] = 1;
  result_args[5] = 0;
  result_args[6] = 16;
  CHECK(24, oracle_sim_response(state, scratch, 0x07, result_args) == 0);
  CHECK(25, load32(&state[12]) == 42);
  CHECK(26, bytes_equal(&scratch[80], response_success, sizeof(response_success)));

  clear_bytes(scratch, sizeof(scratch));
  store32(result_args, 0);
  result_args[4] = 0;
  result_args[5] = 0;
  result_args[6] = 16;
  CHECK(27, oracle_sim_response(state, scratch, 0x42, result_args) == 1);
  CHECK(28, load32(&state[12]) == 42 &&
            bytes_equal(&scratch[80], response_error, sizeof(response_error)));

  clear_bytes(scratch, sizeof(scratch));
  store32(result_args, 2);
  result_args[4] = 1;
  result_args[5] = 0;
  result_args[6] = 16;
  CHECK(29, oracle_sim_response(state, scratch, 0x55, result_args) == 2);
  CHECK(30, load32(&state[12]) == 42 &&
            bytes_equal(&scratch[80], response_busy, sizeof(response_busy)));

  oracle_sim_result = 0x08a0c0de;
}
