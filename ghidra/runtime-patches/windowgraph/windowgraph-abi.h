#ifndef P1ME_WINDOWGRAPH_ABI_H
#define P1ME_WINDOWGRAPH_ABI_H

#include <stdint.h>
#include <string.h>
#define IO(N,T) static inline uint64_t rd##N(const uint8_t *p){T x; memcpy(&x,p,sizeof x);return x;} static inline void wr##N(uint8_t *p,uint64_t x){T v=(T)x;memcpy(p,&v,sizeof v);}
IO(1,uint8_t) IO(2,uint16_t) IO(4,uint32_t) IO(8,uint64_t)
/* Sleigh storage widths need not be powers of two (SHL has a 40-bit temporary). */
#define SPLIT_IO(N,L,H) \
    static inline uint64_t rd##N(const uint8_t *p) {return rd##L(p) | (rd##H(p + L) << (8 * L));} \
    static inline void wr##N(uint8_t *p, uint64_t x) {wr##L(p,x); wr##H(p + L,x >> (8 * L));}
SPLIT_IO(3,2,1) SPLIT_IO(5,4,1) SPLIT_IO(6,4,2) SPLIT_IO(7,4,3)
#undef SPLIT_IO
#include <stdatomic.h>
enum { CTL_LAST, CTL_EDGE, CTL_EXIT, CTL_READS, CTL_COUNT, CTL_MODE,
    CTL_FETCH_LO, CTL_FETCH_HI, CTL_INDEX, CTL_BASE, CTL_WINDOWS,
    CTL_PARTIAL_OP = CTL_WINDOWS + 40, CTL_PARTIAL_SITE, CTL_MISS_ADDRESS, CTL_MISS_TRANSFER,
    CTL_RETIRE_FLAGS, CTL_STORED, CTL_WRITE_LOST, CTL_ALIASES, CTL_SYNC,
    CTL_WRITE_COUNT = CTL_SYNC + 3, CTL_RECENT_START, CTL_RECENT };
enum { EXIT_BUDGET, EXIT_BUS, EXIT_INDIRECT, EXIT_SUSPEND, EXIT_EDGE, EXIT_UNBOUND, EXIT_STOP, EXIT_FETCH, EXIT_CONTROL };
enum { GUEST_CONTROL = 2, GUEST_DYNAMIC = 3, GUEST_BUS_MISS = -3 };
enum { HEADER = 4, MAX_WINDOWS = 8, MAX_RETIRED = 256, MAX_STACK_WORDS = 32,
    RECENT_COUNT = 16, CTL_WRITE_MISSES = CTL_RECENT + RECENT_COUNT, STACK_RAM = 256, MISS_STACK = 128, MODE_CHECKED_DESCRIPTORS = 512 };
enum { COUNT_ALIAS = 2, MARK_WRITE = 4, CHECK_WRITE = 8, COUNT_SYNC = 16 };
struct ctx {
    uint64_t *words;
    uint8_t *memory;
    const uint64_t *code;
    const int32_t *index;
    uint8_t *r, *w, *m;
    uint64_t *written;
    unsigned retire_flags;
    uint64_t miss_address;
    unsigned miss_transfer;
    const _Atomic int *machine_stop, *thread_stop;
    uint64_t cache_low[2], cache_high[2];
    unsigned cache_stack[2];
    uint64_t write_key, *write_cell;
};

/* A bank contains one decoder context. A target is usable only when flowing that
   context to its address preserves it. Leave fetch grants, stops, and budgets to the runner. */
static inline int indirect_edge(struct ctx *s, const uint64_t *args, uint64_t target) {
    if (target == args[-1]) return 0;
    uint64_t delta = target - s->words[CTL_BASE];
    if ((delta & 1) || delta / 2 >= s->words[CTL_INDEX]) return -1;
    int loc = (int)(delta / 2);
    int pos = s->index[loc] & INT32_MAX;
    if (!pos || !s->code[pos] || !(s->code[pos + 2] & (UINT64_C(1) << 62))) return -1;
    return GUEST_DYNAMIC + loc;
}

