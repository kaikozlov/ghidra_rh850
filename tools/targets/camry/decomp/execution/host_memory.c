#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <setjmp.h>

#ifndef MAP_ANON
#define MAP_ANON MAP_ANONYMOUS
#endif

/* Host stand-in for the 32-bit address space. Later regions overlay earlier
 * ones, so an oracle image can cover RAM while CodeFlash stays at VA 0.
 */

#define CAMRY_HOST_REGIONS 64

/* A C local is not in a firmware region. camry_host_addr assigns it a
 * firmware address, and camry_host_ptr of that address returns the local.
 */
#define CAMRY_ALIAS_SLOTS 64
#define CAMRY_ALIAS_STRIDE 0x200u
#define CAMRY_ALIAS_BASE 0xFEBD0000u

typedef struct {
    uint32_t base;
    uint32_t size;
    uint8_t *data;
} CamryHostRegion;

typedef struct {
    uintptr_t host;
    uint32_t firmware;
} CamryAlias;

static CamryHostRegion camry_host_regions[CAMRY_HOST_REGIONS];
static int camry_host_region_count;
static CamryAlias camry_aliases[CAMRY_ALIAS_SLOTS];
static int camry_alias_count;
static uint32_t camry_dcra1_words[9];
static int camry_dcra1_seeded;

typedef struct {
    uint32_t address;
    uint32_t size;
    uint32_t widths;
    uint32_t access;
    uint32_t initialized;
    uint8_t data[4];
} CamryHostRegister;

#define CAMRY_MODEL_REGISTERS 512
static CamryHostRegister camry_host_registers[CAMRY_MODEL_REGISTERS];
static uint32_t camry_host_register_count;
static jmp_buf camry_host_fault_return;
static int camry_host_fault_armed;
const char *camry_host_fault_kind;
uint32_t camry_host_fault_address;
uint32_t camry_host_fault_width;
uint32_t camry_host_fault_write;

static void camry_device_fault(const char *kind, uint32_t address,
                               uint32_t width, uint32_t write) {
    camry_host_fault_kind = kind;
    camry_host_fault_address = address;
    camry_host_fault_width = width;
    camry_host_fault_write = write;
    if (camry_host_fault_armed)
        longjmp(camry_host_fault_return, 1);
    fprintf(stderr, "camry device fault %s at %#x width %u write %u\n",
        kind, address, width, write);
    abort();
}

/* Expected-fault roots use only the four register argument slots. Keep the
 * fault boundary in C so the verifier can inspect all pre-fault stores. */
void camry_host_fault_call(void *function, const uintptr_t *args, uint32_t count) {
    camry_host_fault_kind = NULL;
    if (count > 4 || camry_host_fault_armed)
        abort();
    camry_host_fault_armed = 1;
    if (setjmp(camry_host_fault_return) == 0) {
        switch (count) {
        case 0: ((void (*)(void))function)(); break;
        case 1: ((void (*)(uintptr_t))function)(args[0]); break;
        case 2: ((void (*)(uintptr_t, uintptr_t))function)(args[0], args[1]); break;
        case 3: ((void (*)(uintptr_t, uintptr_t, uintptr_t))function)(args[0], args[1], args[2]); break;
        case 4: ((void (*)(uintptr_t, uintptr_t, uintptr_t, uintptr_t))function)(args[0], args[1], args[2], args[3]); break;
        }
    }
    camry_host_fault_armed = 0;
}

void camry_host_add_register(uint32_t address, uint32_t size, uint32_t widths,
                             uint32_t access, uint32_t initialized) {
    if (camry_host_register_count == CAMRY_MODEL_REGISTERS || size > 4)
        abort();
    camry_host_registers[camry_host_register_count++] = (CamryHostRegister){
        address, size, widths, access, initialized, {0},
    };
}

static CamryHostRegister *camry_host_register(uint32_t address, uint32_t width) {
    uint32_t index;
    for (index = 0; index < camry_host_register_count; index += 1) {
        CamryHostRegister *reg = &camry_host_registers[index];
        if (address >= reg->address && address - reg->address < reg->size
            && width <= reg->size - (address - reg->address))
            return reg;
    }
    return NULL;
}

static int camry_register_firmware(uintptr_t raw, uint32_t *out) {
    uint32_t index;
    for (index = 0; index < camry_host_register_count; index += 1) {
        CamryHostRegister *reg = &camry_host_registers[index];
        uintptr_t host = (uintptr_t)reg->data;
        if (raw >= host && raw - host < reg->size) {
            *out = reg->address + (uint32_t)(raw - host);
            return 1;
        }
    }
    return 0;
}

