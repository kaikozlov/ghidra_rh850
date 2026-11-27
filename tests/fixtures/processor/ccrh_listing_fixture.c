typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;

u32 ccrh_mix_words(const u16 *src, u32 count, u32 seed)
{
    u32 value = seed;
    while (count != 0) {
        value = (value << 5) ^ (value >> 3) ^ *src++;
        count--;
    }
    return value;
}

u32 ccrh_select(u32 selector, u32 left, u32 right)
{
    if (selector > 3) {
        return 0xffffffffUL;
    }
    if (selector == 0) {
        return left + right;
    }
    if (selector == 1) {
        return left - right;
    }
    if (selector == 2) {
        return left ^ right;
    }
    return (left << 3) | (right >> 5);
}

u32 ccrh_frame_checksum(const u8 *src, u32 count)
{
    volatile u8 local[20];
    u32 index;
    u32 sum = 0;
    for (index = 0; index < 20; index++) {
        local[index] = (index < count) ? src[index] : (u8)index;
        sum += local[index];
    }
    return sum;
}

u32 ccrh_large_frame(u32 value)
{
    volatile u8 local[2048];
    local[0] = (u8)value;
    local[2047] = (u8)(value >> 8);
    return (u32)local[0] + (u32)local[2047];
}