static __attribute__((noinline)) int window_find(struct ctx *s, uint64_t a, int n, int store, int stack) {
    if (a > UINT32_MAX || (a & (n - 1))) goto miss;
    unsigned i = store ? (unsigned)s->words[CTL_READS] : 0;
    unsigned end = (unsigned)s->words[store ? CTL_COUNT : CTL_READS];
    const uint64_t *row = s->words + CTL_WINDOWS + 5 * i;
    for (; i < end; i++, row += 5) {
        if (a < row[0] || a + n > row[1]) continue;
        if (stack && !(row[2] & STACK_RAM)) continue;
        if (!s->memory) goto miss;
        s->cache_low[store] = row[0];
        s->cache_high[store] = row[1];
        s->cache_stack[store] = row[2] & STACK_RAM;
        if (store) {
            s->w = s->memory + row[3];
            s->m = (row[2] & 1) ? s->memory + row[4] : NULL;
        } else s->r = s->memory + row[3];
        return 1;
    }
miss:
    s->miss_address = a;
    s->miss_transfer = (stack ? MISS_STACK : 0) | (n << 1) | store;
    return 0;
}

static inline __attribute__((always_inline)) int window_fits(struct ctx *s, uint64_t a, unsigned n, int store, int stack) {
    if (!(a & (n - 1)) && a >= s->cache_low[store] && a < s->cache_high[store] &&
            a + n <= s->cache_high[store] && (!stack || s->cache_stack[store])) return 1;
    return window_find(s, a, n, store, stack);
}

static inline int fits(struct ctx *s, uint64_t a, int n, int store) {
    return window_fits(s, a, n, store, 0);
}

struct stack_word {
    uint8_t *primary, *mirror;
    uint64_t address;
};

static inline int stack_fit(struct ctx *s, uint64_t addr, int store, struct stack_word *w) {
    if (!window_fits(s, addr, 4, store, 1)) return 0;
    uint64_t offset = addr - s->cache_low[store];
    w->primary = (store ? s->w : s->r) + offset;
    w->mirror = store && s->m ? s->m + offset : NULL;
    if (store) w->address = addr;
    return 1;
}

static inline int stack_mode_ready(struct ctx *s) {
    /* A checked descriptor bank has no undefined slots. Every stack word must
       still fit a live, direction-specific RAM grant before any word commits. */
    uint64_t mode = s->words[CTL_MODE];
    return (mode & MODE_CHECKED_DESCRIPTORS) || !(mode & 1) || !(mode & 0x42);
}

static inline int suspended(const struct ctx *s) {
    return atomic_load_explicit(s->machine_stop, memory_order_acquire) |
        atomic_load_explicit(s->thread_stop, memory_order_acquire);
}

static inline int stack_suspend(struct ctx *s, unsigned next_op) {
    if (!suspended(s)) return 0;
    s->words[CTL_PARTIAL_OP] = next_op;
    return 1;
}

// The native runner is admitted only when there are no bus rows or listeners.
// Only stores to absent ledger words go back to Java, which owns table allocation.
static inline void retire_store(struct ctx *s, uint64_t addr, unsigned width, int mirror) {
    uint64_t *ctl = s->words;
    unsigned flags = s->retire_flags;
    ctl[CTL_STORED] = 1;
    if (mirror && (flags & COUNT_ALIAS)) ++ctl[CTL_ALIASES];
    if (!(flags & (MARK_WRITE | CHECK_WRITE))) return;

    uint64_t key = (addr >> 6) + 1;
    uint64_t *entry = s->write_cell;
    if (s->write_key != key) {
        unsigned table_mask = (unsigned)s->written[0];
        unsigned i = ((key * UINT64_C(0x9e3779b97f4a7c15)) >> 32) & table_mask;
        do {
            entry = s->written + 1 + 2 * i;
            i = (i + 1) & table_mask;
        } while (entry[0] && entry[0] != key);
        s->write_key = key;
        s->write_cell = entry;
    }
    // Native transfers are naturally aligned and 1, 2, 4 or 8 bytes.
    uint64_t bits = ((UINT64_C(1) << width) - 1) << (addr & 63);
    if (flags & MARK_WRITE) {
        if (entry[0]) entry[1] |= bits;
        else ctl[CTL_WRITE_MISSES + ctl[CTL_WRITE_COUNT]++] = addr | ((uint64_t)width << 32);
    } else if ((entry[1] & bits) != bits) {
        ctl[CTL_WRITE_LOST] = 1;
        s->retire_flags &= ~CHECK_WRITE;
    }
}

#endif