/* camry_host_ptr of an address the scenario never touched. The bytes still
 * hold that address in a register. A later load uses camry_read and faults;
 * forming the pointer does not. An unmapped page after the buffer stops a
 * walk at the allocation boundary. */
#define CAMRY_LAZY_PAGE 0x1000u
#define CAMRY_LAZY_SLOTS 128

typedef struct {
    uint32_t base;
    uint8_t *host;
} CamryLazy;

static CamryLazy camry_lazy_pages[CAMRY_LAZY_SLOTS];
static int camry_lazy_count;

/* Same threshold as execution/model.py PERIPHERAL_POLL_READS. */
#define CAMRY_PERIPHERAL_POLL_READS 4096u
/* Same count as execution/model.py ICCTRL_BUSY_READS. */
#define CAMRY_ICCTRL_BUSY_READS 4u
#define CAMRY_PERIPHERAL_POLL_SLOTS 64

typedef struct {
    uint32_t address;
    uint32_t count;
} CamryPeripheralPoll;

static CamryPeripheralPoll camry_peripheral_poll_initial[CAMRY_PERIPHERAL_POLL_SLOTS];
static CamryPeripheralPoll *camry_peripheral_polls = camry_peripheral_poll_initial;
static int camry_peripheral_poll_capacity = CAMRY_PERIPHERAL_POLL_SLOTS;
static int camry_peripheral_poll_count;
static uint32_t camry_icctrl_busy;
static uint32_t camry_flmd_stage;
static uint32_t camry_flmd_desired;
static uint32_t camry_faci_pending_command;
/* Match the primary machine's existing raw-peripheral scenario mode. */
uint32_t camry_peripheral_file;

typedef struct {
    uint32_t after_instructions;
    uint32_t address;
    uint32_t value;
    uint32_t width;
} CamryNativeInput;

uint32_t camry_native_workflow;
static const CamryNativeInput *camry_native_inputs;
static uint32_t camry_native_input_count;
static uint32_t camry_native_input_index;
static uint32_t camry_native_instructions;

/* Only bus identity and instruction positions enter this clock. Read values
 * are always produced by the linked C and its current device backing. */
typedef struct {
    uint32_t instruction;
    uint32_t address;
    uint32_t width;
    uint32_t write;
} CamryNativeAccess;

static const CamryNativeAccess *camry_native_accesses;
static uint32_t camry_native_access_count;
static uint32_t camry_native_access_index;

void camry_native_set_accesses(const CamryNativeAccess *accesses, uint32_t count) {
    camry_native_accesses = accesses;
    camry_native_access_count = count;
    camry_native_access_index = 0;
}

void camry_native_set_inputs(const CamryNativeInput *inputs, uint32_t count) {
    uint32_t index;
    camry_native_inputs = NULL;
    camry_native_input_count = 0;
    camry_native_input_index = 0;
    camry_native_instructions = 0;
    camry_native_workflow = 0;
    if (inputs == NULL || count == 0)
        return;
    for (index = 0; index < count; index += 1) {
        if (inputs[index].width != 1u && inputs[index].width != 2u
            && inputs[index].width != 4u) {
            fprintf(stderr, "invalid camry native input width %u at index %u\n",
                inputs[index].width, index);
            abort();
        }
        if (index != 0
            && inputs[index].after_instructions < inputs[index - 1].after_instructions) {
            fprintf(stderr, "unordered camry native input at index %u\n", index);
            abort();
        }
    }
    camry_native_inputs = inputs;
    camry_native_input_count = count;
    camry_native_workflow = 1;
}

/* Direct calls of a non-returning function, in entry order. The oracle
 * compares this with the bytes' call sequence up to the bounded stop. */
#define CAMRY_NOTE_CAP 8192u
uint32_t camry_note_count;
uint32_t camry_notes[CAMRY_NOTE_CAP];
uint32_t camry_note_root;
int camry_halt_propagate;
int camry_halted;
uint32_t camry_stop_arm;
uint32_t camry_stop_pc;

int camry_note_call(uint32_t caller, uint32_t address) {
    if (caller == camry_note_root && camry_note_count < CAMRY_NOTE_CAP)
        camry_notes[camry_note_count++] = address;
    return 0;
}


/* The src/retained/ bank also defines these. The weak copies supply the host
 * model when those translation units are not linked. */
__attribute__((weak)) volatile uint32_t ICCTRL;
__attribute__((weak)) volatile uint32_t CDBCR;

static void camry_lazy_reset(void) {
    int index;
    for (index = 0; index < camry_lazy_count; index += 1)
        munmap(camry_lazy_pages[index].host, CAMRY_LAZY_PAGE * 2);
    camry_lazy_count = 0;
}

