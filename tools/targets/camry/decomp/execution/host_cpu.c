#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "host_cpu.h"

extern uint32_t camry_sp;

uint32_t camry_R[32];
uint32_t camry_CY, camry_Z, camry_S, camry_OV, camry_SAT;
uint32_t camry_step_limit = 2000000;
uint32_t camry_steps;
extern volatile uint32_t ICCTRL, CDBCR;

uint32_t rr(int reg) {
    return reg ? camry_R[reg] : 0;
}

static void wr(int reg, uint32_t value) {
    if (reg)
        camry_R[reg] = value;
}

static void set_sz_keep_cy(uint32_t value) {
    camry_OV = 0;
    camry_S = value >> 31;
    camry_Z = value == 0;
}

static void flags_add(uint32_t left, uint32_t right) {
    uint64_t wide = (uint64_t)left + right;
    uint32_t result = (uint32_t)wide;
    uint32_t sign_l = left >> 31;
    uint32_t sign_r = right >> 31;
    uint32_t sign_o = result >> 31;
    camry_OV = (sign_l == sign_r) && (sign_r != sign_o);
    camry_CY = (uint32_t)(wide >> 32);
    camry_S = sign_o;
    camry_Z = result == 0;
}

static void flags_sub(uint32_t left, uint32_t right) {
    uint32_t result = left - right;
    uint32_t sign_l = left >> 31;
    uint32_t sign_r = right >> 31;
    uint32_t sign_o = result >> 31;
    camry_OV = (sign_l != sign_r) && (sign_r == sign_o);
    camry_CY = left < right;
    camry_S = sign_o;
    camry_Z = result == 0;
}

int camry_take(int cc) {
    uint32_t z = camry_Z, s = camry_S, ov = camry_OV, cy = camry_CY;
    switch (cc & 0xF) {
    case 0x0: return ov;
    case 0x1: return cy;
    case 0x2: return z;
    case 0x3: return cy || z;
    case 0x4: return s;
    case 0x5: return 1;
    case 0x6: return s ^ ov;
    case 0x7: return (s ^ ov) || z;
    case 0x8: return !ov;
    case 0x9: return !cy;
    case 0xA: return !z;
    case 0xB: return !(cy || z);
    case 0xC: return !s;
    case 0xD: return camry_SAT;
    case 0xE: return !(s ^ ov);
    default: return !((s ^ ov) || z);
    }
}

void camry_step(void) {
    if (++camry_steps > camry_step_limit) {
        fprintf(stderr, "camry lift step limit at r10=%#x\n", camry_R[10]);
        abort();
    }
}

static uint32_t clamp_sat(int64_t value) {
    if (value > 0x7fffffffLL) {
        camry_SAT = 1;
        return 0x7fffffffu;
    }
    if (value < -0x80000000LL) {
        camry_SAT = 1;
        return 0x80000000u;
    }
    if (camry_OV)
        camry_SAT = 1;
    return (uint32_t)value;
}

