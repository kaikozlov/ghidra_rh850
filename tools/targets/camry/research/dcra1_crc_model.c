/* GNU-sim replacement for the P1M-E DCRA1 mode-0 word CRC path.
 *
 * Exact Camry code at 0x67060 writes raw_seed to DCRA1COUT, then writes
 * byte_count >> 2 source words to DCRA1CIN and returns the inverse of COUT.
 * RunP1MEMachine models mode 0 as reflected CRC-32 (poly 0xEDB88320), with
 * COUT holding the inverse of the internal CRC.  Returning the internal CRC
 * therefore preserves the firmware-visible value from 0x6708C.
 */
#include <stdint.h>

uint32_t dcra1_crc_raw_words_model(const uint32_t *source,
                                   uint32_t byte_count,
                                   uint32_t raw_seed)
{
    uint32_t crc = raw_seed;
    uint32_t words = byte_count >> 2;

    for (uint32_t index = 0; index < words; ++index) {
        crc ^= source[index];
        for (uint32_t bit = 0; bit < 32; ++bit) {
            uint32_t polynomial = (uint32_t)-(int32_t)(crc & 1u) & 0xEDB88320u;
            crc = (crc >> 1) ^ polynomial;
        }
    }
    return crc;
}