static void camry_fault(int sig, siginfo_t *info, void *unused) {
    (void)unused;
    fprintf(stderr, "camry fault %d at %p\n", sig, info == NULL ? NULL : info->si_addr);
    fflush(stderr);
    _exit(128 + (sig & 0x7f));
}

__attribute__((constructor)) static void camry_fault_install(void) {
    struct sigaction action;
    memset(&action, 0, sizeof(action));
    action.sa_sigaction = camry_fault;
    action.sa_flags = SA_SIGINFO;
    sigaction(SIGSEGV, &action, NULL);
    sigaction(SIGBUS, &action, NULL);
    sigaction(SIGTRAP, &action, NULL);
    /* The oracle records a halt as the end of the call. The verifier has to
     * stop at the same call, or its replay continues into the caller. */
    camry_halt_propagate = 1;
}

void camry_host_reset(void) {
    memset(camry_dcra1_words, 0, sizeof(camry_dcra1_words));
    camry_dcra1_seeded = 0;
    camry_host_regions[0] = (CamryHostRegion){
        0xffd51000u, sizeof(camry_dcra1_words), (uint8_t *)camry_dcra1_words,
    };
    camry_host_region_count = 1;
    camry_alias_count = 0;
    camry_host_register_count = 0;
    camry_host_fault_kind = NULL;
    camry_lazy_reset();
    camry_peripheral_poll_count = 0;
    camry_icctrl_busy = 0;
    camry_flmd_stage = 0;
    camry_flmd_desired = 0;
    camry_faci_pending_command = 0;
    camry_peripheral_file = 0;
    camry_native_set_inputs(NULL, 0);
    camry_native_set_accesses(NULL, 0);
    camry_note_count = 0;
    camry_note_root = 0;
    camry_halted = 0;
    camry_stop_arm = 0;
    camry_stop_pc = 0;
}

uint32_t camry_sample_icctrl(void) {
    uint32_t value = ICCTRL;
    if ((value & 0x100u) == 0) {
        camry_icctrl_busy = 0;
        return value;
    }
    camry_icctrl_busy += 1;
    if (camry_icctrl_busy != CAMRY_ICCTRL_BUSY_READS)
        return value;
    value &= ~0x100u;
    ICCTRL = value;
    camry_icctrl_busy = 0;
    return value;
}

void camry_host_add(uint32_t base, uint8_t *data, uint32_t size) {
    if (base >= 0xFEDE0000u && base < 0xFEE00000u) {
        if (size > 0xFEE00000u - base) {
            fprintf(stderr, "camry local RAM alias region crosses end at %#x\n", base);
            abort();
        }
        base -= 0x200000u;
    }
    if (camry_host_region_count >= CAMRY_HOST_REGIONS) {
        fprintf(stderr, "camry host region cap at %#x\n", base);
        fflush(stderr);
        abort();
    }
    camry_host_regions[camry_host_region_count].base = base;
    camry_host_regions[camry_host_region_count].size = size;
    camry_host_regions[camry_host_region_count].data = data;
    camry_host_region_count += 1;
}

static uint8_t *camry_alias_locate(uint32_t address, uint32_t width) {
    int index;
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        uint32_t offset;
        if (address < alias->firmware)
            continue;
        offset = address - alias->firmware;
        if (offset < CAMRY_ALIAS_STRIDE && width <= CAMRY_ALIAS_STRIDE - offset)
            return (uint8_t *)alias->host + offset;
    }
    return NULL;
}

static uint8_t *camry_host_find(uint32_t address, uint32_t width) {
    int index;
    if (address >= 0xFEDE0000u && address < 0xFEE00000u) {
        if (width > 0xFEE00000u - address)
            return NULL;
        address -= 0x200000u;
    }
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        uint32_t offset;
        if (address < region->base)
            continue;
        offset = address - region->base;
        if (offset < region->size && width <= region->size - offset)
            return region->data + offset;
    }
    {
        uint8_t *alias = camry_alias_locate(address, width);
        CamryHostRegister *reg;
        if (alias != NULL)
            return alias;
        reg = camry_host_register(address, width);
        return reg != NULL ? reg->data + address - reg->address : NULL;
    }
}

/* instructions specifies the absolute workflow clock. Inputs are external
 * register changes: bypass firmware write hooks and their side effects. */
