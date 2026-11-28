#include "windowgraph-abi.h"

/* Export the source identity checked by the Java loader. */
int WINDOWGRAPH_ABI(void) { return 0; }

typedef int (*guest)(struct ctx*, uint64_t*, uint8_t*, uint8_t*);

/* The location field is followed by the flow and stop bits in op[2]. */
enum { LOC_SHIFT = 40, LOC_MASK = (1u << 22) - 1, LOC_FLOW = 1u << 22 };

int window_run(int loc, int start, int limit, uint64_t *code, int32_t *index, uint64_t *ctl,
        uint64_t *written, const _Atomic int *machine, const _Atomic int *thread,
        uint8_t *registers, uint8_t *unique, uint8_t *memory,
        uint64_t *executed_bits, uint32_t *exec_dirty,
        uint64_t *bus_log, uint64_t *trace_log) {
    if (start < 0 || limit < start || limit > MAX_RETIRED ||
        ctl[CTL_READS] > ctl[CTL_COUNT] || ctl[CTL_COUNT] > MAX_WINDOWS) return -1;
    /* Java keeps the origin fixed across refills; shift both bounds so the
       retirement index directly addresses the shared ring. */
    int recent_start = (int)ctl[CTL_RECENT_START];
    start += recent_start;
    limit += recent_start;
    struct ctx s = {.words = ctl, .memory = memory, .code = code, .index = index,
        .machine_stop = machine, .thread_stop = thread, .written = written,
        .retire_flags = (unsigned)ctl[CTL_RETIRE_FLAGS], .bus_log = bus_log};
    if (memory) {
        uint64_t valid = ctl[CTL_CACHE_VALID];
        if (valid & 1) {
            uint64_t ri = ctl[CTL_CACHE_RINFO];
            s.cache_low[0] = ctl[CTL_CACHE_RLO];
            s.cache_high[0] = ctl[CTL_CACHE_RHI];
            s.cache_r_off = ctl[CTL_CACHE_ROFF];
            s.cache_window[0] = (unsigned)(ri & 255);
            s.cache_stack[0] = (unsigned)(ri & STACK_RAM);
            s.r = memory + s.cache_r_off;
            s.cache_r_valid = 1;
        }
        if (valid & 2) {
            uint64_t wi = ctl[CTL_CACHE_WINFO];
            s.cache_low[1] = ctl[CTL_CACHE_WLO];
            s.cache_high[1] = ctl[CTL_CACHE_WHI];
            s.cache_w_off = ctl[CTL_CACHE_WOFF];
            s.cache_m_off = ctl[CTL_CACHE_MOFF];
            s.cache_window[1] = (unsigned)(wi & 255);
            s.cache_stack[1] = (unsigned)(wi & STACK_RAM);
            s.w = memory + s.cache_w_off;
            s.m = (wi & 512) ? memory + s.cache_m_off : NULL;
            s.cache_w_valid = 1;
        }
    }
    ctl[CTL_PARTIAL_OP] = 0;
    ctl[CTL_STORED] = ctl[CTL_WRITE_LOST] = ctl[CTL_ALIASES] = 0;
    ctl[CTL_SYNC] = ctl[CTL_SYNC + 1] = ctl[CTL_SYNC + 2] = 0;
    ctl[CTL_WRITE_COUNT] = 0;
    ctl[CTL_BUS_LOG_COUNT] = ctl[CTL_TRACE_LOG_COUNT] = ctl[CTL_EXEC_DIRTY_COUNT] = 0;
    const uint64_t total = ctl[CTL_INDEX];
    const uint64_t low0 = ctl[CTL_FETCH_LO], high0 = ctl[CTL_FETCH_HI];
    const uint64_t low1 = ctl[CTL_FETCH_LO1], high1 = ctl[CTL_FETCH_HI1];
    /* A single unsigned range check admits ordinary locations inside fetch window 0
       and excludes the stop bit (bit 63 of info). Near grant ends or in window 1,
       check both grants with the exact instruction width. */
    const uint64_t span0 = high0 > low0 && high0 - low0 >= UINT8_MAX ? high0 - low0 - UINT8_MAX : 0;
    const int log_bus_active = (s.retire_flags & (LOG_READ | LOG_WRITE)) != 0;
    const int log_trace_active = (s.retire_flags & LOG_TRACE) != 0;
    const int check_buf = ((s.retire_flags & (MARK_WRITE | LOG_READ | LOG_WRITE | LOG_TRACE)) != 0)
        || executed_bits != NULL;
    uint32_t trace_count = 0, exec_dirty_count = 0;
    uint64_t last_info = 0;
    unsigned last_edge = 0;
    int i = start;
    unsigned reason = EXIT_BUDGET;
    if (loc < 0 || (uint64_t)loc >= total) return -2;
    if (i == limit) goto done;
    if (__builtin_expect(suspended(&s), 0)) { reason = EXIT_SUSPEND; goto done; }
    int32_t pos = index[loc];
    uint64_t *op;
resolve:
    if (pos <= 0) {
        ctl[CTL_NEXT_LOC] = (uint64_t)(unsigned)loc;
        reason = suspended(&s) ? EXIT_SUSPEND : pos < 0 ? EXIT_STOP : EXIT_UNBOUND;
        goto done;
    }
    if (__builtin_expect(suspended(&s), 0)) { reason = EXIT_SUSPEND; goto done; }
    op = code + pos;
    for (;;) {
        if (__builtin_expect(((i & 63) == 0) && suspended(&s), 0)) { reason = EXIT_SUSPEND; break; }
        const uint64_t fn = op[0], info = op[2];
        const unsigned key = (unsigned)(info >> LOC_SHIFT) & ~LOC_FLOW;
        if (!fn) {
            loc = (int)(key & LOC_MASK);
            pos = index[loc];
            if (pos > 0 && code + pos == op) return -4;
            goto resolve;
        }
        const uint64_t pc = op[3] >> 32;
        if (__builtin_expect(((pc - low0) | (info & (UINT64_C(1) << 63))) >= span0, 0)) {
            if (info >> 63) { reason = EXIT_STOP; break; }
            const uint64_t w = (uint8_t)(info >> 32);
            const int ok0 = pc >= low0 && pc <= high0 && w <= high0 - pc;
            const int ok1 = high1 > low1 && pc >= low1 && pc <= high1 && w <= high1 - pc;
            if (!ok0 && !ok1) {
                ctl[CTL_NEXT_LOC] = key & LOC_MASK;
                reason = EXIT_FETCH;
                break;
            }
        }
        const uint32_t blk_k = (uint32_t)(info >> 24) & 0xFFu;
        if (blk_k) {
            const uint64_t hdr = op[HEADER];
            const int32_t fallback = (int32_t)(uint32_t)hdr;
            if (log_trace_active || (uint32_t)(limit - i) < blk_k) {
                op = code + fallback;
                continue;
            }
            const uint64_t *meta = op + HEADER + 1;
            if (__builtin_expect(check_buf && (
                    ctl[CTL_WRITE_COUNT] >= MAX_WRITE_MISSES - 32 ||
                    s.bus_log_count >= MAX_BUS_LOG - 32 ||
                    exec_dirty_count > MAX_EXEC_DIRTY - blk_k), 0)) {
                ctl[CTL_NEXT_LOC] = key & LOC_MASK;
                reason = EXIT_FLUSH;
                break;
            }
            s.cur_pc = pc;
            s.cur_inst = (uint32_t)(i - start);
            s.block_budget = (uint32_t)(limit - i);
            s.block_retired = 0;
            s.block_exit_idx = 0;
            const int edge = ((guest)(uintptr_t)fn)(&s, op + HEADER + 2 + blk_k, registers, unique);
            const uint32_t ret = s.block_retired;
            if (ret > 0) {
                if (executed_bits) {
                    uint32_t cover = ret >= blk_k ? blk_k : ret;
                    for (uint32_t u = 0; u < cover; u++) {
                        unsigned loc_id = (unsigned)(meta[u] >> LOC_SHIFT) & LOC_MASK;
                        uint64_t *ew = executed_bits + (loc_id >> 6);
                        uint64_t eb = UINT64_C(1) << (loc_id & 63);
                        if (__builtin_expect(!(*ew & eb), 0)) {
                            *ew |= eb;
                            exec_dirty[exec_dirty_count++] = loc_id;
                        }
                    }
                }
                uint32_t tail_n = ret < RECENT_COUNT ? ret : RECENT_COUNT;
                uint32_t skip = ret - tail_n;
                int ri = i + (int)skip;
                uint32_t idx = skip % blk_k;
                for (uint32_t u = 0; u < tail_n; u++) {
                    ctl[CTL_RECENT + (ri++ & (RECENT_COUNT - 1))] = pc + ((meta[idx] >> 24) & 0xFFu);
                    if (++idx == blk_k) idx = 0;
                }
                i += (int)ret;
            }
            if (edge == GUEST_BLOCK_FLUSH) {
                if (ret > 0) {
                    last_info = meta[blk_k - 1] & 0xFFFFFFu;
                    last_edge = (unsigned)((hdr >> 32) & 3u);
                }
                ctl[CTL_NEXT_LOC] = key & LOC_MASK;
                reason = EXIT_FLUSH;
                break;
            }
            if (edge == GUEST_BLOCK_YIELD) {
                if (ret > 0) {
                    last_info = meta[blk_k - 1] & 0xFFFFFFu;
                    last_edge = (unsigned)((hdr >> 32) & 3u);
                }
                if (i == limit) { reason = EXIT_BUDGET; break; }
                if (suspended(&s)) { reason = EXIT_SUSPEND; break; }
                if ((uint32_t)(limit - i) < blk_k) {
                    op = code + fallback;
                    continue;
                }
                ctl[CTL_NEXT_LOC] = key & LOC_MASK;
                reason = EXIT_FLUSH;
                break;
            }
            if (edge < 0) {
                const uint32_t m = s.block_exit_idx;
                if (ret > 0) {
                    if (m > 0) {
                        last_info = meta[m - 1] & 0xFFFFFFu;
                        last_edge = 0;
                    } else {
                        last_info = meta[blk_k - 1] & 0xFFFFFFu;
                        last_edge = (unsigned)((hdr >> 32) & 3u);
                    }
                }
                if (edge == GUEST_BUS_MISS) {
                    unsigned loc_m = (unsigned)(meta[m] >> LOC_SHIFT) & LOC_MASK;
                    ctl[CTL_MISS_ADDRESS] = s.miss_address;
                    ctl[CTL_MISS_TRANSFER] = ((uint64_t)loc_m << 8) | s.miss_transfer;
                    reason = EXIT_BUS;
                } else if (edge == -1) {
                    reason = EXIT_INDIRECT;
                } else {
                    return -6;
                }
                break;
            }
            last_info = meta[blk_k - 1] & 0xFFFFFFu;
            if ((unsigned)edge > 1) {
                loc = edge - GUEST_DYNAMIC;
                pos = index[loc];
                last_edge = (uint32_t)(code[(pos & INT32_MAX) + 2] & 0xFFFFFFu) + GUEST_DYNAMIC;
                if (i == limit) break;
                goto resolve;
            }
            last_edge = (unsigned)edge;
            if (i == limit) break;
            const unsigned shift = 32u * (unsigned)edge;
            const uint64_t links = op[1];
            const int32_t link = (int32_t)(links >> shift);
            if (link < -1) { op = code + ~link; continue; }
            if (link == -1) { reason = suspended(&s) ? EXIT_SUSPEND : EXIT_EDGE; break; }
            loc = link;
            pos = index[loc];
            if (pos > 0) {
                const uint64_t mask = (uint64_t)UINT32_MAX << shift;
                op[1] = (links & ~mask) | ((uint64_t)(uint32_t)~pos << shift);
            }
            goto resolve;
        }
        if (__builtin_expect(check_buf && (
                ctl[CTL_WRITE_COUNT] >= MAX_WRITE_MISSES - MAX_STACK_WORDS ||
                s.bus_log_count >= MAX_BUS_LOG - MAX_STACK_WORDS ||
                trace_count >= MAX_TRACE_LOG ||
                exec_dirty_count >= MAX_EXEC_DIRTY), 0)) {
            ctl[CTL_NEXT_LOC] = key & LOC_MASK;
            reason = EXIT_FLUSH;
            break;
        }
        if (__builtin_expect(log_bus_active, 0)) {
            s.cur_pc = pc;
            s.cur_inst = (uint32_t)(i - start);
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
            if (executed_bits) {
                unsigned loc_id = key & LOC_MASK;
                uint64_t *ew = executed_bits + (loc_id >> 6);
                uint64_t eb = UINT64_C(1) << (loc_id & 63);
                if (__builtin_expect(!(*ew & eb), 0)) {
                    *ew |= eb;
                    exec_dirty[exec_dirty_count++] = loc_id;
                }
            }
            if (__builtin_expect(log_trace_active, 0)) {
                trace_log[trace_count++] = (pc & UINT32_MAX) | ((uint64_t)(uint8_t)(info >> 32) << 32);
            }
            ctl[CTL_RECENT + (i++ & (RECENT_COUNT - 1))] = pc;
            last_info = info;
            if (edge == GUEST_CONTROL) {
                last_edge = 0;
                reason = EXIT_CONTROL;
                break;
            }
            loc = edge - GUEST_DYNAMIC;
            pos = index[loc];
            last_edge = (uint32_t)(code[(pos & INT32_MAX) + 2] & 0xFFFFFFu) + GUEST_DYNAMIC;
            if (i == limit) break;
            goto resolve;
        }

        if (executed_bits) {
            unsigned loc_id = key & LOC_MASK;
            uint64_t *ew = executed_bits + (loc_id >> 6);
            uint64_t eb = UINT64_C(1) << (loc_id & 63);
            if (__builtin_expect(!(*ew & eb), 0)) {
                *ew |= eb;
                exec_dirty[exec_dirty_count++] = loc_id;
            }
        }
        if (__builtin_expect(log_trace_active, 0)) {
            trace_log[trace_count++] = (pc & UINT32_MAX) | ((uint64_t)(uint8_t)(info >> 32) << 32);
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
        loc = link;
        pos = index[loc];
        if (pos > 0) {
            const uint64_t mask = (uint64_t)UINT32_MAX << shift;
            op[1] = (links & ~mask) | ((uint64_t)(uint32_t)~pos << shift);
        }
        goto resolve;
    }
done:
    if (i != start) { ctl[CTL_LAST] = (uint32_t)(last_info & 0xFFFFFFu); ctl[CTL_EDGE] = last_edge; }
    uint64_t valid = 0;
    if (s.cache_r_valid) {
        valid |= 1;
        ctl[CTL_CACHE_RLO] = s.cache_low[0];
        ctl[CTL_CACHE_RHI] = s.cache_high[0];
        ctl[CTL_CACHE_ROFF] = s.cache_r_off;
        ctl[CTL_CACHE_RINFO] = s.cache_window[0] | s.cache_stack[0];
    }
    if (s.cache_w_valid) {
        valid |= 2;
        ctl[CTL_CACHE_WLO] = s.cache_low[1];
        ctl[CTL_CACHE_WHI] = s.cache_high[1];
        ctl[CTL_CACHE_WOFF] = s.cache_w_off;
        ctl[CTL_CACHE_MOFF] = s.cache_m_off;
        ctl[CTL_CACHE_WINFO] = s.cache_window[1] | s.cache_stack[1] | (s.m ? 512ULL : 0ULL);
    }
    ctl[CTL_CACHE_VALID] = valid;
    ctl[CTL_BUS_LOG_COUNT] = s.bus_log_count;
    ctl[CTL_TRACE_LOG_COUNT] = trace_count;
    ctl[CTL_EXEC_DIRTY_COUNT] = exec_dirty_count;
    ctl[CTL_EXIT] = reason;
    return i - start;
}