void camry_mov(int dst, int src) { wr(dst, rr(src)); }
void camry_movi(int dst, uint32_t imm) { wr(dst, imm); }
void camry_movea(int dst, int src, int32_t imm) { wr(dst, rr(src) + (uint32_t)imm); }
void camry_movhi(int dst, int src, int32_t imm) { wr(dst, rr(src) + ((uint32_t)imm << 16)); }
void camry_not(int dst, int src) { uint32_t value = ~rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_or(int dst, int src) { uint32_t value = rr(dst) | rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_xor(int dst, int src) { uint32_t value = rr(dst) ^ rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_and(int dst, int src) { uint32_t value = rr(dst) & rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_tst(int dst, int src) { set_sz_keep_cy(rr(dst) & rr(src)); }
void camry_add(int dst, int src) { uint32_t left = rr(dst), right = rr(src); flags_add(left, right); wr(dst, left + right); }
void camry_sub(int dst, int src) { uint32_t left = rr(dst), right = rr(src); flags_sub(left, right); wr(dst, left - right); }
void camry_subr(int dst, int src) { uint32_t left = rr(src), right = rr(dst); flags_sub(left, right); wr(dst, left - right); }
void camry_cmp(int dst, int src) { flags_sub(rr(dst), rr(src)); }
void camry_addi(int dst, int src, int32_t imm) { uint32_t left = rr(src), right = (uint32_t)imm; flags_add(left, right); wr(dst, left + right); }
void camry_addi_imm5(int dst, int32_t imm) { camry_addi(dst, dst, imm); }
void camry_cmpi(int dst, int32_t imm) { flags_sub(rr(dst), (uint32_t)imm); }
void camry_ori(int dst, int src, uint32_t imm) { uint32_t value = rr(src) | imm; set_sz_keep_cy(value); wr(dst, value); }
void camry_xori(int dst, int src, uint32_t imm) { uint32_t value = rr(src) ^ imm; set_sz_keep_cy(value); wr(dst, value); }
void camry_andi(int dst, int src, uint32_t imm) { uint32_t value = rr(src) & imm; set_sz_keep_cy(value); wr(dst, value); }

static void shift_left(int dst, uint32_t value, uint32_t amount) {
    amount &= 31u;
    uint32_t result = value << amount;
    camry_OV = 0;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = amount == 0 ? 0 : (value >> (32u - amount)) & 1u;
    wr(dst, result);
}

static void shift_right(int dst, uint32_t value, uint32_t amount, int arithmetic) {
    amount &= 31u;
    uint32_t result = amount == 0 ? value : (arithmetic ? (uint32_t)((int32_t)value >> amount) : value >> amount);
    camry_OV = 0;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = amount == 0 ? 0 : (value >> (amount - 1u)) & 1u;
    wr(dst, result);
}

void camry_shl_imm(int dst, uint32_t amount) { shift_left(dst, rr(dst), amount); }
void camry_shr(int dst, uint32_t amount) { shift_right(dst, rr(dst), amount, 0); }
void camry_sar_imm(int dst, uint32_t amount) { shift_right(dst, rr(dst), amount, 1); }
void camry_shl_reg(int dst, int src, int amount) { shift_left(dst, rr(src), rr(amount)); }
void camry_shr_reg(int dst, int src, int amount) { shift_right(dst, rr(src), rr(amount), 0); }
void camry_sar_reg(int dst, int src, int amount) { shift_right(dst, rr(src), rr(amount), 1); }
void camry_zxb(int reg) { wr(reg, rr(reg) & 0xffu); }
void camry_zxh(int reg) { wr(reg, rr(reg) & 0xffffu); }
void camry_sxb(int reg) { wr(reg, (uint32_t)(int32_t)(int8_t)rr(reg)); }
void camry_sxh(int reg) { wr(reg, (uint32_t)(int32_t)(int16_t)rr(reg)); }
void camry_setf(int dst, int cc) { wr(dst, camry_take(cc) ? 1u : 0u); }
void camry_sasf(int dst, int cc) { wr(dst, (rr(dst) << 1) | (camry_take(cc) ? 1u : 0u)); }
void camry_cmovi(int dst, int fallback, int32_t imm, int cc) { wr(dst, camry_take(cc) ? (uint32_t)imm : rr(fallback)); }
void camry_cmov(int dst, int fallback, int taken, int cc) { wr(dst, camry_take(cc) ? rr(taken) : rr(fallback)); }

void camry_sbf(int dst, int src, int other, int cc) {
    uint32_t lsb = camry_take(cc) ? 1u : 0u;
    uint32_t left = rr(other);
    uint32_t right = rr(src);
    uint32_t result = left - right - lsb;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_OV = ((right >> 31) != (left >> 31)) && ((left >> 31) != (result >> 31));
    camry_CY = (uint64_t)left < (uint64_t)right + lsb;
    wr(dst, result);
}

void camry_adf(int dst, int src, int other, int cc) {
    uint32_t lsb = camry_take(cc) ? 1u : 0u;
    uint32_t left = rr(other);
    uint32_t right = rr(src);
    uint64_t wide = (uint64_t)left + right + lsb;
    uint32_t result = (uint32_t)wide;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = wide >> 32 ? 1u : 0u;
    camry_OV = ((right >> 31) == (left >> 31)) && ((left >> 31) != (result >> 31));
    wr(dst, result);
}

static uint32_t addr_of(int base, int32_t disp) { return rr(base) + (uint32_t)disp; }
void camry_ld8s(int dst, int base, int32_t disp) { wr(dst, (uint32_t)(int32_t)(int8_t)camry_read8(addr_of(base, disp))); }
void camry_ld8u(int dst, int base, int32_t disp) { wr(dst, camry_read8(addr_of(base, disp))); }
void camry_ld16s(int dst, int base, int32_t disp) { wr(dst, (uint32_t)(int32_t)(int16_t)camry_read16(addr_of(base, disp))); }
void camry_ld16u(int dst, int base, int32_t disp) { wr(dst, camry_read16(addr_of(base, disp))); }
void camry_ld32(int dst, int base, int32_t disp) { wr(dst, camry_read32(addr_of(base, disp))); }
void camry_st8(int src, int base, int32_t disp) { camry_write8(addr_of(base, disp), rr(src)); }
void camry_st16(int src, int base, int32_t disp) { camry_write16(addr_of(base, disp), rr(src)); }
void camry_st32(int src, int base, int32_t disp) { camry_write32(addr_of(base, disp), rr(src)); }

static void bit_op(int base, int32_t disp, int bit, int kind) {
    uint32_t address = addr_of(base, disp);
    uint32_t value = camry_read8(address);
    uint32_t mask = 1u << (bit & 7);
    camry_Z = (value & mask) == 0;
    if (kind == 0) camry_write8(address, value | mask);
    else if (kind == 1) camry_write8(address, value ^ mask);
    else if (kind == 2) camry_write8(address, value & ~mask);
}
void camry_set1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 0); }
void camry_not1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 1); }
void camry_clr1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 2); }
void camry_tst1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 3); }
void camry_set1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 0); }
void camry_not1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 1); }
void camry_clr1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 2); }
void camry_tst1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 3); }