void camry_native_advance(uint32_t instructions) {
    if (instructions < camry_native_instructions) {
        fprintf(stderr, "camry native clock reversal from %u to %u\n",
            camry_native_instructions, instructions);
        abort();
    }
    camry_native_instructions = instructions;
    if (!camry_native_workflow)
        return;
    while (camry_native_input_index < camry_native_input_count) {
        const CamryNativeInput *input = &camry_native_inputs[camry_native_input_index];
        uint8_t *bytes;
        uint32_t index;
        if (input->after_instructions > instructions)
            break;
        bytes = camry_host_find(input->address, input->width);
        if (bytes == NULL) {
            fprintf(stderr, "unmapped camry native input at %#x width %u\n",
                input->address, input->width);
            abort();
        }
        for (index = 0; index < input->width; index += 1)
            bytes[index] = (uint8_t)(input->value >> (8u * index));
        {
            CamryHostRegister *reg = camry_host_register(input->address, input->width);
            if (reg != NULL)
                reg->initialized |= ((1u << input->width) - 1u) << (input->address - reg->address);
        }
        camry_native_input_index += 1;
    }
}

static void camry_native_access(uint32_t address, uint32_t width, uint32_t write) {
    const CamryNativeAccess *access;
    if (!camry_native_workflow || address < 0xFF000000u)
        return;
    if (camry_native_access_index >= camry_native_access_count) {
        fprintf(stderr, "extra camry native bus access at %#x width %u write %u\n",
            address, width, write);
        abort();
    }
    access = &camry_native_accesses[camry_native_access_index];
    if (access->address != address || access->width != width || access->write != write) {
        fprintf(stderr, "changed camry native bus order at %u: %#x/%u/%u != %#x/%u/%u\n",
            camry_native_access_index, address, width, write,
            access->address, access->width, access->write);
        abort();
    }
    camry_native_advance(access->instruction);
    camry_native_access_index += 1;
}

void camry_native_finish(uint32_t instructions) {
    if (camry_native_access_index != camry_native_access_count) {
        fprintf(stderr, "missing camry native bus accesses: %u of %u\n",
            camry_native_access_index, camry_native_access_count);
        abort();
    }
    camry_native_advance(instructions);
    camry_native_set_inputs(NULL, 0);
    camry_native_set_accesses(NULL, 0);
}

static uint32_t camry_stored_value(uint32_t address, uint32_t width);

static void camry_require_access(uint32_t address, uint32_t width, uint32_t write) {
    CamryHostRegister *reg;
    uint32_t mask;
    extern uint32_t camry_SR[14][32];
    if (camry_peripheral_file)
        return;
    if (camry_host_register_count == 0) {
        if (!write && address >= 0xFF000000u && camry_host_find(address, width) == NULL)
            camry_device_fault("uninitialized-read", address, width, 0);
        return;
    }
    if ((address & (width - 1u)) != 0 && (camry_SR[1][5] & 2u) == 0)
        camry_device_fault(write ? "misaligned-write" : "misaligned-read",
            address, width, write);
    if (address >= 0xFF200000u && address < 0xFF208000u) {
        if (write)
            camry_device_fault("write-prohibited", address, width, 1);
        if (camry_stored_value(0xFFC5B000u, 4) != 0
            || camry_stored_value(0xFFC5B01Cu, 4) != 0)
            camry_device_fault("unsupported-dataflash-ecc-mode", address, width, 0);
        return;
    }
    if (address < 0xFF000000u)
        return;
    reg = camry_host_register(address, width);
    if (reg == NULL)
        camry_device_fault(write ? "unmapped-write" : "unmapped-read", address, width, write);
    if ((reg->widths & (1u << width)) == 0 || (address & (width - 1u)) != 0)
        camry_device_fault("mmio-width", address, width, write);
    if ((reg->access & (write ? 2u : 1u)) == 0)
        camry_device_fault(write ? "write-prohibited" : "read-prohibited", address, width, write);
    if (!write && address == 0xFFD51004u && camry_stored_value(0xFFD51020u, 1) != 0)
        camry_device_fault("unsupported-dcra-mode", 0xFFD51020u, 1, 0);
    mask = ((1u << width) - 1u) << (address - reg->address);
    if (!write && (reg->initialized & mask) != mask)
        camry_device_fault("uninitialized-read", address, width, 0);
}

static uint8_t *camry_lazy_ptr(uint32_t address) {
    uint32_t base = address & ~(CAMRY_LAZY_PAGE - 1u);
    uint32_t offset = address - base;
    int index;
    uint8_t *page;
    for (index = camry_lazy_count - 1; index >= 0; index -= 1) {
        if (camry_lazy_pages[index].base == base)
            return camry_lazy_pages[index].host + offset;
    }
    if (camry_lazy_count >= CAMRY_LAZY_SLOTS)
        return NULL;
    page = mmap(NULL, CAMRY_LAZY_PAGE * 2, PROT_NONE, MAP_PRIVATE | MAP_ANON, -1, 0);
    if (page == MAP_FAILED)
        return NULL;
    if (mprotect(page, CAMRY_LAZY_PAGE, PROT_READ | PROT_WRITE) != 0) {
        munmap(page, CAMRY_LAZY_PAGE * 2);
        return NULL;
    }
    camry_lazy_pages[camry_lazy_count].base = base;
    camry_lazy_pages[camry_lazy_count].host = page;
    camry_lazy_count += 1;
    return page + offset;
}

