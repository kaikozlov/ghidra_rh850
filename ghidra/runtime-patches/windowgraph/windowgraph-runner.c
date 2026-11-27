#include "windowgraph-abi.h"

/* Export the source identity checked by the Java loader. */
int WINDOWGRAPH_ABI(void) { return 0; }

typedef int (*guest)(struct ctx*, uint64_t*, uint8_t*, uint8_t*);

/* The location field is followed by the flow and stop bits in op[2]. */
enum { LOC_SHIFT = 40, LOC_MASK = (1u << 22) - 1, LOC_FLOW = 1u << 22 };

int window_run(int loc, int start, int limit, uint64_t *code, int32_t *index, uint64_t *ctl,
        uint64_t *written, const _Atomic int *machine, const _Atomic int *thread,
        uint8_t *registers, uint8_t *unique, uint8_t *memory) {
    if (start < 0 || limit < start || limit > MAX_RETIRED ||
        ctl[CTL_READS] > ctl[CTL_COUNT] || ctl[CTL_COUNT] > MAX_WINDOWS) return -1;
    /* Java keeps the origin fixed across refills; shift both bounds so the
       retirement index directly addresses the shared ring. */
    int recent_start = (int)ctl[CTL_RECENT_START];
    start += recent_start;
    limit += recent_start;
    struct ctx s = {.words = ctl, .memory = memory, .code = code, .index = index,
        .machine_stop = machine, .thread_stop = thread, .written = written,
        .retire_flags = (unsigned)ctl[CTL_RETIRE_FLAGS]};
    ctl[CTL_PARTIAL_OP] = 0;
    ctl[CTL_STORED] = ctl[CTL_WRITE_LOST] = ctl[CTL_ALIASES] = 0;
    ctl[CTL_SYNC] = ctl[CTL_SYNC + 1] = ctl[CTL_SYNC + 2] = 0;
    ctl[CTL_WRITE_COUNT] = 0;
    const uint64_t base = ctl[CTL_BASE], total = ctl[CTL_INDEX];
    const uint64_t low = ctl[CTL_FETCH_LO], high = ctl[CTL_FETCH_HI];
    const uint64_t bank_end = base + 2 * total;
    /* A single unsigned range check admits ordinary locations and excludes
       the stop bit. Near the grant end, check the actual instruction width. */
    const unsigned first = low <= base ? 0 : low >= bank_end ? (unsigned)total :
        (unsigned)((low - base + 1) / 2);
    const unsigned end = high >= bank_end ? (unsigned)total :
        high >= base && high - base >= UINT8_MAX ? (unsigned)((high - base - UINT8_MAX) / 2 + 1) : 0;
    const unsigned grant_count = end > first ? end - first : 0;
    uint64_t last_info = 0;
    unsigned last_edge = 0;
    int i = start;
    unsigned reason = EXIT_BUDGET;
    if (loc < 0 || (uint64_t)loc >= total) return -2;
    if (i == limit) goto done;
    int32_t pos = index[loc];
    uint64_t *op;
resolve:
    if (pos <= 0) {
        reason = suspended(&s) ? EXIT_SUSPEND : pos < 0 ? EXIT_STOP : EXIT_UNBOUND;
        goto done;
    }
    op = code + pos;
    for (;;) {
        if (suspended(&s)) { reason = EXIT_SUSPEND; break; }
        const uint64_t fn = op[0], info = op[2];
        const unsigned key = (unsigned)(info >> LOC_SHIFT) & ~LOC_FLOW;
        if (!fn) {
            pos = index[key & LOC_MASK];
            if (pos > 0 && code + pos == op) return -4;
            goto resolve;
        }
        const uint64_t pc = base + 2 * (uint64_t)key;
        if (key - first >= grant_count) {
            if (info >> 63) { reason = EXIT_STOP; break; }
            if (pc < low || pc > high || (uint8_t)(info >> 32) > high - pc) {
                reason = EXIT_FETCH;
                break;
            }
        }
        const int edge = ((guest)(uintptr_t)fn)(&s, op + HEADER, registers, unique);
        if ((unsigned)edge > 1) {
            if (edge < 0) {
                if (edge == GUEST_BUS_MISS) {
                    ctl[CTL_MISS_ADDRESS] = s.miss_address;
                    ctl[CTL_MISS_TRANSFER] = ((uint64_t)key << 8) | s.miss_transfer;
                    reason = EXIT_BUS;
                } else if (edge == -2) {
                    if (!ctl[CTL_PARTIAL_OP]) return -8;
                    ctl[CTL_PARTIAL_SITE] = (uint32_t)info;
                    reason = EXIT_SUSPEND;
                } else if (edge == -1) reason = EXIT_INDIRECT;
                else return -6;
                break;
            }
            ctl[CTL_RECENT + (i++ & (RECENT_COUNT - 1))] = pc;
            last_info = info;
            if (edge == GUEST_CONTROL) {
                last_edge = 0;
                reason = EXIT_CONTROL;
                break;
            }
            pos = index[edge - GUEST_DYNAMIC];
            last_edge = (uint32_t)code[(pos & INT32_MAX) + 2] + GUEST_DYNAMIC;
            if (i == limit) break;
            goto resolve;
        }

        ctl[CTL_RECENT + (i++ & (RECENT_COUNT - 1))] = pc;
        last_info = info;
        last_edge = (unsigned)edge;
        if (i == limit) break;

        /* A direct link already encodes a positive entry offset. Still
           check its current function, stop state, grant and suspension. */
        const unsigned shift = 32u * (unsigned)edge;
        const uint64_t links = op[1];
        const int32_t link = (int32_t)(links >> shift);
        if (link < -1) {
            op = code + ~link;
            continue;
        }
        if (link == -1) {
            reason = suspended(&s) ? EXIT_SUSPEND : EXIT_EDGE;
            break;
        }
        pos = index[link];
        if (pos > 0) {
            const uint64_t mask = (uint64_t)UINT32_MAX << shift;
            op[1] = (links & ~mask) | ((uint64_t)(uint32_t)~pos << shift);
        }
        goto resolve;
    }
done:
    if (i != start) { ctl[CTL_LAST] = (uint32_t)last_info; ctl[CTL_EDGE] = last_edge; }
    ctl[CTL_EXIT] = reason;
    return i - start;
}
