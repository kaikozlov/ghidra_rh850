#include <stdint.h>

typedef struct {
    uint8_t *request;
    uint32_t request_length;
} DcmMessagePrefix;

#define RESIDENT_BASE ((volatile uint8_t *)0xFEBFF9F0u)
#define HELPER_BASE ((volatile uint8_t *)0xFEF07C00u)

extern void positive(DcmMessagePrefix *message);

__attribute__((section(".text.entry")))
void tss3_application_uds_bootstrap(DcmMessagePrefix *message)
{
    uint8_t *request = message->request;
    uint32_t length = message->request_length;
    uint8_t selector = request[0];

    if (selector == 0xFFu) {
        (void)*RESIDENT_BASE;
        __asm__ volatile("syncp\n\tsynci\n\tdi" ::: "memory");
        ((void (*)(void))RESIDENT_BASE)();
        __builtin_unreachable();
    }

    uint32_t offset = (uint32_t)request[1] | ((uint32_t)request[2] << 8);
    volatile uint8_t *destination =
        (selector == 0u ? RESIDENT_BASE : HELPER_BASE) + offset;

    for (uint32_t index = 3; index < length; ++index) {
        destination[index - 3] = request[index];
    }

    positive(message);
}