static int camry_lazy_firmware(uintptr_t raw, uint32_t *out) {
    int index;
    for (index = camry_lazy_count - 1; index >= 0; index -= 1) {
        uintptr_t host = (uintptr_t)camry_lazy_pages[index].host;
        if (raw >= host && raw < host + CAMRY_LAZY_PAGE) {
            *out = camry_lazy_pages[index].base + (uint32_t)(raw - host);
            return 1;
        }
    }
    return 0;
}

/* The byte machine returns the scenario fill for an address it has not been
 * given. A host load returns the same fill word without faulting. A store
 * the scenario did not map is not a checked write. */
extern uint8_t camry_fill;

static uint32_t camry_unmapped_value(uint32_t width) {
    uint32_t value = 0;
    uint32_t index;
    for (index = 0; index < width; index += 1)
        value |= (uint32_t)camry_fill << (8u * index);
    return value;
}

static uint32_t camry_peripheral_poll(uint32_t address, uint32_t value, uint32_t width);

/* Device transitions use mapped backing directly, like the primary model's
 * setMemory/registerValue. They are not additional firmware bus accesses. */
static uint32_t camry_stored_value(uint32_t address, uint32_t width) {
    const uint8_t *bytes = camry_host_find(address, width);
    uint32_t value = 0;
    uint32_t index;
    if (bytes == NULL)
        return camry_unmapped_value(width);
    for (index = 0; index < width; index += 1)
        value |= (uint32_t)bytes[index] << (8u * index);
    return value;
}

static void camry_store_value(uint32_t address, uint32_t value, uint32_t width) {
    uint8_t *bytes = camry_host_find(address, width);
    uint32_t index;
    if (bytes == NULL)
        return;
    for (index = 0; index < width; index += 1)
        bytes[index] = (uint8_t)(value >> (8u * index));
    {
        CamryHostRegister *reg = camry_host_register(address, width);
        if (reg != NULL)
            reg->initialized |= ((1u << width) - 1u) << (address - reg->address);
    }
}

static void camry_faci_command(uint32_t command) {
    uint32_t status = camry_stored_value(0xFFA10080u, 4);
    uint32_t access = camry_stored_value(0xFFA10010u, 1);
    uint32_t history = camry_stored_value(0xFFA100A0u, 2);
    uint32_t control = camry_stored_value(0xFFA10084u, 2) & 0x81u;
    uint32_t next_status;
    uint32_t next_access;
    /* RunP1MEMachine.validateFaciWrite: only these modeled sequences exist. */
    if (command != 0x50u && command != 0x71u && command != 0xD0u && command != 0xB3u)
        camry_device_fault("unsupported-faci-command", 0xFFA20000u, 1, 1);
    if (command == 0xD0u ? camry_faci_pending_command != 0x71u : camry_faci_pending_command != 0)
        camry_device_fault("unsupported-faci-sequence", 0xFFA20000u, 1, 1);
    if (command != 0xB3u && (status & 0x8000u) == 0)
        camry_device_fault("faci-not-ready", 0xFFA20000u, 1, 1);
    if (command == 0x50u || command == 0xB3u) {
        if (control != 1u && control != 0x80u)
            camry_device_fault("unsupported-faci-mode", 0xFFA20000u, 1, 1);
        if (command == 0xB3u && camry_stored_value(0xFFA100F0u, 1) != 0)
            camry_device_fault("unsupported-faci-emulation", 0xFFA20000u, 1, 1);
    } else {
        uint32_t first;
        uint32_t last;
        if ((access & 0x10u) != 0 || control != 0x80u
            || camry_stored_value(0xFFA100D0u, 1) != 0
            || camry_stored_value(0xFFA100F0u, 1) != 0
            || camry_stored_value(0xFFF8A430u, 4) != 1u
            || camry_stored_value(0xFFF82410u, 4) != 1u)
            camry_device_fault("unsupported-faci-mode", 0xFFA20000u, 1, 1);
        if (command == 0x71u) {
            camry_faci_pending_command = command;
            return;
        }
        first = camry_stored_value(0xFFA10030u, 4) & 0x7FFFCu;
        last = camry_stored_value(0xFFA10034u, 4) & 0x7FFFCu;
        if (first > last || last - first + 4u > 0x10000u
            || camry_host_find(0xFF200000u + first, last - first + 4u) == NULL)
            camry_device_fault("unsupported-faci-range", 0xFFA20000u, 1, 1);
    }
    if (command == 0xD0u) {
        camry_store_value(0xFFA100A0u, 0xD071u, 2);
        camry_store_value(0xFFA10080u, status & ~0x8000u, 4);
        /* FRDY, blankness and first-nonblank address are external inputs. */
    } else {
        if (command == 0xB3u) {
            next_status = status & ~(0x3703Cu | 0x8B40u);
            next_access = (access & 0x88u) != 0 ? access : access & ~0x10u;
            if ((status & 0x10014u) != 0)
                next_access &= ~1u;
        } else {
            next_status = status & ~0x3703Cu;
            if ((access & 0x88u) != 0)
                next_status |= 0x4000u;
            next_access = (next_status & 0x27068u) != 0
                ? access | 0x10u : access & ~0x10u;
        }
        camry_store_value(0xFFA100A0u, (command << 8) | ((history >> 8) & 0xFFu), 2);
        camry_store_value(0xFFA10080u, next_status, 4);
        camry_store_value(0xFFA10010u, next_access, 1);
    }
    camry_faci_pending_command = 0;
    return;
}

