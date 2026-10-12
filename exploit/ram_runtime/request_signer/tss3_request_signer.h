#ifndef TSS3_REQUEST_SIGNER_H
#define TSS3_REQUEST_SIGNER_H

#include <stddef.h>
#include <stdint.h>

/* Layout shared with the host, resident, and exact-firmware simulator. */
typedef struct {
    uint32_t magic;
    uint8_t version;
    uint8_t active;
    uint8_t sequence;
    uint8_t next_fragment;
    uint32_t request_count;
    uint32_t success_count;
    uint32_t response_count;
    uint8_t wrapper_result;
    uint8_t command_completion;
    uint8_t command_status;
    uint8_t command_outlen;
    uint32_t auth_reset;
    uint16_t auth_trip;
    uint8_t message_counter;
    uint8_t freshness_initialized;
    uint16_t cursor;
    uint8_t fv4;
    uint8_t reserved;
} SignerState;

/* The stock freshness encoder consumes the first 12 bytes. */
typedef struct {
    uint32_t trip;
    uint32_t reset;
    uint16_t message;
    uint8_t reset_low2;
    uint8_t bit_length;
} SignerFreshness;

typedef struct {
    uint8_t magic;
    uint8_t sequence;
    uint8_t status;
    uint8_t inverted_sequence;
    uint32_t trailer;
} SignerResponse;

typedef struct {
    uint16_t confirmation_handle;
    uint8_t length;
    uint8_t reserved;
    uint32_t can_id;
    uint8_t *data;
} SignerPdu;

typedef struct {
    SignerFreshness freshness;       /* +0 */
    uint32_t reserved;              /* +12 */
    uint16_t data_id;               /* +16: wire bytes 00 8A */
    uint8_t application[28];        /* +18 */
    uint8_t encoded_freshness[6];   /* +46 */
    uint32_t mac[4];                /* +52 */
    uint32_t mac_length;            /* +68 */
    uint32_t command_config[2];     /* +72: type, selector */
    SignerResponse response;        /* +80: header bytes and aligned trailer */
    SignerPdu pdu;                  /* +88 */
    uint32_t freshness_length;      /* +100 */
} SignerScratch;

typedef struct {
    uint32_t *config;
    uint8_t *input;
    uint32_t input_length;
    uint8_t reserved[16];
    uint8_t completion;
    uint8_t status;
    uint8_t tail[14];
} SignerCommandGlobals;

/* Serialized in CONFIG_FIELDS order by build_tss3_request_signer.py. The
 * builder generates offset assertions against that owner before compilation. */
typedef struct {
    uintptr_t app_context;
    uintptr_t startup_first;
    uintptr_t startup_after;
    void (*startup_final)(uint32_t);
    volatile uint8_t *timing_flag;
    volatile uint8_t *tick_counter;
    void (*fg_timing_begin)(void);
    void (*fg_pre_0)(void);
    void (*fg_pre_1)(void);
    void (*fg_pre_2)(void);
    void (*fg_pre_3)(void);
    void (*fg_aggregate)(void);
    void (*fg_post_0)(void);
    void (*fg_post_1)(void);
    void (*fg_post_2)(void);
    void (*fg_timing_end)(void);
    volatile SignerState *state_base;
    SignerScratch *scratch_base;
    const volatile uint32_t *ring_base;
    const volatile uint16_t *ring_producer;
    const volatile uint32_t *auth_reset;
    const volatile uint32_t *auth_trip;
    void (*freshness_encode)(SignerFreshness *, uint8_t *, uint32_t *);
    uint32_t (*command5_sync)(uint32_t, uint32_t *, uint32_t *, uint32_t);
    uint32_t (*lower_can_write)(uint32_t, SignerPdu *);
    volatile SignerCommandGlobals *command5_globals;
    uint32_t response_handle;
} SignerConfig;

_Static_assert(sizeof(SignerState) == 0x24, "signer state ABI");
_Static_assert(offsetof(SignerState, cursor) == 32, "private cursor ABI");
_Static_assert(offsetof(SignerState, auth_reset) == 24, "freshness state ABI");
_Static_assert(sizeof(SignerFreshness) == 12, "freshness encoder ABI");
_Static_assert(sizeof(SignerResponse) == 8, "response wire ABI");
_Static_assert(offsetof(SignerResponse, trailer) == 4, "response trailer ABI");
_Static_assert(sizeof(SignerPdu) == 12, "lower CAN PDU ABI");
_Static_assert(sizeof(SignerScratch) == 0x68, "signer scratch ABI");
_Static_assert(offsetof(SignerScratch, application) == 18, "application ABI");
_Static_assert(offsetof(SignerScratch, mac) == 52, "command output ABI");
_Static_assert(offsetof(SignerScratch, pdu) == 88, "response PDU ABI");
_Static_assert(offsetof(SignerScratch, freshness_length) == 100, "encoder length ABI");
_Static_assert(offsetof(SignerCommandGlobals, completion) == 0x1c, "command status ABI");
_Static_assert(sizeof(SignerCommandGlobals) == 0x2c, "command globals ABI");

#ifdef ORACLE_CONFIG_BASE
#define SIGNER_CONFIG ((const SignerConfig *)(uintptr_t)ORACLE_CONFIG_BASE)
#endif

#endif
