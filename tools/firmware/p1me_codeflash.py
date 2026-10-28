"""Input geometry for bare 1-MiB RH850/P1M-E user CodeFlash images."""

# Images start at VA zero and exclude DataFlash and the extended user area.
P1M_E_CODEFLASH_SIZE = 0x100000
P1M_E_DATAFLASH_PREFIX_SIZE = 0x8000
CONCATENATED_DUMP_SIZE = P1M_E_CODEFLASH_SIZE + P1M_E_DATAFLASH_PREFIX_SIZE


def validate_codeflash_geometry(size: int) -> None:
    """Fail closed unless the image has the bare 1 MiB user-area geometry."""
    if size < 0:
        raise ValueError("image size must not be negative")
    if size == P1M_E_CODEFLASH_SIZE:
        return
    if size == CONCATENATED_DUMP_SIZE:
        raise ValueError(
            f"image is {size} (0x{size:X}) bytes: this is the DataFlash+CodeFlash concatenated "
            f"dump geometry; strip the leading 0x{P1M_E_DATAFLASH_PREFIX_SIZE:X} DataFlash bytes "
            f"and supply the bare 0x{P1M_E_CODEFLASH_SIZE:X}-byte CodeFlash image"
        )
    raise ValueError(
        f"unexpected CodeFlash image geometry: {size} (0x{size:X}) bytes; expected exactly "
        f"0x{P1M_E_CODEFLASH_SIZE:X} (1 MiB) P1M-E user CodeFlash — reject truncated or oversized images"
    )