static uint32_t camry_flash_write(uint32_t address, uint32_t value, uint32_t width) {
    if (camry_peripheral_file)
        return value;
    if (address == 0xFFD51000u || address == 0xFFD51004u || address == 0xFFD51020u) {
        uint32_t mode = address == 0xFFD51020u ? value : camry_stored_value(0xFFD51020u, 1);
        if (mode != 0)
            camry_device_fault("unsupported-dcra-mode", 0xFFD51020u, 1, 1);
        if (address == 0xFFD51004u) {
            camry_dcra1_seeded = 1;
            return value ^ 0xFFFFFFFFu;
        }
        if (address == 0xFFD51000u) {
            uint32_t crc;
            uint32_t bit;
            if (!camry_dcra1_seeded)
                camry_device_fault("uninitialized-dcra-seed", address, width, 1);
            crc = ~camry_stored_value(0xFFD51004u, 4) ^ value;
            for (bit = 0; bit < 32; bit += 1)
                crc = (crc >> 1) ^ ((crc & 1u) != 0 ? 0xEDB88320u : 0);
            camry_store_value(0xFFD51004u, ~crc, 4);
        }
        return value;
    }
    if (address == 0xFFA100F0u
        && (value != 0 || camry_stored_value(address, width) != 0))
        camry_device_fault("unsupported-faci-emulation", address, width, 1);
    if (address == 0xFFC5D000u) {
        if ((value & 0xFFFFu) != 5u)
            camry_device_fault("unsupported-icus-command", address, width, 1);
        camry_store_value(0xFFC5D00Cu, 0, 4);
        camry_store_value(0xFFC5D014u, 0, 4);
    }
    {
        uint32_t base = address & ~3u;
        if (base == 0xFFC5B000u || base == 0xFFC5B01Cu) {
            uint32_t writable = base == 0xFFC5B000u ? 3u : 1u;
            uint32_t previous = camry_stored_value(base, 4);
            uint32_t next = address == base && (value & 0xC000u) == 0x4000u
                ? value & writable : previous & writable;
            camry_store_value(base, next, 4);
            return address == base ? next : 0;
        }
        if (base == 0xFFC5B014u) {
            uint32_t shift = (address - base) * 8u;
            uint32_t mask = (width == 4u ? 0xFFFFFFFFu : (1u << (width * 8u)) - 1u) << shift;
            uint32_t next = ((camry_stored_value(base, 4) & ~mask) | (value << shift)) & 7u;
            camry_store_value(base, next, 4);
            return next >> shift;
        }
    }
    if (address == 0xFFC59810u && width == 1u) {
        if ((value & 0xFu) < 3u)
            camry_device_fault("prohibited-dataflash-read-cycle", address, width, 1);
        return value & 0xFu;
    }
    if (address == 0xFFA20000u && width == 1u) {
        camry_faci_command(value & 0xFFu);
    } else if (address == 0xFFA10084u && width == 2u) {
        uint32_t previous = camry_stored_value(address, 2);
        if ((camry_stored_value(0xFFA10080u, 4) & 0x8000u) == 0)
            return previous;
        value &= 0xFFFFu;
        if ((previous != 0 && previous != 0x80u)
            || ((value >> 8) == 0xAAu && (value & 0xFFu) != 0
                && (value & 0xFFu) != 0x80u)) {
            camry_device_fault("unsupported-faci-mode", address, width, 1);
        }
        return (value >> 8) == 0xAAu && previous == 0 ? value & 0x80u : 0;
    } else if ((address == 0xFFA10030u || address == 0xFFA10034u) && width == 4u) {
        return (camry_stored_value(0xFFA10080u, 4) & 0x8000u) != 0
            ? value & ~3u : camry_stored_value(address, 4);
    } else if ((address == 0xFFF82410u || address == 0xFFF8A430u) && width == 4u) {
        return value & 1u;
    } else if (address == 0xFFC5B008u && (value & 1u) != 0) {
        camry_store_value(0xFFC5B004u, camry_stored_value(0xFFC5B004u, 4) & ~3u, 4);
    }
    return value;
}