void camry_prepare(uint32_t regs, int slots, int mode, uint32_t imm) {
    static const int order[12] = {20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31};
    int index;
    for (index = 0; index < 12; index += 1) {
        if (regs & (1u << order[index])) {
            camry_R[3] -= 4u;
            camry_write32(camry_R[3], rr(order[index]));
        }
    }
    camry_R[3] -= (uint32_t)slots << 2;
    if (mode == 1) camry_R[30] = camry_R[3];
    else if (mode == 2) camry_R[30] = imm;
    else if (mode == 3) camry_R[30] = imm << 16;
    else if (mode == 4) camry_R[30] = imm;
}

void camry_sp_add(uint32_t bytes) { camry_R[3] += bytes; }
void camry_pop(int reg) { wr(reg, camry_read32(camry_R[3])); camry_R[3] += 4u; }

void camry_mul(int lo, int hi, int left_reg, int right_reg, int is_signed) {
    uint32_t left = rr(left_reg);
    uint32_t right = rr(right_reg);
    uint32_t low, high;
    if (is_signed) {
        int64_t product = (int64_t)(int32_t)left * (int64_t)(int32_t)right;
        low = (uint32_t)product;
        high = (uint32_t)((uint64_t)product >> 32);
    } else {
        uint64_t product = (uint64_t)left * right;
        low = (uint32_t)product;
        high = (uint32_t)(product >> 32);
    }
    wr(lo, low);
    wr(hi, high);
}

void camry_muli(int lo, int hi, int32_t imm) {
    int64_t product = (int64_t)(int32_t)rr(lo) * imm;
    uint32_t low = (uint32_t)product;
    uint32_t high = (uint32_t)((uint64_t)product >> 32);
    wr(lo, low);
    wr(hi, high);
}

