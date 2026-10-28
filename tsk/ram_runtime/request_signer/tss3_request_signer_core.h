#ifndef TSS3_REQUEST_SIGNER_CORE_H
#define TSS3_REQUEST_SIGNER_CORE_H

/*
 * Pure CPU/memory logic shared by the live TSS3 request signer and the
 * RH850 instruction-simulator fixture.
 *
 * These helpers deliberately contain no MMIO, GP-relative hardware state
 * reads, stock-function calls, or CAN transmit. They operate only on
 * caller-supplied state, scratch, and request-record bytes, and are always
 * inlined so the RAM-resident helper keeps one call-free code path. The
 * four-frame assembler copies all 28 application bytes verbatim.
 */

#include "tss3_request_signer.h"

/* Record-consumption outcomes for request assembly. */
#define ORACLE_CORE_PENDING 0    /* record consumed; transaction not complete */
#define ORACLE_CORE_COMMITTED 1  /* transaction assembled; sign it now */
#define ORACLE_CORE_REJECTED 2   /* invalid continuation; assembly reset */


/*
 * Four-frame request codec.
 *
 * Each classic frame carries seven consecutive application bytes. Header
 * high nibbles 8..B select fragments 0..3; low nibbles carry sequence low,
 * high, low, high. Fragment 0 always restarts assembly. Continuations must
 * be ordered and repeat both sequence nibbles. This does not bind every
 * fragment to the complete sequence: A[0] followed by B[1..3] is accepted when
 * A and B share the low nibble. The host must serialize complete bursts.
 *
 * payload points at the eight record payload bytes; payload[0] is the
 * fragment/sequence tag, payload[1..7] carry application bytes.
 *
 * State effects:
 *   PENDING:   state->sequence holds the running sequence (low nibble until
 *              fragment 1), state->next_fragment updated
 *   COMMITTED: state->sequence complete, assembly closed (next_fragment 0)
 *   REJECTED:  state->next_fragment reset; sequence left untouched
 */
static inline __attribute__((always_inline)) int oracle_core_assemble_fragment(
    const volatile uint8_t *payload, volatile SignerState *state,
    SignerScratch *scratch) {
  uint8_t tag = payload[0];
  uint8_t nibble = tag & 0x0f;
  unsigned fragment = (unsigned)(tag >> 4) - 8; /* type 8..B -> 0..3 */
  uint8_t *destination;
  unsigned i;

  if (fragment > 3) goto rejected;

  if (fragment == 0) {
    /* Fragment 0 starts/restarts one complete stateless transaction. */
    state->sequence = nibble; /* low nibble until fragment 1 */
    scratch->data_id = 0x8a00; /* DataID 00 8A */
  } else {
    uint8_t sequence;
    if (state->next_fragment != (uint8_t)fragment) goto rejected;
    if (fragment == 1) {
      sequence = (uint8_t)((nibble << 4) | state->sequence);
      if (sequence == 0) goto rejected;
      state->sequence = sequence;
    } else if (fragment == 2) {
      if ((uint8_t)(state->sequence & 0x0f) != nibble) goto rejected;
    } else if ((uint8_t)(state->sequence >> 4) != nibble) {
      goto rejected;
    }
  }

  /* Seven consecutive application bytes: application + fragment*7. */
  destination = &scratch->application[fragment * 7u];
  for (i = 0; i < 7; ++i) destination[i] = payload[1 + i];

  if (fragment == 3) {
    state->next_fragment = 0; /* close assembly before synchronous work */
    return ORACLE_CORE_COMMITTED;
  }
  state->next_fragment = (uint8_t)(fragment + 1);
  return ORACLE_CORE_PENDING;

rejected:
  state->next_fragment = 0;
  return ORACLE_CORE_REJECTED;
}


/*
 * Advance the private freshness epoch and message counter from the
 * EPS-authenticated trip/reset counters, prepare the stock freshness-encoder
 * input at the scratch base (trip:u32 reset:u32 message:u16 reset_low2:u8
 * bitlen:u8) plus its output length.
 */
static inline __attribute__((always_inline)) void
oracle_core_advance_freshness(volatile SignerState *state, SignerScratch *scratch,
                              uint32_t trip, uint32_t reset) {
  uint16_t trip16 = (uint16_t)trip; /* authenticated trip is 16-bit */
  uint8_t message;

  if (state->freshness_initialized && state->auth_trip == trip16 &&
      state->auth_reset == reset) {
    /* Captured reset epochs normally advance about every 300 ms: roughly
       30 attempts at 100 Hz before the new-epoch branch restarts at 1.
       Preserve the existing uint8_t wrap here. Native freshness instead
       saturates at 255 and reports exhaustion, so a stalled authenticated
       epoch can expose a mismatch. The 2026-10-20 capture audit did not
       establish EPS signer exhaustion; leave an added error path pending
       evidence that justifies its footprint. See the shared findings in
       docs/architecture/toyota-tss3-minimal-runtime.md. */
    message = (uint8_t)(state->message_counter + 1);
  } else {
    message = 1; /* new epoch */
  }
  state->auth_reset = reset;
  state->auth_trip = trip16;
  state->message_counter = message;
  state->freshness_initialized = 1;
  state->fv4 = (uint8_t)(((message & 3) << 2) | (reset & 3));

  scratch->freshness.trip = trip16;
  scratch->freshness.reset = reset;
  scratch->freshness.message = message;
  scratch->freshness.reset_low2 = (uint8_t)(reset & 3);
  scratch->freshness.bit_length = 0x2e;
  scratch->freshness_length = 0x2e;
}

/*
 * Pack the 8-byte oracle response (scratch->response) from the command-5
 * wrapper result, completion, status, and output length. The response status
 * is 0 for success, 1 for command error, and 2 for busy. Only a successful
 * command-5 completion increments success_count; failure statuses carry a
 * zero trailer. On success the big-endian CMAC prefix (scratch->mac[0]) is
 * converted to an integer, truncated to its high 28 bits, prepended with the
 * transmitted FV4 nibble, and byte-swapped once for the little-endian store.
 */
static inline __attribute__((always_inline)) void oracle_core_pack_response(
    volatile SignerState *state, SignerScratch *scratch, uint8_t sequence,
    uint32_t wrapper_result, uint8_t completion, uint8_t status,
    uint8_t output_length) {
  int response_status;
  uint32_t trailer;

  if (wrapper_result == 0 && completion == 1 && status == 0 &&
      output_length == 16) {
    response_status = 0;
    state->success_count++;
  } else if (wrapper_result == 2) {
    response_status = 2; /* busy */
  } else {
    response_status = 1; /* wrapper or command error */
  }

  if (response_status != 0) scratch->mac[0] = 0; /* failure zero trailer */

  scratch->response.magic = 0xc9;
  scratch->response.sequence = sequence;
  scratch->response.status = (uint8_t)response_status;
  scratch->response.inverted_sequence = (uint8_t)~sequence;

  if (response_status == 0) {
    uint32_t mac_prefix = __builtin_bswap32(scratch->mac[0]);
    trailer = __builtin_bswap32((mac_prefix >> 4) |
                                ((uint32_t)state->fv4 << 28));
  } else {
    trailer = 0;
  }
  scratch->response.trailer = trailer;
}

#endif