uint32_t camry_read8(uint32_t address) {
    camry_native_access(address, 1, 0);
    uint8_t *found = camry_host_find(address, 1);
    camry_require_access(address, 1, 0);
    uint32_t value = found != NULL ? *found : camry_fill;
    return camry_peripheral_poll(address, value, 1);
}

uint32_t camry_read16(uint32_t address) {
    camry_native_access(address, 2, 0);
    const uint8_t *found = camry_host_find(address, 2);
    camry_require_access(address, 2, 0);
    uint32_t value = found != NULL
        ? (uint32_t)found[0] | ((uint32_t)found[1] << 8)
        : camry_unmapped_value(2);
    return camry_peripheral_poll(address, value, 2);
}

uint32_t camry_read32(uint32_t address) {
    camry_native_access(address, 4, 0);
    const uint8_t *found = camry_host_find(address, 4);
    camry_require_access(address, 4, 0);
    uint32_t value = found != NULL
        ? (uint32_t)found[0]
            | ((uint32_t)found[1] << 8)
            | ((uint32_t)found[2] << 16)
            | ((uint32_t)found[3] << 24)
        : camry_unmapped_value(4);
    return camry_peripheral_poll(address, value, 4);
}

void camry_write8(uint32_t address, uint32_t value) {
    camry_native_access(address, 1, 1);
    camry_require_access(address, 1, 1);
    value &= 0xFFu;
    value = camry_flash_write(address, value, 1);
    camry_store_value(address, value, 1);
}

void camry_write16(uint32_t address, uint32_t value) {
    camry_native_access(address, 2, 1);
    camry_require_access(address, 2, 1);
    value &= 0xFFFFu;
    value = camry_flash_write(address, value, 2);
    camry_store_value(address, value, 2);
}

uint8_t *camry_host_ptr(uint32_t address) {
    uint8_t *mapped = camry_host_find(address, 1);
    uint8_t *lazy;
    /* A direct load of a scenario peripheral never reaches camry_readN, so it
     * misses the one-shot that turns the 4096th read into the completed poll.
     * Counting the word here makes that load see the same value as the bytes. */
    if (camry_peripheral_file && !camry_native_workflow
        && mapped != NULL && address >= 0xFF000000u
        && !(address >= 0xFF200000u && address < 0xFF208000u)
        && (address & 3u) == 0u && camry_host_find(address, 4) != NULL)
        (void)camry_read32(address);
    if (mapped != NULL)
        return mapped;
    lazy = camry_lazy_ptr(address);
    if (lazy != NULL)
        return lazy;
    fprintf(stderr, "unmapped camry access at %#x\n", address);
    fflush(stderr);
    abort();
}

void *camry_host_resolve(const void *pointer) {
    uintptr_t raw = (uintptr_t)pointer;
    uint32_t address;
    uint8_t *mapped;
    if (pointer == NULL)
        return NULL;
    /* Darwin host pointers sit above 4GB. A value that fits in a firmware
     * address, or a sign-extended one, is that address when a window holds it. */
    if (raw <= 0xffffffffu)
        address = (uint32_t)raw;
    else if ((raw >> 32) == 0xffffffffu)
        address = (uint32_t)raw;
    else
        return (void *)pointer;
    mapped = camry_host_find(address, 1);
    if (mapped != NULL)
        return mapped;
    return (void *)pointer;
}

int camry_host_firmware(const void *pointer, uint32_t *out) {
    const uint8_t *bytes = pointer;
    uintptr_t raw = (uintptr_t)pointer;
    int index;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        const uint8_t *end = region->data + region->size;
        if (bytes >= region->data && bytes < end) {
            *out = region->base + (uint32_t)(bytes - region->data);
            return 1;
        }
    }
    if (camry_register_firmware(raw, out))
        return 1;
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        if (raw >= alias->host && raw < alias->host + CAMRY_ALIAS_STRIDE) {
            *out = alias->firmware + (uint32_t)(raw - alias->host);
            return 1;
        }
    }
    return camry_lazy_firmware(raw, out);
}