void camry_mului(int lo, int hi, uint32_t imm) {
    uint64_t product = (uint64_t)rr(lo) * imm;
    uint32_t low = (uint32_t)product;
    uint32_t high = (uint32_t)(product >> 32);
    wr(lo, low);
    wr(hi, high);
}

void camry_mulh(int dst, int src) {
    wr(dst, (uint32_t)((int32_t)(int16_t)rr(src) * (int32_t)(int16_t)rr(dst)));
}
void camry_mulhi(int dst, int src, int32_t imm) { wr(dst, (uint32_t)((int32_t)(int16_t)rr(src) * imm)); }
void camry_mulhi5(int dst, int32_t imm) { wr(dst, (uint32_t)((int32_t)(int16_t)rr(dst) * imm)); }

void camry_div3(int quot, int divisor_reg, int rem, int is_signed, int half) {
    uint32_t dividend = rr(quot);
    uint32_t divisor = rr(divisor_reg);
    if (half) divisor = (uint32_t)(int32_t)(int16_t)divisor;
    if (divisor == 0) { camry_OV = 1; return; }
    if (is_signed && dividend == 0x80000000u && divisor == 0xffffffffu) {
        camry_OV = 1; camry_S = 1; camry_Z = 0;
        wr(quot, 0x80000000u);
        wr(rem, 0);
        return;
    }
    if (is_signed) {
        int32_t q = (int32_t)dividend / (int32_t)divisor;
        int32_t m = (int32_t)dividend % (int32_t)divisor;
        camry_OV = 0; camry_S = (uint32_t)q >> 31; camry_Z = q == 0;
        wr(quot, (uint32_t)q);
        wr(rem, (uint32_t)m);
    } else {
        uint32_t q = dividend / divisor;
        uint32_t m = dividend % divisor;
        camry_OV = 0; camry_S = q >> 31; camry_Z = q == 0;
        wr(quot, q);
        wr(rem, m);
    }
}

void camry_divh2(int dst, int src) {
    uint32_t dividend = rr(dst);
    uint32_t divisor = (uint32_t)(int32_t)(int16_t)rr(src);
    if (divisor == 0) { camry_OV = 1; return; }
    if (dividend == 0x80000000u && divisor == 0xffffffffu) {
        camry_OV = 1; camry_S = 1; camry_Z = 0; wr(dst, 0x80000000u); return;
    }
    int32_t q = (int32_t)dividend / (int32_t)divisor;
    camry_OV = 0; camry_S = (uint32_t)q >> 31; camry_Z = q == 0;
    wr(dst, (uint32_t)q);
}

void camry_satadd(int dst, int src) {
    uint32_t left = rr(src), right = rr(dst);
    flags_add(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left + (int64_t)(int32_t)right));
}
void camry_satsub(int dst, int src) {
    uint32_t left = rr(dst), right = rr(src);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}
void camry_satsubr(int dst, int src) {
    uint32_t left = rr(src), right = rr(dst);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}
void camry_sataddi(int dst, int32_t imm) {
    uint32_t left = rr(dst);
    flags_add(left, (uint32_t)imm);
    wr(dst, clamp_sat((int64_t)(int32_t)left + imm));
}
void camry_satsubi(int dst, int src, int32_t imm) {
    uint32_t left = rr(src);
    flags_sub(left, (uint32_t)imm);
    wr(dst, clamp_sat((int64_t)(int32_t)left - imm));
}
void camry_satadd3(int dst, int left_reg, int right_reg) {
    uint32_t left = rr(left_reg), right = rr(right_reg);
    flags_add(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left + (int64_t)(int32_t)right));
}
void camry_satsub3(int dst, int left_reg, int right_reg) {
    uint32_t left = rr(left_reg), right = rr(right_reg);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}

