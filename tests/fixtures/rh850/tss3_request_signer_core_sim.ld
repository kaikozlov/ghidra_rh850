ENTRY(_start)

SECTIONS
{
  . = 0xFEBF0000;
  .text : { *(.text*) }

  . = ALIGN(4);
  .rodata : { *(.rodata*) }

  . = ALIGN(4);
  .data : { *(.data*) }

  . = ALIGN(4);
  .bss : { *(.bss*) *(COMMON) }
}
