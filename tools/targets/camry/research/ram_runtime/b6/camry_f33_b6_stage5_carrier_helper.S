/* Deliberate bad-MAC variant of the exact-F33 inline B6 helper.

   The shared helper still proves the untouched native signature and computes
   the replacement signature.  This build alone retains the native trailer
   when it commits changed B3..B9, isolating stage-5 receiver-result bypass
   behavior from command-5 signing and external B6 delivery. */
#define F33_STAGE5_CARRIER 1
#include "camry_f33_b6_inline_signer_helper.S"