static void search_bits(int src, int dst, int pattern, int from_left) {
    uint32_t value = rr(src);
    uint32_t count = 0;
    uint32_t cursor = value;
    int found = 0;
    while (count < 32u) {
        uint32_t bit = from_left ? cursor >> 31 : cursor & 1u;
        if (bit == (uint32_t)pattern) { found = 1; break; }
        cursor = from_left ? cursor << 1 : cursor >> 1;
        count += 1u;
    }
    if (found) count += 1u;
    else count = 0;
    camry_OV = 0;
    camry_S = 0;
    camry_Z = count == 0;
    camry_CY = count == 32u;
    wr(dst, count);
}
void camry_sch0r(int src, int dst) { search_bits(src, dst, 0, 0); }
void camry_sch1r(int src, int dst) { search_bits(src, dst, 1, 0); }
void camry_sch0l(int src, int dst) { search_bits(src, dst, 0, 1); }
void camry_sch1l(int src, int dst) { search_bits(src, dst, 1, 1); }
void camry_bins(int dst, int src, int pos, int width) {
    uint32_t mask = (1u << width) - 1u;
    uint32_t result = (rr(dst) & ~(mask << pos)) | ((rr(src) & mask) << pos);
    camry_OV = 0;
    camry_S = result >> 31;
    camry_Z = result == 0;
    wr(dst, result);
}
static uint64_t camry_read_pair(int even) {
    if (even == 0) return (uint64_t)camry_R[1] << 32;
    return ((uint64_t)camry_R[even + 1] << 32) | camry_R[even];
}
static void camry_write_pair(int even, uint64_t value) {
    if (even == 0) { wr(1, (uint32_t)(value >> 32)); return; }
    wr(even, (uint32_t)value);
    wr(even + 1, (uint32_t)(value >> 32));
}
void camry_mac(int src1, int src2, int acc, int dst) {
    int64_t product = (int64_t)(int32_t)rr(src1) * (int64_t)(int32_t)rr(src2);
    camry_write_pair(dst, camry_read_pair(acc) + (uint64_t)product);
}
void camry_macu(int src1, int src2, int acc, int dst) {
    uint64_t product = (uint64_t)rr(src1) * (uint64_t)rr(src2);
    camry_write_pair(dst, camry_read_pair(acc) + product);
}
void camry_bsw(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = ((value & 0xffu) << 24) | ((value & 0xff00u) << 8) | ((value & 0xff0000u) >> 8) | (value >> 24);
    set_sz_keep_cy(result);
    camry_CY = !(value & 0xffu) || !((value >> 8) & 0xffu) || !((value >> 16) & 0xffu) || !(value >> 24);
    wr(dst, result);
}
void camry_bsh(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = ((value & 0xff0000u) << 8) | ((value >> 24) << 16) | ((value & 0xffu) << 8) | ((value >> 8) & 0xffu);
    camry_OV = 0; camry_S = result >> 31; camry_Z = (result & 0xffffu) == 0;
    camry_CY = !(value & 0xffu) || !((value >> 8) & 0xffu);
    wr(dst, result);
}
void camry_hsw(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = (value << 16) | (value >> 16);
    set_sz_keep_cy(result);
    camry_CY = !(value & 0xffffu) || !(value >> 16);
    wr(dst, result);
}
void camry_hsh(int src, int dst) {
    uint32_t value = rr(src);
    camry_OV = 0; camry_S = value >> 31; camry_Z = (value & 0xffffu) == 0; camry_CY = (value & 0xffffu) == 0;
    wr(dst, value);
}

uint32_t pack_psw(void) {
    uint32_t value = camry_psw & ~0x1fu;
    value |= camry_Z | (camry_S << 1) | (camry_OV << 2) | (camry_CY << 3) | (camry_SAT << 4);
    return value;
}

void camry_ldsr(int src, int id, int sel) {
    uint32_t value = rr(src);
    if (sel == 4 && id == 24) {
        ICCTRL = value;
        return;
    }
    if (sel == 13 && id == 24) {
        CDBCR = value;
        return;
    }
    if (sel == 2 && id == 10 && (camry_SR[2][13] & 1u) == 0)
        return;
    if (sel == 2 && id == 11) {
        camry_pmr = value;
        return;
    }
    if (sel == 0 && id == 5) {
        camry_Z = value & 1u;
        camry_S = (value >> 1) & 1u;
        camry_OV = (value >> 2) & 1u;
        camry_CY = (value >> 3) & 1u;
        camry_SAT = (value >> 4) & 1u;
        camry_psw = value;
        return;
    }
    if ((unsigned)sel < 14u && (unsigned)id < 32u)
        camry_SR[sel][id] = value;
}

