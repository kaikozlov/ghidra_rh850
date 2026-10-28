/*
 * Shared TSS3 request signer helper.
 *
 * The resident checks an idle window before entry, or invokes this after stock
 * foreground work. This drain loop does not recheck the timer or tick flag.
 * The private cursor does not modify stock consumer state.
 *
 * Four classic 0x777 records carry application[0..27]. Fragment zero restarts
 * assembly; continuations check fragment order and repeated sequence nibbles.
 * A fragment does not carry the complete sequence, so some mixed transactions
 * are indistinguishable.
 *
 * The machine-resolved runtime config supplies only the stock signer and I/O
 * ABI: state/scratch, ring, freshness epoch, command-5 wrapper/globals, lower
 * CAN writer, and response handle. No target code is called directly; every
 * firmware entry comes from the immutable config.
 */

#ifndef ORACLE_CONFIG_BASE
#error ORACLE_CONFIG_BASE is required
#endif

#include "tss3_request_signer_core.h"

/* Software RX ring geometry: 0x228 words of four bytes each. */
#define ORACLE_RING_WORDS 0x228u

/* Exact functional-diagnostic classic request record header: route_tag = 0,
 * callback selector = 0x04, received length = 8, standard CAN 0x777. */
#define ORACLE_REQUEST_HEADER 0x00000408u
#define ORACLE_REQUEST_CAN_ID 0x00000777u

__attribute__((section(".text.entry")))
void helper_entry(void) {
  const SignerConfig *config = SIGNER_CONFIG;
  volatile SignerState *state = config->state_base;
  SignerScratch *scratch = config->scratch_base;

  for (;;) {
    uint16_t producer = *config->ring_producer;
    uint16_t cursor = state->cursor; /* private oracle tap */
    unsigned reload = 0;

    while (producer != cursor) {
      const volatile uint32_t *record;
      const volatile uint8_t *payload;
      uint32_t header;
      uint32_t record_size;
      uint16_t next;
      int committed = 0;

      /* Stock wrap sentinel needs two readable words at the current index. */
      if (cursor + 2u > ORACLE_RING_WORDS) return;

      record = config->ring_base + cursor;
      header = record[0];
      if (~header != record[1]) return; /* header/complement guard */

      if (header == 0xffffffffu) { /* stock wrap sentinel */
        cursor = 0;
        state->cursor = 0;
        continue;
      }

      /* Record size in ring words from the received length byte. */
      {
        uint32_t received_length = header & 0xffu;
        record_size = received_length <= 8
                          ? 5
                          : (((received_length + 7) >> 3) << 1) + 3;
      }
      next = (uint16_t)(cursor + record_size);
      if (next > ORACLE_RING_WORDS) return; /* word bounds */
      if (next == ORACLE_RING_WORDS) next = 0; /* wrap the private tap */

      payload = (const volatile uint8_t *)record + 12;
      if (header == ORACLE_REQUEST_HEADER &&
          record[2] == ORACLE_REQUEST_CAN_ID) {
        committed = oracle_core_assemble_fragment(payload, state, scratch) ==
                    ORACLE_CORE_COMMITTED;
      }

      if (!committed) {
        /* Consume the record and continue scanning; partial and rejected
           frames never block later records. */
        state->cursor = next;
        cursor = next;
        continue;
      }

      /* Transaction assembled: sign synchronously, then transmit. */
      {
        uint8_t sequence = state->sequence; /* complete response sequence */
        volatile SignerCommandGlobals *globals;
        uint32_t reset;
        uint32_t trip;
        uint32_t wrapper_result;
        uint8_t completion;
        uint8_t command_status;
        uint8_t output_length;

        /* Advance the private tap before synchronous signing. Any records
           arriving while command5 runs remain discoverable from the producer
           on reload. */
        state->cursor = next;
        state->request_count++;

        /* Read the EPS-authenticated current epoch. */
        reset = *config->auth_reset;
        trip = *config->auth_trip;
        oracle_core_advance_freshness(state, scratch, trip, reset);
        config->freshness_encode(&scratch->freshness, scratch->encoded_freshness,
                                 &scratch->freshness_length);

        /* Fixed command5 config {type=1, selector=4}. The 36-byte command
           input is data_id + application + encoded_freshness. */
        scratch->command_config[0] = 1;
        scratch->command_config[1] = 4;
        globals = config->command5_globals;
        globals->config = scratch->command_config;
        globals->input = (uint8_t *)&scratch->data_id;
        globals->input_length = 36;
        scratch->mac_length = 16;

        wrapper_result =
            config->command5_sync(0, scratch->mac, &scratch->mac_length, 1);

        state->wrapper_result = (uint8_t)wrapper_result;
        globals = config->command5_globals;
        completion = globals->completion;
        command_status = globals->status;
        output_length = (uint8_t)scratch->mac_length;
        state->command_completion = completion;
        state->command_status = command_status;
        state->command_outlen = output_length;

        oracle_core_pack_response(state, scratch, sequence, wrapper_result,
                                  completion, command_status, output_length);

        /* Reuse the target's diagnostic response mailbox and no-op software
           confirmation handle; do not manufacture CanTp state. */
        scratch->pdu.confirmation_handle = 0x00f0;
        scratch->pdu.length = 8;
        scratch->pdu.reserved = 0;
        scratch->pdu.can_id = 0x000007a9;
        scratch->pdu.data = (uint8_t *)&scratch->response;
        if (config->lower_can_write(config->response_handle, &scratch->pdu) !=
            0)
          return;
        state->response_count++;
        /* command5/lower-write may span new RX arrivals. Reload the producer
           and continue from the private cursor rather than relying on stale
           ring state. */
        reload = 1;
        break;
      }
    }
    if (!reload) return;
  }
}
