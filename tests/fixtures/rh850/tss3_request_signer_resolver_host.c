#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define CODEFLASH_SIZE 0x100000u
#define OUTPUT_WORDS 33u

int resolve_request_signer_image(const uint8_t *image, uint32_t *output);

int main(int argc, char **argv)
{
    uint8_t *image;
    uint32_t output[OUTPUT_WORDS] = {0};
    FILE *stream;
    int result;
    unsigned index;

    if (argc != 2) {
        return 2;
    }
    image = malloc(CODEFLASH_SIZE);
    if (image == NULL) {
        return 3;
    }
    stream = fopen(argv[1], "rb");
    if (stream == NULL || fread(image, 1, CODEFLASH_SIZE, stream) != CODEFLASH_SIZE ||
        fgetc(stream) != EOF) {
        free(image);
        if (stream != NULL) {
            fclose(stream);
        }
        return 4;
    }
    fclose(stream);

    result = resolve_request_signer_image(image, output);
    free(image);
    printf("%d", result);
    if (result == 0) {
        for (index = 0; index < OUTPUT_WORDS; ++index) {
            printf(" %08x", output[index]);
        }
    }
    putchar('\n');
    return 0;
}
