// Canonical FACI decisions shared with native execution via generate_p1me_faci.py.
// Inputs: 32-bit unsigned register values widened to long; physical states 0..3;
// region size is the backing cell array's byte size (4..0x80000, multiple of 4).
// Cells are read-only; result arrays have 4 (scan) or 5 (completion) elements.
// Arithmetic stays below 2^33. Shifts, callbacks and object operations are excluded.
public final class P1MEFaci {
    // Result: error (0=success, 1=range, 2=unknown cell), first dirty offset,
    // latency in microseconds, unknown offset. Tables4.5/4.15; Table37.14.
    static void blankCheck(byte[] cells, long start, long end, long size,
                           int decrement, long[] result) {
        long first = start & 0x7fffc;
        long last = end & 0x7fffc;
        long low = first < last ? first : last;
        long high = first > last ? first : last;
        result[0] = 0;
        result[1] = -1;
        result[2] = 0;
        result[3] = 0;
        if ((decrement != 0 ? first < last : first > last)
                || high + 4 > size || high - low + 4 > 0x10000) {
            result[0] = 1;
            return;
        }
        long scanned = 0;
        for (long offset = first;; offset += decrement != 0 ? -4 : 4) {
            int state = cells == null ? 0 : cells[(int)(offset / 4)];
            if (state == 0 || state == 3) {
                result[0] = 2;
                result[3] = offset;
                return;
            }
            scanned += 4;
            if (state == 1) {
                result[1] = offset;
                break;
            }
            if (offset == last) break;
        }
        long remainder = scanned % 64;
        result[2] = (scanned / 64) * 100
            + (remainder == 0 ? 0 : remainder == 4 ? 30 : 100);
    }

    // Result: FSTATR, FASTAT, FBCSTAT write (-1=retain), FPSADDR write
    // (-1=retain), FRDY rising edge. Tables4.15/6.2; sections6.3.8-6.3.15.
    static void complete(long previousStatus, long access, int operation,
                         long firstDirty, long[] result) {
        long status = previousStatus | 0x8000;
        if ((access & 0x88) != 0) {
            status |= 0x4000;
            access |= 0x10;
        }
        result[0] = status;
        result[1] = access;
        result[2] = operation == 0x71 ? (firstDirty < 0 ? 0 : 1) : -1;
        result[3] = operation == 0x71 ? firstDirty : -1;
        result[4] = (previousStatus & 0x8000) == 0 ? 1 : 0;
    }
}