void camry_stsr(int dst, int id, int sel) {
    uint32_t value = 0;
    if ((unsigned)sel < 14u && (unsigned)id < 32u)
        value = camry_SR[sel][id];
    if (sel == 0 && id == 5)
        value = pack_psw();
    if (sel == 2 && id == 11)
        value = camry_pmr;
    if (sel == 4 && id == 24)
        value = camry_sample_icctrl();
    if (sel == 13 && id == 24)
        value = CDBCR & ~2u;
    wr(dst, value);
}

void camry_pushsp(int low, int high) {
    uint32_t pointer = camry_R[3];
    int reg;
    if (low > high)
        return;
    for (reg = low; reg <= high; reg += 1) {
        pointer -= 4u;
        camry_write32(pointer, rr(reg));
    }
    camry_R[3] = pointer;
}

void camry_popsp(int low, int high) {
    uint32_t pointer = camry_R[3];
    int reg;
    if (low > high)
        return;
    for (reg = high; reg >= low; reg -= 1) {
        if (reg != 3)
            wr(reg, camry_read32(pointer));
        pointer += 4u;
    }
    camry_R[3] = pointer;
}

void apply_psw(uint32_t psw) {
    camry_psw = psw;
    camry_Z = psw & 1u;
    camry_S = (psw >> 1) & 1u;
    camry_OV = (psw >> 2) & 1u;
    camry_CY = (psw >> 3) & 1u;
    camry_SAT = (psw >> 4) & 1u;
}

uint32_t camry_return_target(unsigned mode) {
    uint32_t pc, priority, psw = pack_psw();
    if (mode == 0) {
        apply_psw((psw & ~0x1fu) | (camry_SR[0][17] & 0x1fu));
        return camry_SR[0][16];
    }
    if ((psw & 0x40u) == 0 && (camry_SR[2][13] & 1u) == 0)
        camry_SR[2][10] &= camry_SR[2][10] - 1u;
    pc = camry_SR[0][mode == 2 ? 2 : 0];
    apply_psw(camry_SR[0][mode == 2 ? 3 : 1]);
    camry_SR[2][12] &= ~2u;
    if ((camry_SR[0][11] & 1u) == 0)
        return pc;
    priority = camry_SR[1][7] & 31u;
    if (priority > 16u) priority = 16u;
    if (camry_pmr & (1u << (priority < 16u ? priority : 15u))) {
        camry_SR[2][12] |= 2u;
        return pc;
    }
    if ((camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)
        || (pack_psw() & 0xa0u))
        return pc;
    camry_SR[0][11] = 0;
    camry_SR[0][0] = pc;
    camry_SR[0][1] = pack_psw();
    camry_SR[0][13] = 0x72u;
    apply_psw((pack_psw() & 0xbfffffffu) | 0x60u);
    return (camry_SR[1][(pack_psw() & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;
}

int camry_loop(int reg) {
    uint32_t current = rr(reg);
    flags_add(current, 0xffffffffu);
    uint32_t count = current - 1u;
    wr(reg, count);
    return count != 0;
}

uint32_t camry_switch_target(uint32_t next, int reg) {
    uint32_t slot = next + (rr(reg) << 1);
    int32_t disp = (int16_t)camry_read16(slot);
    return next + ((uint32_t)disp << 1);
}

uint32_t camry_callt_target(uint32_t next, uint32_t imm) {
    uint32_t ctbp = camry_SR[0][20];
    camry_SR[0][16] = next;
    camry_SR[0][17] = pack_psw() & 0x1fu;
    return ctbp + camry_read16(ctbp + (imm << 1));
}