uint32_t camry_host_addr(const void *pointer) {
    const uint8_t *bytes = pointer;
    uintptr_t raw = (uintptr_t)pointer;
    int index;
    if (pointer == NULL)
        return 0;
    if (raw <= 0xffffffffu || (raw >> 32) == 0xffffffffu)
        return (uint32_t)raw;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        const uint8_t *end = region->data + region->size;
        if (bytes >= region->data && bytes < end)
            return region->base + (uint32_t)(bytes - region->data);
    }
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        if (raw >= alias->host && raw < alias->host + CAMRY_ALIAS_STRIDE)
            return alias->firmware + (uint32_t)(raw - alias->host);
    }
    {
        uint32_t firmware;
        if (camry_register_firmware(raw, &firmware))
            return firmware;
        if (camry_lazy_firmware(raw, &firmware))
            return firmware;
    }
    {
        uint32_t firmware;
        /* Declared in camry.h. A code pointer is not a firmware region. */
        extern int camry_code_address(const void *pointer, uint32_t *address);
        if (camry_code_address(pointer, &firmware))
            return firmware;
    }
    if (camry_alias_count >= CAMRY_ALIAS_SLOTS) {
        fprintf(stderr, "unmapped camry host pointer\n");
        abort();
    }
    camry_aliases[camry_alias_count].host = raw;
    camry_aliases[camry_alias_count].firmware =
        CAMRY_ALIAS_BASE + (uint32_t)camry_alias_count * CAMRY_ALIAS_STRIDE;
    camry_alias_count += 1;
    return camry_aliases[camry_alias_count - 1].firmware;
}

void camry_write32(uint32_t address, uint32_t value) {
    camry_native_access(address, 4, 1);
    camry_require_access(address, 4, 1);
    value = camry_flash_write(address, value, 4);
    /* Outside raw peripheral-file mode, use the same protected sequence as
     * RunP1MEMachine: only the final control write commits and clears status. */
    if (!camry_peripheral_file && (address == 0xFFA00004u || address == 0xFFA00000u)) {
        int valid = address == 0xFFA00004u
            ? camry_flmd_stage == 0 && value == 0xA5u
            : (camry_flmd_stage == 1 && value <= 1u)
                || (camry_flmd_stage == 2 && value == (camry_flmd_desired ^ 0xFFFFFFFFu))
                || (camry_flmd_stage == 3 && value == camry_flmd_desired);
        if (!valid) {
            camry_device_fault("unsupported-flmd-sequence", address, 4, 1);
        }
        if (address == 0xFFA00004u) {
            camry_flmd_stage = 1;
        } else if (camry_flmd_stage == 3) {
            camry_flmd_stage = 0;
            camry_store_value(0xFFA00008u, 0, 4);
        } else {
            if (camry_flmd_stage == 1)
                camry_flmd_desired = value;
            camry_flmd_stage += 1;
            return;
        }
    }
    camry_store_value(address, value, 4);
}

static uint32_t camry_peripheral_poll(uint32_t address, uint32_t value, uint32_t width) {
    int index;
    uint32_t count;
    uint32_t scripted;
    if (!camry_peripheral_file || camry_native_workflow || address < 0xFF000000u
        || (address >= 0xFF200000u && address < 0xFF208000u))
        return value;
    for (index = 0; index < camry_peripheral_poll_count; index += 1) {
        if (camry_peripheral_polls[index].address == address)
            break;
    }
    if (index == camry_peripheral_poll_count) {
        if (camry_peripheral_poll_count == camry_peripheral_poll_capacity) {
            int capacity = camry_peripheral_poll_capacity * 2;
            CamryPeripheralPoll *polls;
            if (camry_peripheral_polls == camry_peripheral_poll_initial) {
                polls = malloc((size_t)capacity * sizeof(*polls));
                if (polls != NULL)
                    memcpy(polls, camry_peripheral_polls,
                        (size_t)camry_peripheral_poll_count * sizeof(*polls));
            } else {
                polls = realloc(camry_peripheral_polls,
                    (size_t)capacity * sizeof(*polls));
            }
            if (polls == NULL)
                abort();
            camry_peripheral_polls = polls;
            camry_peripheral_poll_capacity = capacity;
        }
        camry_peripheral_polls[index].address = address;
        camry_peripheral_polls[index].count = 0;
        camry_peripheral_poll_count += 1;
    }
    camry_peripheral_polls[index].count += 1;
    count = camry_peripheral_polls[index].count;
    if (count != CAMRY_PERIPHERAL_POLL_READS
        && !(width == 1u && count == CAMRY_PERIPHERAL_POLL_READS * 2u))
        return value;
    /* A byte is all-ones, then zero. A word still flips. */
    if (width == 1u)
        scripted = count == CAMRY_PERIPHERAL_POLL_READS ? 0xffu : 0u;
    else
        scripted = value == 0u ? (width == 2u ? 0xffffu : 0xffffffffu) : 0u;
    camry_store_value(address, scripted, width);
    return scripted;
}
