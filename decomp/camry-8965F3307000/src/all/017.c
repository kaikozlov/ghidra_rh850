#include "common.h"


/* After both common initializers, copyE400/E600 publication fields into6434..644C and6768..6794 ECU
   views. Does not publish liveB11A toE8CC or obtain new physical inputs. */

void f33_snapshot_initialized_control_publications(void)

{
  DAT_febe643c = DAT_febee408;
  DAT_febe6770 = DAT_febee408;
  DAT_febe6772 = DAT_febee40a;
  DAT_febe6774 = DAT_febee40c;
  DAT_febe6776 = DAT_febee40e;
  DAT_febe6768 = DAT_febee400;
  DAT_febe6778 = DAT_febee410;
  DAT_febe677a = DAT_febee412;
  DAT_febe6769 = DAT_febee401;
  DAT_febe676a = DAT_febee402;
  DAT_febe676b = DAT_febee403;
  DAT_febe676c = DAT_febee404;
  DAT_febe677c = DAT_febee414;
  DAT_febe676d = DAT_febee405;
  DAT_febe677e = DAT_febee416;
  DAT_febe676e = DAT_febee406;
  DAT_febe6780 = DAT_febee418;
  DAT_febe676f = DAT_febee407;
  DAT_febe643b = DAT_febee407;
  DAT_febe643e = DAT_febee40a;
  DAT_febe6440 = DAT_febee40c;
  DAT_febe6442 = DAT_febee40e;
  DAT_febe678c = DAT_febee608;
  DAT_febe6434 = DAT_febee400;
  DAT_febe6444 = DAT_febee410;
  DAT_febe6446 = DAT_febee412;
  DAT_febe6784 = DAT_febee600;
  DAT_febe6435 = DAT_febee401;
  DAT_febe6436 = DAT_febee402;
  DAT_febe6437 = DAT_febee403;
  DAT_febe6794 = DAT_febee610;
  DAT_febe6438 = DAT_febee404;
  DAT_febe6448 = DAT_febee414;
  DAT_febe6439 = DAT_febee405;
  DAT_febe6785 = DAT_febee601;
  DAT_febe644a = DAT_febee416;
  DAT_febe643a = DAT_febee406;
  DAT_febe644c = DAT_febee418;
  DAT_febe6786 = DAT_febee602;
  DAT_febe6787 = DAT_febee603;
  DAT_febe678e = DAT_febee60a;
  DAT_febe6788 = DAT_febee604;
  DAT_febe6789 = DAT_febee605;
  DAT_febe678a = DAT_febee606;
  DAT_febe6790 = DAT_febee60c;
  return;
}



void FUN_0005c7b6(void)

{
  DAT_febe61a8 = DAT_febe824c;
  DAT_febe61aa = DAT_febe824e;
  DAT_febe61ac = DAT_febe8250;
  DAT_febe61ae = DAT_febe8252;
  DAT_febe61b0 = DAT_febe8254;
  DAT_febe61b2 = DAT_febe8256;
  DAT_febe61a0 = DAT_febe8244;
  DAT_febe61a1 = DAT_febe8245;
  DAT_febe61a2 = DAT_febe8246;
  DAT_febe61a3 = DAT_febe8247;
  DAT_febe61a4 = DAT_febe8248;
  DAT_febe61a5 = DAT_febe8249;
  DAT_febe61a6 = DAT_febe824a;
  DAT_febe61a7 = DAT_febe824b;
  DAT_febe61b4 = DAT_febe8258;
  DAT_febe61b6 = DAT_febe825a;
  DAT_febe61b8 = DAT_febe825c;
  DAT_febe61ba = DAT_febe825e;
  DAT_febe616a = DAT_febe8b60;
  DAT_febe616c = DAT_febe8b62;
  DAT_febe616e = DAT_febe8b64;
  DAT_febe6170 = DAT_febe8b66;
  DAT_febe6172 = DAT_febe8b68;
  DAT_febe6174 = DAT_febe8b6a;
  DAT_febe6176 = DAT_febe8b6c;
  DAT_febe6178 = DAT_febe8b6e;
  DAT_febe617a = DAT_febe8b70;
  DAT_febe617c = DAT_febe8b72;
  DAT_febe617e = DAT_febe8b74;
  DAT_febe6180 = DAT_febe8b76;
  DAT_febe6182 = DAT_febe8b78;
  DAT_febe6184 = DAT_febe8b7a;
  DAT_febe6186 = DAT_febe8b7c;
  DAT_febe6188 = DAT_febe8b7e;
  DAT_febe618a = DAT_febe8b80;
  DAT_febe618c = DAT_febe8b82;
  DAT_febe6168 = DAT_febe8b5e;
  DAT_febe6169 = DAT_febe8b5f;
  DAT_febe61cc = DAT_febe7e2e;
  DAT_febe61ce = DAT_febe7e30;
  DAT_febe61d0 = DAT_febe7e32;
  DAT_febe61d2 = DAT_febe7e34;
  DAT_febe61d4 = DAT_febe7e36;
  DAT_febe61d6 = DAT_febe7e38;
  DAT_febe61d8 = DAT_febe7e3a;
  DAT_febe61da = DAT_febe7e3c;
  DAT_febe61dc = DAT_febe7e3e;
  DAT_febe61de = DAT_febe7e40;
  DAT_febe61e0 = DAT_febe7e42;
  DAT_febe61e2 = DAT_febe7e44;
  DAT_febe61e4 = DAT_febe7e46;
  DAT_febe61e6 = DAT_febe7e48;
  DAT_febe61e8 = DAT_febe7e4a;
  DAT_febe61ea = DAT_febe7e4c;
  DAT_febe61ec = DAT_febe7e4e;
  DAT_febe61ee = DAT_febe7e50;
  DAT_febe61bc = DAT_febe7e1c;
  DAT_febe61bd = DAT_febe7e1d;
  DAT_febe61be = DAT_febe7e1e;
  DAT_febe61bf = DAT_febe7e1f;
  DAT_febe61c0 = DAT_febe7e20;
  DAT_febe61c1 = DAT_febe7e21;
  DAT_febe61c2 = DAT_febe7e22;
  DAT_febe61c3 = DAT_febe7e23;
  DAT_febe61c4 = DAT_febe7e24;
  DAT_febe61c5 = DAT_febe7e25;
  DAT_febe61c6 = DAT_febe7e26;
  DAT_febe61c7 = DAT_febe7e27;
  DAT_febe61c8 = DAT_febe7e28;
  DAT_febe61c9 = DAT_febe7e29;
  DAT_febe61ca = DAT_febe7e2a;
  DAT_febe61cb = DAT_febe7e2b;
  DAT_febe61f0 = DAT_febe7e54;
  DAT_febe61f4 = DAT_febe7e58;
  DAT_febe61f8 = DAT_febe7e5c;
  DAT_febe61fc = DAT_febe7e60;
  DAT_febe6200 = DAT_febe7e64;
  DAT_febe6204 = DAT_febe7e68;
  DAT_febe6208 = DAT_febe7d74;
  DAT_febe6190 = DAT_febe5f34;
  DAT_febe6192 = DAT_febe5f36;
  DAT_febe6194 = DAT_febe5f38;
  DAT_febe6198 = DAT_febe5f40;
  DAT_febe619c = DAT_febe5f44;
  DAT_febe620c = DAT_febe7ea8;
  DAT_febe620e = DAT_febe7eaa;
  DAT_febe6210 = f33_mode600_stimulus_fit_work.stimulus_valid;
  DAT_febe6212 = f33_mode600_stimulus_fit_work.stimulus;
  DAT_febe621c = DAT_febe6d78;
  DAT_febe6214 = DAT_febe6d70;
  DAT_febe6216 = DAT_febe6d72;
  DAT_febe6218 = DAT_febe6d74;
  DAT_febe621a = DAT_febe6d76;
  DAT_febe6220 = DAT_febe6d7c;
  DAT_febe6222 = DAT_febe6d7e;
  DAT_febe6224 = DAT_febe6d80;
  DAT_febe6226 = DAT_febe6d82;
  DAT_febe6228 = DAT_febe6d84;
  DAT_febe622a = DAT_febe6d86;
  return;
}



/* Copy current ECU acquisition/status into CH2-specific views;822C/8238 banks become622C/6238.
   Called in58A1C FFC0 window; foreground6450/645C copies remain a different generation. */

void f33_snapshot_ecu_ch2_acquisition(void)

{
  DAT_febe622c = DAT_febe822c;
  DAT_febe622e = DAT_febe822e;
  DAT_febe6230 = DAT_febe8230;
  DAT_febe6232 = DAT_febe8232;
  DAT_febe6234 = DAT_febe8234;
  DAT_febe6236 = DAT_febe8236;
  DAT_febe6238 = DAT_febe8238;
  DAT_febe623a = DAT_febe823a;
  DAT_febe623c = DAT_febe823c;
  DAT_febe623e = DAT_febe823e;
  DAT_febe6240 = DAT_febe8240;
  DAT_febe6242 = DAT_febe8242;
  DAT_febe6354 = DAT_febe824c;
  DAT_febe6356 = DAT_febe824e;
  DAT_febe6358 = DAT_febe8250;
  DAT_febe635a = DAT_febe8252;
  DAT_febe635c = DAT_febe8254;
  DAT_febe635e = DAT_febe8256;
  DAT_febe634c = DAT_febe8244;
  DAT_febe634d = DAT_febe8245;
  DAT_febe634e = DAT_febe8246;
  DAT_febe634f = DAT_febe8247;
  DAT_febe6350 = DAT_febe8248;
  DAT_febe6351 = DAT_febe8249;
  DAT_febe6352 = DAT_febe824a;
  DAT_febe6353 = DAT_febe824b;
  DAT_febe6360 = DAT_febe8258;
  DAT_febe6362 = DAT_febe825a;
  DAT_febe6364 = DAT_febe825c;
  DAT_febe6366 = DAT_febe825e;
  DAT_febe625e = DAT_febe8b60;
  DAT_febe6260 = DAT_febe8b62;
  DAT_febe6262 = DAT_febe8b64;
  DAT_febe6264 = DAT_febe8b66;
  DAT_febe6266 = DAT_febe8b68;
  DAT_febe6268 = DAT_febe8b6a;
  DAT_febe626a = DAT_febe8b6c;
  DAT_febe626c = DAT_febe8b6e;
  DAT_febe626e = DAT_febe8b70;
  DAT_febe6270 = DAT_febe8b72;
  DAT_febe6272 = DAT_febe8b74;
  DAT_febe6274 = DAT_febe8b76;
  DAT_febe6276 = DAT_febe8b78;
  DAT_febe6278 = DAT_febe8b7a;
  DAT_febe627a = DAT_febe8b7c;
  DAT_febe627c = DAT_febe8b7e;
  DAT_febe627e = DAT_febe8b80;
  DAT_febe6280 = DAT_febe8b82;
  DAT_febe625c = DAT_febe8b5e;
  DAT_febe625d = DAT_febe8b5f;
  DAT_febe6378 = DAT_febe7e2e;
  DAT_febe637a = DAT_febe7e30;
  DAT_febe637c = DAT_febe7e32;
  DAT_febe637e = DAT_febe7e34;
  DAT_febe6380 = DAT_febe7e36;
  DAT_febe6382 = DAT_febe7e38;
  DAT_febe6384 = DAT_febe7e3a;
  DAT_febe6386 = DAT_febe7e3c;
  DAT_febe6388 = DAT_febe7e3e;
  DAT_febe638a = DAT_febe7e40;
  DAT_febe638c = DAT_febe7e42;
  DAT_febe638e = DAT_febe7e44;
  DAT_febe6390 = DAT_febe7e46;
  DAT_febe6392 = DAT_febe7e48;
  DAT_febe6394 = DAT_febe7e4a;
  DAT_febe6396 = DAT_febe7e4c;
  DAT_febe6398 = DAT_febe7e4e;
  DAT_febe639a = DAT_febe7e50;
  DAT_febe6368 = DAT_febe7e1c;
  DAT_febe6369 = DAT_febe7e1d;
  DAT_febe636a = DAT_febe7e1e;
  DAT_febe636b = DAT_febe7e1f;
  DAT_febe636c = DAT_febe7e20;
  DAT_febe636d = DAT_febe7e21;
  DAT_febe636e = DAT_febe7e22;
  DAT_febe636f = DAT_febe7e23;
  DAT_febe6370 = DAT_febe7e24;
  DAT_febe6371 = DAT_febe7e25;
  DAT_febe6372 = DAT_febe7e26;
  DAT_febe6373 = DAT_febe7e27;
  DAT_febe6374 = DAT_febe7e28;
  DAT_febe6375 = DAT_febe7e29;
  DAT_febe6376 = DAT_febe7e2a;
  DAT_febe6377 = DAT_febe7e2b;
  DAT_febe639c = DAT_febe7e54;
  DAT_febe63a0 = DAT_febe7e58;
  DAT_febe63a4 = DAT_febe7e5c;
  DAT_febe63a8 = DAT_febe7e60;
  DAT_febe63ac = DAT_febe7e64;
  DAT_febe63b0 = DAT_febe7e68;
  DAT_febe6294 = DAT_febe7d94;
  DAT_febe6284 = DAT_febe7d78;
  DAT_febe6286 = DAT_febe7d7a;
  DAT_febe6288 = DAT_febe7d7c;
  DAT_febe628a = DAT_febe7d7e;
  DAT_febe628c = DAT_febe7d80;
  DAT_febe628e = DAT_febe7d82;
  DAT_febe6290 = DAT_febe7d84;
  DAT_febe6298 = DAT_febe7da0;
  DAT_febe6292 = DAT_febe7d92;
  DAT_febe63b4 = DAT_febe7d74;
  DAT_febe63b8 = DAT_febe7d4a;
  DAT_febe63ba = DAT_febe7d4c;
  DAT_febe63bc = DAT_febe7d4e;
  DAT_febe63be = DAT_febe7d50;
  DAT_febe63c0 = DAT_febe7d54;
  DAT_febe63c2 = DAT_febe7d56;
  DAT_febe63c4 = DAT_febe7d58;
  DAT_febe63c6 = DAT_febe7d5a;
  DAT_febe63c8 = DAT_febe7d5c;
  DAT_febe63ca = DAT_febe7d60;
  DAT_febe63cc = DAT_febe7d62;
  DAT_febe63ce = DAT_febe7d66;
  DAT_febe63d0 = DAT_febe7d68;
  DAT_febe629c = DAT_febe5f34;
  DAT_febe629e = DAT_febe5f36;
  DAT_febe62a0 = DAT_febe5f38;
  DAT_febe62a4 = DAT_febe5f40;
  DAT_febe62a8 = DAT_febe5f44;
  DAT_febe63d4 = DAT_febe7ea8;
  DAT_febe63d6 = DAT_febe7eaa;
  DAT_febe6424 = DAT_febe77c4;
  DAT_febe6425 = DAT_febe77c7;
  DAT_febe6428 = DAT_febe78d4;
  DAT_febe6429 = DAT_febe78d7;
  DAT_febe642c = DAT_febe754f;
  DAT_febe642d = DAT_febe7550;
  DAT_febe642e = DAT_febe7551;
  DAT_febe642f = DAT_febe7552;
  DAT_febe63dc = DAT_febe6b2d;
  DAT_febe63dd = DAT_febe6b2e;
  DAT_febe62bc = DAT_febe6b34;
  DAT_febe62be = DAT_febe6b36;
  DAT_febe62c0 = DAT_febe6b38;
  DAT_febe62c2 = DAT_febe6b3a;
  DAT_febe62c4 = DAT_febe6b3c;
  DAT_febe62c8 = DAT_febe6b40;
  DAT_febe62cc = DAT_febe6b44;
  DAT_febe62d0 = DAT_febe6b48;
  DAT_febe63e6 = DAT_febe6e12;
  DAT_febe63e8 = DAT_febe6e14;
  DAT_febe63ea = DAT_febe6e16;
  DAT_febe63ec = DAT_febe6e18;
  DAT_febe63fc = DAT_febe6e28;
  DAT_febe6400 = DAT_febe6e2c;
  DAT_febe6404 = DAT_febe6e30;
  DAT_febe6408 = DAT_febe6e34;
  DAT_febe63ee = DAT_febe6e1a;
  DAT_febe63f0 = DAT_febe6e1c;
  DAT_febe63f2 = DAT_febe6e1e;
  DAT_febe63f4 = DAT_febe6e20;
  DAT_febe63f6 = DAT_febe6e22;
  DAT_febe63f8 = DAT_febe6e24;
  DAT_febe63e0 = DAT_febe6e0c;
  DAT_febe63e1 = DAT_febe6e0d;
  DAT_febe63e2 = DAT_febe6e0e;
  DAT_febe63e3 = DAT_febe6e0f;
  DAT_febe63e4 = DAT_febe6e10;
  DAT_febe63fa = DAT_febe6e26;
  DAT_febe6414 = DAT_febe6d78;
  DAT_febe640c = DAT_febe6d70;
  DAT_febe640e = DAT_febe6d72;
  DAT_febe6410 = DAT_febe6d74;
  DAT_febe6412 = DAT_febe6d76;
  DAT_febe6418 = DAT_febe6d7c;
  DAT_febe641a = DAT_febe6d7e;
  DAT_febe641c = DAT_febe6d80;
  DAT_febe641e = DAT_febe6d82;
  DAT_febe6420 = DAT_febe6d84;
  DAT_febe6422 = DAT_febe6d86;
  DAT_febe62d4 = DAT_febe6c40;
  DAT_febe62d6 = DAT_febe6c42;
  DAT_febe62d8 = DAT_febe6c44;
  DAT_febe62da = DAT_febe6c46;
  DAT_febe62e0 = DAT_febe6c60;
  DAT_febe62dc = DAT_febe6c4a;
  DAT_febe62e4 = DAT_febe6d5c;
  DAT_febe62e5 = DAT_febe6d5d;
  DAT_febe62e6 = DAT_febe6d5e;
  DAT_febe62e8 = DAT_febe6d60;
  DAT_febe62ec = DAT_febe6b9c;
  DAT_febe62f0 = DAT_febe6ba0;
  DAT_febe62f4 = DAT_febe6ba4;
  DAT_febe62f8 = DAT_febe6bb4;
  DAT_febe62fc = DAT_febe6bb8;
  DAT_febe6300 = DAT_febe6bbc;
  DAT_febe6304 = DAT_febe6bc0;
  DAT_febe6308 = DAT_febe6bc4;
  DAT_febe630c = DAT_febe6bc8;
  DAT_febe6310 = DAT_febe6bd8;
  DAT_febe6314 = DAT_febe6bdc;
  DAT_febe6318 = DAT_febe6be0;
  return;
}



/* Cell-block copy: 83 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_5cf1c(void)

{
  DAT_febe6244 = DAT_febe81f4;
  DAT_febe6246 = DAT_febe81f6;
  DAT_febe6248 = DAT_febe81f8;
  DAT_febe624a = DAT_febe81fa;
  DAT_febe624c = DAT_febe81fc;
  DAT_febe624e = DAT_febe81fe;
  DAT_febe6250 = DAT_febe8200;
  DAT_febe6252 = DAT_febe8202;
  DAT_febe6254 = DAT_febe8204;
  DAT_febe6256 = DAT_febe8206;
  DAT_febe6258 = DAT_febe8208;
  DAT_febe625a = DAT_febe820a;
  DAT_febe62ac = DAT_febe7dea;
  DAT_febe62ae = DAT_febe7dec;
  DAT_febe62b0 = DAT_febe7dee;
  DAT_febe62b2 = DAT_febe7df0;
  DAT_febe62b4 = DAT_febe7df2;
  DAT_febe62b6 = DAT_febe7df4;
  DAT_febe62b8 = DAT_febe7df6;
  DAT_febe62ba = DAT_febe7df8;
  DAT_febe63d8 = DAT_febe7e0c;
  DAT_febe6430 = DAT_febe7bfc;
  DAT_febe631c = DAT_febe7c38;
  DAT_febe631d = DAT_febe7c39;
  DAT_febe631e = DAT_febe7c3a;
  DAT_febe631f = DAT_febe7c3b;
  DAT_febe6320 = DAT_febe7c3c;
  DAT_febe6321 = DAT_febe7c3d;
  DAT_febe6322 = DAT_febe7c3e;
  DAT_febe6323 = DAT_febe7c3f;
  DAT_febe6324 = DAT_febe7c40;
  DAT_febe6325 = DAT_febe7c41;
  DAT_febe6326 = DAT_febe7c42;
  DAT_febe6327 = DAT_febe7c43;
  DAT_febe6328 = DAT_febe7c44;
  DAT_febe6329 = DAT_febe7c45;
  DAT_febe632a = DAT_febe7c46;
  DAT_febe632b = DAT_febe7c47;
  DAT_febe632c = DAT_febe7c48;
  DAT_febe632d = DAT_febe7c49;
  DAT_febe632e = DAT_febe7c4a;
  DAT_febe632f = DAT_febe7c4b;
  DAT_febe6330 = DAT_febe7c4c;
  DAT_febe6331 = DAT_febe7c4d;
  DAT_febe6334 = DAT_febe7c50;
  DAT_febe6335 = DAT_febe7c51;
  DAT_febe6336 = DAT_febe7c52;
  DAT_febe6337 = DAT_febe7c53;
  DAT_febe6338 = DAT_febe7c54;
  DAT_febe6339 = DAT_febe7c55;
  DAT_febe633a = DAT_febe7c56;
  DAT_febe633b = DAT_febe7c57;
  DAT_febe633c = DAT_febe7c58;
  DAT_febe633d = DAT_febe7c59;
  DAT_febe633e = DAT_febe7c5a;
  DAT_febe633f = DAT_febe7c5b;
  DAT_febe6340 = DAT_febe7c5c;
  DAT_febe6341 = DAT_febe7c5d;
  DAT_febe6342 = DAT_febe7c5e;
  DAT_febe6343 = DAT_febe7c5f;
  DAT_febe6344 = DAT_febe7c60;
  DAT_febe6345 = DAT_febe7c61;
  DAT_febe6346 = DAT_febe7c62;
  DAT_febe6347 = DAT_febe7c63;
  DAT_febe6348 = DAT_febe7c64;
  DAT_febe6349 = DAT_febe7c65;
  DAT_febe643c = DAT_febee408;
  DAT_febe643e = DAT_febee40a;
  DAT_febe6440 = DAT_febee40c;
  DAT_febe6442 = DAT_febee40e;
  DAT_febe6434 = DAT_febee400;
  DAT_febe6444 = DAT_febee410;
  DAT_febe6446 = DAT_febee412;
  DAT_febe6435 = DAT_febee401;
  DAT_febe6436 = DAT_febee402;
  DAT_febe6437 = DAT_febee403;
  DAT_febe6438 = DAT_febee404;
  DAT_febe6448 = DAT_febee414;
  DAT_febe6439 = DAT_febee405;
  DAT_febe644a = DAT_febee416;
  DAT_febe643a = DAT_febee406;
  DAT_febe644c = DAT_febee418;
  DAT_febe643b = DAT_febee407;
  return;
}



/* Copy current ECU acquisition/status into foreground-specific views;822C/8238 banks
   become6450/645C. Called in58B1A FFC0 window; does not overwrite CH2 copies622C/6238. */

void f33_snapshot_ecu_foreground_acquisition(void)

{
  DAT_febe6450 = DAT_febe822c;
  DAT_febe6452 = DAT_febe822e;
  DAT_febe6454 = DAT_febe8230;
  DAT_febe6456 = DAT_febe8232;
  DAT_febe6458 = DAT_febe8234;
  DAT_febe645a = DAT_febe8236;
  DAT_febe645c = DAT_febe8238;
  DAT_febe645e = DAT_febe823a;
  DAT_febe6460 = DAT_febe823c;
  DAT_febe6462 = DAT_febe823e;
  DAT_febe6464 = DAT_febe8240;
  DAT_febe6466 = DAT_febe8242;
  DAT_febe6600 = DAT_febe824c;
  DAT_febe6602 = DAT_febe824e;
  DAT_febe6604 = DAT_febe8250;
  DAT_febe6606 = DAT_febe8252;
  DAT_febe6608 = DAT_febe8254;
  DAT_febe660a = DAT_febe8256;
  DAT_febe65f8 = DAT_febe8244;
  DAT_febe65f9 = DAT_febe8245;
  DAT_febe65fa = DAT_febe8246;
  DAT_febe65fb = DAT_febe8247;
  DAT_febe65fc = DAT_febe8248;
  DAT_febe65fd = DAT_febe8249;
  DAT_febe65fe = DAT_febe824a;
  DAT_febe65ff = DAT_febe824b;
  DAT_febe660c = DAT_febe8258;
  DAT_febe660e = DAT_febe825a;
  DAT_febe6610 = DAT_febe825c;
  DAT_febe6612 = DAT_febe825e;
  DAT_febe64a2 = DAT_febe8b60;
  DAT_febe64a4 = DAT_febe8b62;
  DAT_febe64a6 = DAT_febe8b64;
  DAT_febe64a8 = DAT_febe8b66;
  DAT_febe64aa = DAT_febe8b68;
  DAT_febe64ac = DAT_febe8b6a;
  DAT_febe64ae = DAT_febe8b6c;
  DAT_febe64b0 = DAT_febe8b6e;
  DAT_febe64b2 = DAT_febe8b70;
  DAT_febe64b4 = DAT_febe8b72;
  DAT_febe64b6 = DAT_febe8b74;
  DAT_febe64b8 = DAT_febe8b76;
  DAT_febe64ba = DAT_febe8b78;
  DAT_febe64bc = DAT_febe8b7a;
  DAT_febe64be = DAT_febe8b7c;
  DAT_febe64c0 = DAT_febe8b7e;
  DAT_febe64c2 = DAT_febe8b80;
  DAT_febe64c4 = DAT_febe8b82;
  DAT_febe64a0 = DAT_febe8b5e;
  DAT_febe64a1 = DAT_febe8b5f;
  DAT_febe663c = DAT_febe7e2e;
  DAT_febe663e = DAT_febe7e30;
  DAT_febe6640 = DAT_febe7e32;
  DAT_febe6642 = DAT_febe7e34;
  DAT_febe6644 = DAT_febe7e36;
  DAT_febe6646 = DAT_febe7e38;
  DAT_febe6648 = DAT_febe7e3a;
  DAT_febe664a = DAT_febe7e3c;
  DAT_febe664c = DAT_febe7e3e;
  DAT_febe664e = DAT_febe7e40;
  DAT_febe6650 = DAT_febe7e42;
  DAT_febe6652 = DAT_febe7e44;
  DAT_febe6654 = DAT_febe7e46;
  DAT_febe6656 = DAT_febe7e48;
  DAT_febe6658 = DAT_febe7e4a;
  DAT_febe665a = DAT_febe7e4c;
  DAT_febe665c = DAT_febe7e4e;
  DAT_febe665e = DAT_febe7e50;
  DAT_febe662c = DAT_febe7e1c;
  DAT_febe662d = DAT_febe7e1d;
  DAT_febe662e = DAT_febe7e1e;
  DAT_febe662f = DAT_febe7e1f;
  DAT_febe6630 = DAT_febe7e20;
  DAT_febe6631 = DAT_febe7e21;
  DAT_febe6632 = DAT_febe7e22;
  DAT_febe6633 = DAT_febe7e23;
  DAT_febe6634 = DAT_febe7e24;
  DAT_febe6635 = DAT_febe7e25;
  DAT_febe6636 = DAT_febe7e26;
  DAT_febe6637 = DAT_febe7e27;
  DAT_febe6638 = DAT_febe7e28;
  DAT_febe6639 = DAT_febe7e29;
  DAT_febe663a = DAT_febe7e2a;
  DAT_febe663b = DAT_febe7e2b;
  DAT_febe6660 = DAT_febe7e54;
  DAT_febe6664 = DAT_febe7e58;
  DAT_febe6668 = DAT_febe7e5c;
  DAT_febe666c = DAT_febe7e60;
  DAT_febe6670 = DAT_febe7e64;
  DAT_febe6674 = DAT_febe7e68;
  DAT_febe6684 = DAT_febe7d74;
  DAT_febe6528 = f33_six_channel_fit_work.state;
  DAT_febe6688 = DAT_febe7d4a;
  DAT_febe668a = DAT_febe7d4c;
  DAT_febe668c = DAT_febe7d4e;
  DAT_febe668e = DAT_febe7d50;
  DAT_febe6690 = DAT_febe7d54;
  DAT_febe6692 = DAT_febe7d56;
  DAT_febe6694 = DAT_febe7d58;
  DAT_febe6696 = DAT_febe7d5a;
  DAT_febe6698 = DAT_febe7d5c;
  DAT_febe669a = DAT_febe7d60;
  DAT_febe669c = DAT_febe7d62;
  DAT_febe669e = DAT_febe7d66;
  DAT_febe66a0 = DAT_febe7d68;
  DAT_febe64e0 = DAT_febe5f34;
  DAT_febe64e2 = DAT_febe5f36;
  DAT_febe64e4 = DAT_febe5f38;
  DAT_febe64e8 = DAT_febe5f40;
  DAT_febe64ec = DAT_febe5f44;
  DAT_febe66a4 = DAT_febe7ea8;
  DAT_febe652a = f33_six_channel_fit_work.unsigned_max[0];
  DAT_febe66a6 = DAT_febe7eaa;
  DAT_febe652c = f33_six_channel_fit_work.unsigned_max[1];
  DAT_febe6570 = f33_six_channel_fit_work.second_center[5];
  DAT_febe652e = f33_six_channel_fit_work.unsigned_max[2];
  DAT_febe6572 = f33_six_channel_fit_work.component_angle[0];
  DAT_febe6530 = f33_six_channel_fit_work.unsigned_max[3];
  DAT_febe6532 = f33_six_channel_fit_work.unsigned_max[4];
  DAT_febe6574 = f33_six_channel_fit_work.component_angle[1];
  DAT_febe6534 = f33_six_channel_fit_work.unsigned_max[5];
  DAT_febe6576 = f33_six_channel_fit_work.component_angle[2];
  DAT_febe6536 = f33_six_channel_fit_work.unsigned_min[0];
  DAT_febe6538 = f33_six_channel_fit_work.unsigned_min[1];
  DAT_febe653a = f33_six_channel_fit_work.unsigned_min[2];
  DAT_febe653c = f33_six_channel_fit_work.unsigned_min[3];
  DAT_febe653e = f33_six_channel_fit_work.unsigned_min[4];
  DAT_febe6540 = f33_six_channel_fit_work.unsigned_min[5];
  DAT_febe6542 = f33_six_channel_fit_work.first_gain[0];
  DAT_febe6544 = f33_six_channel_fit_work.first_gain[1];
  DAT_febe6546 = f33_six_channel_fit_work.first_gain[2];
  DAT_febe6548 = f33_six_channel_fit_work.first_gain[3];
  DAT_febe654a = f33_six_channel_fit_work.first_gain[4];
  DAT_febe654c = f33_six_channel_fit_work.first_gain[5];
  DAT_febe654e = f33_six_channel_fit_work.first_center[0];
  DAT_febe6550 = f33_six_channel_fit_work.first_center[1];
  DAT_febe6552 = f33_six_channel_fit_work.first_center[2];
  DAT_febe6554 = f33_six_channel_fit_work.first_center[3];
  DAT_febe6556 = f33_six_channel_fit_work.first_center[4];
  DAT_febe6558 = f33_six_channel_fit_work.first_center[5];
  DAT_febe655a = f33_six_channel_fit_work.second_gain[0];
  DAT_febe655c = f33_six_channel_fit_work.second_gain[1];
  DAT_febe655e = f33_six_channel_fit_work.second_gain[2];
  DAT_febe6560 = f33_six_channel_fit_work.second_gain[3];
  DAT_febe6562 = f33_six_channel_fit_work.second_gain[4];
  DAT_febe6564 = f33_six_channel_fit_work.second_gain[5];
  DAT_febe6566 = f33_six_channel_fit_work.second_center[0];
  DAT_febe6568 = f33_six_channel_fit_work.second_center[1];
  DAT_febe656a = f33_six_channel_fit_work.second_center[2];
  DAT_febe656c = f33_six_channel_fit_work.second_center[3];
  DAT_febe656e = f33_six_channel_fit_work.second_center[4];
  DAT_febe66e6 = DAT_febe6e12;
  DAT_febe66e8 = DAT_febe6e14;
  DAT_febe66ea = DAT_febe6e16;
  DAT_febe66ec = DAT_febe6e18;
  DAT_febe66fc = DAT_febe6e28;
  DAT_febe6700 = DAT_febe6e2c;
  DAT_febe6704 = DAT_febe6e30;
  DAT_febe6708 = DAT_febe6e34;
  DAT_febe66ee = DAT_febe6e1a;
  DAT_febe66f0 = DAT_febe6e1c;
  DAT_febe66f2 = DAT_febe6e1e;
  DAT_febe66f4 = DAT_febe6e20;
  DAT_febe66f6 = DAT_febe6e22;
  DAT_febe66f8 = DAT_febe6e24;
  DAT_febe66e0 = DAT_febe6e0c;
  DAT_febe66e1 = DAT_febe6e0d;
  DAT_febe66e2 = DAT_febe6e0e;
  DAT_febe66e3 = DAT_febe6e0f;
  DAT_febe66e4 = DAT_febe6e10;
  DAT_febe66fa = DAT_febe6e26;
  DAT_febe6714 = DAT_febe6d78;
  DAT_febe670c = DAT_febe6d70;
  DAT_febe670e = DAT_febe6d72;
  DAT_febe6710 = DAT_febe6d74;
  DAT_febe6712 = DAT_febe6d76;
  DAT_febe6718 = DAT_febe6e00;
  DAT_febe671c = DAT_febe6d7c;
  DAT_febe671e = DAT_febe6d7e;
  DAT_febe6720 = DAT_febe6d80;
  DAT_febe6722 = DAT_febe6d82;
  DAT_febe6724 = DAT_febe6d84;
  DAT_febe6726 = DAT_febe6d86;
  DAT_febe65b0 = DAT_febe6c40;
  DAT_febe65b2 = DAT_febe6c42;
  DAT_febe65b4 = DAT_febe6c44;
  DAT_febe65b6 = DAT_febe6c46;
  DAT_febe65bc = DAT_febe6c60;
  DAT_febe65b8 = DAT_febe6c4a;
  return;
}



/* Cell-block copy: 39 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_5d5e0(void)

{
  DAT_febe6468 = DAT_febe81f4;
  DAT_febe646a = DAT_febe81f6;
  DAT_febe646c = DAT_febe81f8;
  DAT_febe646e = DAT_febe81fa;
  DAT_febe6470 = DAT_febe81fc;
  DAT_febe6472 = DAT_febe81fe;
  DAT_febe6474 = DAT_febe8200;
  DAT_febe6476 = DAT_febe8202;
  DAT_febe6478 = DAT_febe8204;
  DAT_febe647a = DAT_febe8206;
  DAT_febe647c = DAT_febe8208;
  DAT_febe647e = DAT_febe820a;
  DAT_febe64f0 = DAT_febe7dea;
  DAT_febe64f2 = DAT_febe7dec;
  DAT_febe64f4 = DAT_febe7dee;
  DAT_febe64f6 = DAT_febe7df0;
  DAT_febe64f8 = DAT_febe7df2;
  DAT_febe64fa = DAT_febe7df4;
  DAT_febe64fc = DAT_febe7df6;
  DAT_febe64fe = DAT_febe7df8;
  DAT_febe66a8 = DAT_febe7e0c;
  DAT_febe675c = DAT_febe7bfc;
  DAT_febe6770 = DAT_febee408;
  DAT_febe6772 = DAT_febee40a;
  DAT_febe6774 = DAT_febee40c;
  DAT_febe6776 = DAT_febee40e;
  DAT_febe6768 = DAT_febee400;
  DAT_febe6778 = DAT_febee410;
  DAT_febe677a = DAT_febee412;
  DAT_febe6769 = DAT_febee401;
  DAT_febe676a = DAT_febee402;
  DAT_febe676b = DAT_febee403;
  DAT_febe676c = DAT_febee404;
  DAT_febe677c = DAT_febee414;
  DAT_febe676d = DAT_febee405;
  DAT_febe677e = DAT_febee416;
  DAT_febe676e = DAT_febee406;
  DAT_febe6780 = DAT_febee418;
  DAT_febe676f = DAT_febee407;
  return;
}



/* Sequentially snapshot acquisition channels820C..8228, output/channel request state, conditioned
   scalars7DA4..7DB6, monitor statuses, live qualification71EC/limit71F2, scalar
   availability7BBC..7BC3 and application-record
   fields.66B8<-7DB0;66AE/B0<-7DA6/A8;6492/98<-821E/24. No local critical section makes the entire
   snapshot atomic. */

void f33_snapshot_monitor_inputs(void)

{
  DAT_febe6480 = DAT_febe820c;
  DAT_febe6482 = DAT_febe820e;
  DAT_febe6484 = DAT_febe8210;
  DAT_febe6486 = DAT_febe8212;
  DAT_febe6488 = DAT_febe8214;
  DAT_febe648a = DAT_febe8216;
  DAT_febe648c = DAT_febe8218;
  DAT_febe648e = DAT_febe821a;
  DAT_febe6490 = DAT_febe821c;
  DAT_febe6492 = DAT_febe821e;
  DAT_febe6494 = DAT_febe8220;
  DAT_febe6496 = DAT_febe8222;
  DAT_febe6498 = DAT_febe8224;
  DAT_febe649a = DAT_febe8226;
  DAT_febe649c = DAT_febe8228;
  DAT_febe6614 = DAT_febe8274;
  DAT_febe64cc = f33_output_request_status;
  DAT_febe64c8 = f33_output_phase_masks[0];
  DAT_febe64c9 = f33_output_phase_masks[1];
  DAT_febe6618 = DAT_febe8b18;
  DAT_febe64d4 = DAT_febe8ae4;
  DAT_febe64d0 = DAT_febe8ac8;
  DAT_febe64d1 = DAT_febe8acb;
  DAT_febe661c = DAT_febe8af0;
  DAT_febe64dc = f33_channel_request_state.observed_mismatch;
  DAT_febe64d8 = f33_channel_request_state.channel0_state;
  DAT_febe64d9 = f33_channel_request_state.channel1_state;
  DAT_febe6620 = DAT_febe8aa4;
  DAT_febe6624 = DAT_febe8a44;
  DAT_febe6628 = DAT_febe8a64;
  DAT_febe6678 = DAT_febe7e9c;
  DAT_febe667a = DAT_febe7e9e;
  DAT_febe667c = DAT_febe7ea0;
  DAT_febe667e = DAT_febe7ea2;
  DAT_febe6680 = DAT_febe7ea4;
  DAT_febe6682 = DAT_febe7ea6;
  DAT_febe66ae = DAT_febe7da6;
  DAT_febe66b0 = DAT_febe7da8;
  DAT_febe66b2 = DAT_febe7daa;
  DAT_febe66b4 = DAT_febe7dac;
  DAT_febe66b6 = DAT_febe7dae;
  DAT_febe66b8 = DAT_febe7db0;
  DAT_febe66ba = DAT_febe7db2;
  DAT_febe66ac = DAT_febe7da4;
  DAT_febe66bc = DAT_febe7db4;
  DAT_febe66be = DAT_febe7db6;
  DAT_febe65c0 = DAT_febe74a8;
  DAT_febe65c1 = DAT_febe74a9;
  DAT_febe65c2 = DAT_febe74aa;
  DAT_febe65c3 = DAT_febe74ab;
  DAT_febe65c4 = DAT_febe74ac;
  DAT_febe65c5 = DAT_febe74ad;
  DAT_febe6728 = DAT_febe7818;
  DAT_febe6729 = DAT_febe7819;
  DAT_febe672a = DAT_febe781a;
  DAT_febe672b = DAT_febe781b;
  DAT_febe672c = DAT_febe781c;
  DAT_febe672d = DAT_febe781d;
  DAT_febe672e = DAT_febe781e;
  DAT_febe672f = DAT_febe781f;
  DAT_febe6730 = DAT_febe7820;
  DAT_febe6731 = DAT_febe7821;
  DAT_febe6732 = DAT_febe7822;
  DAT_febe6733 = DAT_febe7823;
  DAT_febe6734 = DAT_febe7824;
  DAT_febe6736 = DAT_febe7826;
  DAT_febe6735 = DAT_febe7825;
  DAT_febe6737 = DAT_febe7827;
  DAT_febe6738 = DAT_febe7828;
  DAT_febe673c = DAT_febe7928;
  DAT_febe673d = DAT_febe7929;
  DAT_febe673e = DAT_febe792a;
  DAT_febe673f = DAT_febe792b;
  DAT_febe6740 = DAT_febe792c;
  DAT_febe6741 = DAT_febe792d;
  DAT_febe6742 = DAT_febe792e;
  DAT_febe6743 = DAT_febe792f;
  DAT_febe6744 = DAT_febe7930;
  DAT_febe6745 = DAT_febe7931;
  DAT_febe6746 = DAT_febe7932;
  DAT_febe6747 = DAT_febe7933;
  DAT_febe6748 = DAT_febe7934;
  DAT_febe674a = DAT_febe7936;
  DAT_febe6749 = DAT_febe7935;
  DAT_febe674b = DAT_febe7937;
  DAT_febe674c = DAT_febe7938;
  DAT_febe6750 = f33_shared_condition_status[0];
  DAT_febe6751 = f33_shared_condition_status[1];
  DAT_febe6752 = f33_shared_condition_status[2];
  DAT_febe6753 = f33_shared_condition_status[3];
  DAT_febe6754 = f33_shared_condition_status[4];
  DAT_febe6755 = f33_shared_condition_status[5];
  DAT_febe6756 = f33_shared_condition_status[6];
  DAT_febe6757 = f33_shared_condition_status[7];
  DAT_febe6759 = DAT_febe79e5;
  DAT_febe6758 = f33_shared_condition_status[8];
  DAT_febe65c8 = f33_paired_source_monitor_status[0];
  DAT_febe65c9 = f33_paired_source_monitor_status[1];
  DAT_febe65ca = f33_paired_source_monitor_status[2];
  DAT_febe65cb = f33_paired_source_monitor_status[3];
  DAT_febe65cc = f33_paired_source_monitor_status[4];
  DAT_febe65cd = f33_paired_source_monitor_status[5];
  DAT_febe65ce = f33_paired_source_monitor_status[6];
  DAT_febe65cf = f33_paired_source_monitor_status[7];
  DAT_febe65d0 = f33_paired_source_monitor_status[8];
  DAT_febe65d1 = f33_paired_source_monitor_status[9];
  DAT_febe65d2 = DAT_febe7566;
  DAT_febe65d3 = DAT_febe7567;
  DAT_febe65d4 = DAT_febe7568;
  DAT_febe65d7 = DAT_febe7575;
  DAT_febe65d5 = DAT_febe7569;
  DAT_febe65d6 = DAT_febe7574;
  DAT_febe65dc = DAT_febe7578;
  DAT_febe65d8 = DAT_febe7576;
  DAT_febe65e0 = f33_shared_snapshot_status[0];
  DAT_febe65e1 = f33_shared_snapshot_status[1];
  DAT_febe65e2 = f33_shared_snapshot_status[2];
  DAT_febe65e3 = f33_shared_snapshot_status[3];
  DAT_febe65e4 = f33_shared_snapshot_status[4];
  DAT_febe65e5 = f33_shared_snapshot_status[5];
  DAT_febe65e6 = f33_shared_snapshot_status[6];
  DAT_febe65e7 = f33_shared_snapshot_status[7];
  DAT_febe65e8 = f33_shared_snapshot_status[8];
  DAT_febe65e9 = f33_shared_snapshot_status[9];
  DAT_febe65eb = DAT_febe7cb7;
  DAT_febe65ea = f33_shared_snapshot_status[10];
  DAT_febe65ec = DAT_febe7cb8;
  DAT_febe65ed = DAT_febe7cc4;
  DAT_febe65ee = DAT_febe7cc5;
  DAT_febe6760 = DAT_febe686c;
  DAT_febe6762 = DAT_febe6870;
  DAT_febe6764 = DAT_febe71ec;
  DAT_febe6766 = DAT_febe71f2;
  DAT_febe65f0 = DAT_febe7bbc;
  DAT_febe65f1 = DAT_febe7bbd;
  DAT_febe65f2 = DAT_febe7bbe;
  DAT_febe65f3 = DAT_febe7bbf;
  DAT_febe65f4 = DAT_febe7bc0;
  DAT_febe65f5 = DAT_febe7bc1;
  DAT_febe65f6 = DAT_febe7bc2;
  DAT_febe65f7 = DAT_febe7bc3;
  DAT_febe6502 = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[0];
  DAT_febe6504 = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[1];
  DAT_febe6506 = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[2];
  DAT_febe6508 = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[3];
  DAT_febe650a = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[4];
  DAT_febe650c = f33_monitor_current_active_calibration.coefficients.negative_residual_gain[5];
  DAT_febe650e = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0];
  DAT_febe6510 = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1];
  DAT_febe6512 = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2];
  DAT_febe6514 = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3];
  DAT_febe6516 = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4];
  DAT_febe6518 = f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5];
  DAT_febe651a = f33_monitor_current_active_calibration.coefficients.bias[0];
  DAT_febe651c = f33_monitor_current_active_calibration.coefficients.bias[1];
  DAT_febe651e = f33_monitor_current_active_calibration.coefficients.bias[2];
  DAT_febe6520 = f33_monitor_current_active_calibration.coefficients.bias[3];
  DAT_febe6522 = f33_monitor_current_active_calibration.coefficients.bias[4];
  DAT_febe6500 = f33_monitor_current_active_calibration.changed;
  DAT_febe6524 = f33_monitor_current_active_calibration.coefficients.bias[5];
  DAT_febe6501 = f33_monitor_current_active_calibration.range_error;
  DAT_febe657a = f33_published_fit_coefficients.first_center[0];
  DAT_febe657c = f33_published_fit_coefficients.first_center[1];
  DAT_febe657e = f33_published_fit_coefficients.first_center[2];
  DAT_febe6580 = f33_published_fit_coefficients.first_center[3];
  DAT_febe6582 = f33_published_fit_coefficients.first_center[4];
  DAT_febe6584 = f33_published_fit_coefficients.first_center[5];
  DAT_febe6586 = f33_published_fit_coefficients.first_gain[0];
  DAT_febe6588 = f33_published_fit_coefficients.first_gain[1];
  DAT_febe658a = f33_published_fit_coefficients.first_gain[2];
  DAT_febe658c = f33_published_fit_coefficients.first_gain[3];
  DAT_febe658e = f33_published_fit_coefficients.first_gain[4];
  DAT_febe6590 = f33_published_fit_coefficients.first_gain[5];
  DAT_febe6592 = f33_published_fit_coefficients.second_center[0];
  DAT_febe6594 = f33_published_fit_coefficients.second_center[1];
  DAT_febe6596 = f33_published_fit_coefficients.second_center[2];
  DAT_febe6598 = f33_published_fit_coefficients.second_center[3];
  DAT_febe659a = f33_published_fit_coefficients.second_center[4];
  DAT_febe659c = f33_published_fit_coefficients.second_center[5];
  DAT_febe659e = f33_published_fit_coefficients.second_gain[0];
  DAT_febe65a0 = f33_published_fit_coefficients.second_gain[1];
  DAT_febe65a2 = f33_published_fit_coefficients.second_gain[2];
  DAT_febe65a4 = f33_published_fit_coefficients.second_gain[3];
  DAT_febe65a6 = f33_published_fit_coefficients.second_gain[4];
  DAT_febe65a8 = f33_published_fit_coefficients.second_gain[5];
  DAT_febe65aa = f33_published_fit_coefficients.component_angle[0];
  DAT_febe65ac = f33_published_fit_coefficients.component_angle[1];
  DAT_febe65ae = f33_published_fit_coefficients.component_angle[2];
  DAT_febe6578 = DAT_febe6a24;
  DAT_febe6579 = DAT_febe6a25;
  DAT_febe66c8 = DAT_febe689a;
  DAT_febe66ca = DAT_febe689c;
  DAT_febe66cc = DAT_febe689e;
  DAT_febe66ce = DAT_febe68a0;
  DAT_febe66d0 = DAT_febe68a2;
  DAT_febe66c0 = DAT_febe6891;
  DAT_febe66c1 = DAT_febe6892;
  DAT_febe66c2 = DAT_febe6893;
  DAT_febe66c3 = DAT_febe6894;
  DAT_febe66c4 = DAT_febe6895;
  DAT_febe66c5 = DAT_febe6896;
  DAT_febe66c6 = DAT_febe6897;
  DAT_febe66c7 = DAT_febe6898;
  DAT_febe66d6 = DAT_febe6ad2;
  DAT_febe66d8 = DAT_febe6ad4;
  DAT_febe66da = DAT_febe6ad6;
  DAT_febe66dc = DAT_febe6ad8;
  DAT_febe66d4 = DAT_febe6ad0;
  DAT_febe66d5 = DAT_febe6ad1;
  DAT_febe678c = DAT_febee608;
  DAT_febe6784 = DAT_febee600;
  DAT_febe6794 = DAT_febee610;
  DAT_febe6785 = DAT_febee601;
  DAT_febe6786 = DAT_febee602;
  DAT_febe6787 = DAT_febee603;
  DAT_febe678e = DAT_febee60a;
  DAT_febe6788 = DAT_febee604;
  DAT_febe6789 = DAT_febee605;
  DAT_febe678a = DAT_febee606;
  DAT_febe6790 = DAT_febee60c;
  return;
}



void FUN_0005dc7e(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  if (0xff < param_2) {
    uVar1 = param_1 & 1;
    if (param_3 < 0x100) {
      FUN_00056684();
      if (uVar1 != 0) {
        FUN_0005668a();
      }
      FUN_000566f0();
      if (uVar1 != 0) {
        FUN_000566fa();
      }
      f33_return_only_stub_50b68();
      if (uVar1 != 0) {
        f33_copy_acquisition_banks_to_application();
      }
      f33_return_only_stub_50bba();
      if (uVar1 != 0) goto LAB_0005dcda;
    }
    else if (uVar1 != 0) {
      FUN_0005668a();
      FUN_000566fa();
      f33_copy_acquisition_banks_to_application();
LAB_0005dcda:
      f33_copy_serial_acquisition_to_application();
    }
  }
  if (0x100 < param_2) {
    uVar1 = param_1 & 1;
    if (param_3 < 0x101) {
      f33_fill_constant_block_486aa();
      if (uVar1 != 0) {
        f33_condition_measured_phase_currents();
      }
      thunk_FUN_00047d78();
      if (uVar1 != 0) {
        f33_update_electrical_angle_feedback();
      }
      FUN_00047d34();
      if (uVar1 != 0) {
        FUN_00047d3a();
      }
      f33_fill_constant_block_47b3c();
      if (uVar1 != 0) {
        FUN_00047b70();
      }
      f33_fill_constant_block_47ea4();
      if (uVar1 != 0) {
        FUN_00047eb8();
      }
      FUN_0004963e();
      if (uVar1 != 0) goto LAB_0005dd4c;
    }
    else if (uVar1 != 0) {
      f33_condition_measured_phase_currents();
      f33_update_electrical_angle_feedback();
      FUN_00047d3a();
      FUN_00047b70();
      FUN_00047eb8();
LAB_0005dd4c:
      FUN_0004964c();
    }
  }
  if (param_2 - 0x200 < 0x323) {
    uVar1 = param_1 & 1;
    if (param_3 - 0x200 < 0x323) {
      if (uVar1 != 0) {
        f33_accumulate_paired_source_difference_counts();
        f33_step_channel_difference_latch_a();
LAB_0005dd96:
        f33_step_channel_difference_latch_b();
      }
    }
    else {
      FUN_0003e0b4();
      if (uVar1 != 0) {
        f33_accumulate_paired_source_difference_counts();
      }
      f33_fill_constant_block_4246e();
      if (uVar1 != 0) {
        f33_step_channel_difference_latch_a();
      }
      f33_fill_constant_block_43430();
      if (uVar1 != 0) goto LAB_0005dd96;
    }
  }
  if (param_2 == 0x512) {
    if (param_3 != 0x512) {
      f33_return_only_stub_32d24();
    }
    if ((param_1 & 1) != 0) {
      f33_step_six_channel_fit();
    }
  }
  if (param_2 == 0x600) {
    uVar1 = param_1 & 1;
    if (param_3 == 0x600) {
      if (uVar1 == 0) goto LAB_0005dde6;
      f33_step_mode600_stimulus_fit();
    }
    else {
      f33_initialize_mode600_stimulus_fit();
      if (uVar1 != 0) {
        f33_step_mode600_stimulus_fit();
      }
      f33_return_only_stub_32d24();
      if (uVar1 == 0) goto LAB_0005dde6;
    }
    f33_step_six_channel_fit();
  }
LAB_0005dde6:
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      f33_initialize_terminal_output_ramp();
    }
    if ((param_1 & 1) != 0) {
      f33_step_terminal_output_ramp();
    }
  }
  return;
}



/* Current mode>=0200 runs entry resets when prior mode<0200; workmask bit0 gates measured
   transform, envelope qualification and paired feedback steps. Mode>=0101 separately
   initializes/reduces output-code requests. Always publish57FD2 snapshot. Distinct generation from
   bit1 current-control composition. */

void f33_update_mode_owned_current_feedback(uint workmask,ushort mode,ushort previous_mode)

{
  uint uVar1;
  
  if (0x1ff < mode) {
    uVar1 = workmask & 1;
    if (previous_mode < 0x200) {
      f33_return_only_stub_36142();
      if (uVar1 != 0) {
        f33_transform_measured_phase_currents();
      }
      f33_return_only_stub_38faa();
      if (uVar1 != 0) {
        f33_refresh_current_reference_envelope_qualification();
      }
      f33_initialize_bank0_current_reference_feedback();
      if (uVar1 != 0) {
        f33_update_bank0_current_reference_feedback();
      }
      f33_initialize_bank1_current_reference_feedback();
      if (uVar1 == 0) goto LAB_0005de62;
    }
    else {
      if (uVar1 == 0) goto LAB_0005de62;
      f33_transform_measured_phase_currents();
      f33_refresh_current_reference_envelope_qualification();
      f33_update_bank0_current_reference_feedback();
    }
    f33_update_bank1_current_reference_feedback();
  }
LAB_0005de62:
  if (0x100 < mode) {
    if (previous_mode < 0x101) {
      f33_initialize_output_code_limit_requests();
    }
    if ((workmask & 1) != 0) {
      f33_reduce_phase_output_code_limits();
    }
  }
  f33_publish_current_control_snapshot();
  return;
}



void FUN_0005de82(uint param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if ((0xff < param_2) && ((param_1 & 1) != 0)) {
    FUN_0005668a();
    FUN_000566fa();
    f33_copy_acquisition_banks_to_application();
    f33_copy_serial_acquisition_to_application();
  }
  if ((0x100 < param_2) && ((param_1 & 1) != 0)) {
    f33_condition_measured_phase_currents();
    f33_update_electrical_angle_feedback();
    FUN_00047d3a();
    FUN_00047b70();
    FUN_00047eb8();
    FUN_0004964c();
  }
  if ((param_2 - 0x200 < 0x323) && ((param_1 & 1) != 0)) {
    f33_accumulate_paired_source_difference_counts();
    f33_step_channel_difference_latch_a();
    f33_step_channel_difference_latch_b();
  }
  if ((param_2 == 0x512) && ((param_1 & 1) != 0)) {
    f33_step_six_channel_fit();
  }
  if ((param_2 == 0x600) && ((param_1 & 1) != 0)) {
    f33_step_mode600_stimulus_fit();
    f33_step_six_channel_fit();
  }
  if ((0x1ff < param_2) && ((param_1 & 1) != 0)) {
    f33_step_terminal_output_ramp();
  }
  return;
}



/* With workmask bit0 and mode>=0200, transform measured currents, update envelope qualifier, then
   bank0 and bank1 feedback. Mode>=0101 independently gates code-limit reduction. Always
   publish57FD2 diagnostic snapshot. Does not itself execute387CE consumer staging or current
   regulation. */

void f33_update_steady_current_feedback(uint workmask,ushort mode)

{
  if ((0x1ff < mode) && ((workmask & 1) != 0)) {
    f33_transform_measured_phase_currents();
    f33_refresh_current_reference_envelope_qualification();
    f33_update_bank0_current_reference_feedback();
    f33_update_bank1_current_reference_feedback();
  }
  if ((0x100 < mode) && ((workmask & 1) != 0)) {
    f33_reduce_phase_output_code_limits();
  }
  f33_publish_current_control_snapshot();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5df5a(void)

{
  return;
}



void FUN_0005df5c(uint param_1,ushort param_2,ushort param_3)

{
  uint uVar1;
  
  if (0x1ff < param_2) {
    uVar1 = param_1 & 2;
    if (param_3 < 0x200) {
      f33_return_only_stub_387cc();
      if (uVar1 != 0) {
        f33_latch_current_feedback_and_reference_inputs();
      }
      f33_return_only_stub_387b8();
      if (uVar1 != 0) {
        FUN_000387ba();
      }
      FUN_0003798c();
      if (uVar1 != 0) {
        FUN_00037a92();
      }
      f33_return_only_stub_37e46();
      if (uVar1 != 0) {
        f33_compose_current_feedback();
      }
      f33_return_only_stub_38676();
      if (uVar1 != 0) {
        FUN_0003879e();
      }
      f33_return_only_stub_38500();
      if (uVar1 != 0) {
        f33_map_sampled_command_to_base_first_current();
      }
      f33_return_only_stub_37f90();
      if (uVar1 != 0) {
        f33_select_feedback_bounded_first_current_request();
      }
      f33_return_only_stub_38580();
      if (uVar1 != 0) {
        f33_update_additional_first_current_request();
      }
      f33_return_only_stub_3835c();
      if (uVar1 != 0) {
        f33_select_actual_and_feedback_first_current_baselines();
      }
      f33_return_only_stub_38394();
      if (uVar1 != 0) {
        FUN_000384d8();
      }
      f33_return_only_stub_38160();
      if (uVar1 != 0) {
        f33_calculate_sixfold_current_correction();
      }
      f33_return_only_stub_37f14();
      if (uVar1 != 0) {
        f33_publish_corrected_current_reference_pairs();
      }
      FUN_00038a4c();
      if (uVar1 != 0) {
        FUN_00038a58();
      }
      FUN_00038b5e();
      if (uVar1 != 0) {
        FUN_00038b6a();
      }
      f33_fill_constant_block_37218();
      if (uVar1 != 0) {
        FUN_00037228();
      }
      f33_fill_constant_block_370d6();
      if (uVar1 != 0) {
        FUN_000370e6();
      }
      f33_fill_constant_block_3759c();
      if (uVar1 != 0) {
        FUN_0003777e();
      }
      f33_fill_constant_block_373be();
      if (uVar1 != 0) {
        FUN_00037538();
      }
      FUN_00036910();
      if (uVar1 != 0) {
        f33_compose_regulator_output_bank0();
      }
      FUN_00036c1c();
      if (uVar1 != 0) {
        f33_compose_regulator_output_bank1();
      }
      f33_return_only_stub_377ec();
      if (uVar1 != 0) {
        f33_refresh_shared_second_axis_envelope();
      }
      f33_return_only_stub_378d2();
      if (uVar1 != 0) {
        f33_apply_shared_second_axis_envelope();
      }
      f33_return_only_stub_36f24();
      if (uVar1 != 0) {
        FUN_00036f26();
      }
      FUN_00038c70();
      if (uVar1 != 0) {
        f33_transform_first_regulated_phase_commands();
      }
      FUN_00038d60();
      if (uVar1 != 0) {
        f33_transform_second_regulated_phase_commands();
      }
      f33_return_only_stub_37c4a();
      if (uVar1 != 0) {
        f33_select_phase_modulation_modes();
      }
      FUN_000368aa();
      if (uVar1 != 0) {
        f33_map_phase_compensation_gain();
      }
      f33_return_only_stub_36676();
      if (uVar1 != 0) {
        f33_refresh_phase_compensation_amplitude();
      }
      f33_return_only_stub_3674e();
      if (uVar1 != 0) {
        f33_compensate_first_regulated_phases();
      }
      f33_return_only_stub_367fc();
      if (uVar1 != 0) {
        f33_compensate_second_regulated_phases();
      }
      FUN_00038838();
      if (uVar1 != 0) {
        f33_modulate_first_phase_triplet();
      }
      FUN_00038942();
      if (uVar1 != 0) {
        f33_modulate_second_phase_triplet();
      }
      f33_return_only_stub_38e50();
LAB_0005e1ae:
      if (uVar1 != 0) {
        f33_publish_current_output_slot();
      }
    }
    else if (uVar1 != 0) {
      f33_latch_current_feedback_and_reference_inputs();
      FUN_000387ba();
      FUN_00037a92();
      f33_compose_current_feedback();
      FUN_0003879e();
      f33_map_sampled_command_to_base_first_current();
      f33_select_feedback_bounded_first_current_request();
      f33_update_additional_first_current_request();
      if (uVar1 != 0) {
        f33_select_actual_and_feedback_first_current_baselines();
        FUN_000384d8();
        f33_calculate_sixfold_current_correction();
        f33_publish_corrected_current_reference_pairs();
        FUN_00038a58();
        FUN_00038b6a();
        if (uVar1 != 0) {
          FUN_00037228();
          FUN_000370e6();
          FUN_0003777e();
          FUN_00037538();
          f33_compose_regulator_output_bank0();
          f33_compose_regulator_output_bank1();
          if (uVar1 != 0) {
            f33_refresh_shared_second_axis_envelope();
            f33_apply_shared_second_axis_envelope();
            FUN_00036f26();
            f33_transform_first_regulated_phase_commands();
            if (uVar1 != 0) {
              f33_transform_second_regulated_phase_commands();
              f33_select_phase_modulation_modes();
              f33_map_phase_compensation_gain();
              f33_refresh_phase_compensation_amplitude();
              f33_compensate_first_regulated_phases();
              f33_compensate_second_regulated_phases();
              f33_modulate_first_phase_triplet();
              f33_modulate_second_phase_triplet();
            }
            goto LAB_0005e1ae;
          }
        }
      }
    }
  }
  if (0x100 < param_2) {
    param_1 = param_1 & 2;
    if (param_3 < 0x101) {
      f33_initialize_phase_output_slots();
      if (param_1 != 0) {
        f33_select_phase_output_slots();
      }
      f33_fill_constant_block_5745a();
      if (param_1 != 0) {
        f33_stage_phase_output_history();
      }
      f33_return_only_stub_57dee();
      if (param_1 == 0) goto LAB_0005e1f8;
    }
    else {
      if (param_1 == 0) goto LAB_0005e1f8;
      f33_select_phase_output_slots();
      f33_stage_phase_output_history();
    }
    f33_stage_live_phase_halfword_compares();
  }
LAB_0005e1f8:
  f33_publish_current_control_snapshot();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5e200(void)

{
  return;
}



/* With workmask bit1, state>=0200 runs current conversion, feedback regulation, limiting,
   transforms and slot0 publication. Independently state>=0101 runs arbitration/history and compare
   staging, so0101..01FF can stage existing values without recomputing control.57FD2 always
   publishes snapshots. Software compare staging is separate from acquisition and hardware commit.
   Separate compute/staging gates and unconditional snapshot. Existing full-root regulation proofs
   remain. New native nonzero tail5E280 exercises5A/A5 modulation and competing slots4/3;
   full5E202(2,0101) stages retained control with slot1 clamp exemption. Acquisition, upstream
   nonzero regulation, interrupt interleavings and physical commit remain separate boundaries. */

void f33_run_current_control_and_stage_output(uint workmask,ushort state)

{
  uint uVar1;
  
  if ((0x1ff < state) && (uVar1 = workmask & 2, uVar1 != 0)) {
    f33_latch_current_feedback_and_reference_inputs();
    FUN_000387ba();
    FUN_00037a92();
    f33_compose_current_feedback();
    FUN_0003879e();
    f33_map_sampled_command_to_base_first_current();
    f33_select_feedback_bounded_first_current_request();
    f33_update_additional_first_current_request();
    if (uVar1 != 0) {
      f33_select_actual_and_feedback_first_current_baselines();
      FUN_000384d8();
      f33_calculate_sixfold_current_correction();
      f33_publish_corrected_current_reference_pairs();
      FUN_00038a58();
      FUN_00038b6a();
      if (uVar1 != 0) {
        FUN_00037228();
        FUN_000370e6();
        FUN_0003777e();
        FUN_00037538();
        f33_compose_regulator_output_bank0();
        f33_compose_regulator_output_bank1();
        if (uVar1 != 0) {
          f33_refresh_shared_second_axis_envelope();
          f33_apply_shared_second_axis_envelope();
          FUN_00036f26();
          f33_transform_first_regulated_phase_commands();
          if (uVar1 != 0) {
            f33_transform_second_regulated_phase_commands();
            f33_select_phase_modulation_modes();
            f33_map_phase_compensation_gain();
            f33_refresh_phase_compensation_amplitude();
            f33_compensate_first_regulated_phases();
            f33_compensate_second_regulated_phases();
            f33_modulate_first_phase_triplet();
            f33_modulate_second_phase_triplet();
            f33_publish_current_output_slot();
          }
        }
      }
    }
  }
  if ((0x100 < state) && ((workmask >> 1 & 1) != 0)) {
    f33_select_phase_output_slots();
    f33_stage_phase_output_history();
    f33_stage_live_phase_halfword_compares();
  }
  f33_publish_current_control_snapshot();
  return;
}



void FUN_0005e2da(undefined4 param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      FUN_000566d6();
      FUN_000566dc();
      f33_return_only_stub_50afe();
      f33_fill_constant_block_50b00();
      f33_return_only_stub_50a50();
    }
    else {
      FUN_000566dc();
      f33_fill_constant_block_50b00();
    }
    FUN_00050ae2();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      f33_fill_constant_block_4843c();
    }
    f33_decode_torque_sensor_channels();
  }
  if (param_2 - 0x301 < 0x222) {
    if (param_3 - 0x301 < 0x222) {
      f33_return_only_stub_4606e();
      FUN_0004663c();
    }
    else {
      f33_return_only_stub_4606c();
      f33_return_only_stub_4606e();
      FUN_0004661e();
      FUN_0004663c();
      FUN_000467d0();
    }
    FUN_000467ee();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      FUN_0004867e();
    }
    f33_publish_selected_torque_feedback();
  }
  if (param_2 == 0x600) {
    if (param_3 != 0x600) {
      FUN_00034c48();
    }
    f33_select_mode600_stimulus_request();
  }
  f33_fill_constant_block_5802e();
  return;
}



void FUN_0005e38e(undefined4 param_1,ushort param_2,ushort param_3)

{
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      f33_return_only_stub_35c4a();
    }
    f33_sample_motor_command();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      f33_return_only_stub_53ffa();
    }
    f33_return_only_stub_53ffc();
  }
  f33_fill_constant_block_5802e();
  return;
}



void FUN_0005e3ca(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    FUN_000566dc();
    f33_fill_constant_block_50b00();
    FUN_00050ae2();
  }
  if (0x100 < param_2) {
    f33_decode_torque_sensor_channels();
  }
  if (param_2 - 0x301 < 0x222) {
    f33_return_only_stub_4606e();
    FUN_0004663c();
    FUN_000467ee();
  }
  if (0x100 < param_2) {
    f33_publish_selected_torque_feedback();
  }
  if (param_2 == 0x600) {
    f33_select_mode600_stimulus_request();
  }
  f33_fill_constant_block_5802e();
  return;
}



void FUN_0005e420(undefined4 param_1,ushort param_2)

{
  if (param_2 < 0x200) {
    if (param_2 < 0x102) goto LAB_0005e43c;
  }
  else {
    f33_sample_motor_command();
  }
  f33_return_only_stub_53ffc();
LAB_0005e43c:
  f33_fill_constant_block_5802e();
  return;
}



/* Low16 current modeR7/prior modeR8 control entry initialization and monitor groups. For
   current>100h condition current planes before monitor consumers; for current>102h adopt active
   calibration only after fault aggregation. Thus this invocation uses the prior active-calibration
   generation. Mode600 sampling and later owner9 budgets are separate branches; no task-period
   claim. */

void f33_step_transitioned_channel_monitor_slice
               (uint unused_r6,ushort current_mode,ushort previous_mode)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)previous_mode;
  uVar1 = (uint)current_mode;
  if (0xff < uVar1) {
    if (uVar2 < 0x100) {
      FUN_00056722();
      FUN_0005672c();
      FUN_000566a2();
      FUN_000566ac();
      f33_return_only_stub_50b24();
      f33_copy_cell_block_50b26();
      f33_return_only_stub_50a04();
      f33_snapshot_acquisition_status_flags();
      f33_return_only_stub_50a1a();
    }
    else {
      FUN_0005672c();
      FUN_000566ac();
      f33_copy_cell_block_50b26();
      f33_snapshot_acquisition_status_flags();
    }
    f33_snapshot_acquisition_range_fields();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      FUN_00048d32();
      f33_condition_monitor_current_planes();
      f33_fill_constant_block_495a4();
    }
    else {
      f33_condition_monitor_current_planes();
    }
    FUN_000495b6();
  }
  if (0xff < uVar1) {
    if (uVar2 < 0x100) {
      FUN_00047f98();
    }
    FUN_00048230();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      f33_fill_constant_block_45bb2();
    }
    f33_update_scalar_availability();
  }
  if (0x102 < uVar1) {
    if (uVar1 < 0x523) {
      if (uVar2 - 0x103 < 0x420) {
        f33_step_acquisition_status_a_monitor();
        f33_step_acquisition_status_b_monitor();
        f33_step_acquisition_range_a_monitor();
        f33_step_acquisition_range_b_monitor();
      }
      else {
        f33_reset_scalar_monitor_3bab2_3baa2();
        f33_step_acquisition_status_a_monitor();
        f33_reset_scalar_monitor_3bb44_3bb34();
        f33_step_acquisition_status_b_monitor();
        f33_reset_scalar_monitor_3bc4c_3bc3c();
        f33_step_acquisition_range_a_monitor();
        f33_reset_scalar_monitor_3bcfc_3bcec();
        f33_step_acquisition_range_b_monitor();
        f33_return_only_stub_3bbb8();
      }
      f33_publish_acquisition_monitor_actions();
    }
    if (uVar2 < 0x103) {
      f33_return_only_stub_3d6d0();
    }
    f33_compose_local_status_fault_actions();
  }
  if (uVar1 - 0x200 < 0x323) {
    if (uVar2 - 0x200 < 0x323) {
      FUN_0004523e();
      f33_step_paired_source_counter_monitor_a();
      f33_step_paired_source_counter_monitor_b();
      f33_step_paired_source_mask_monitor_a();
      f33_step_paired_source_mask_monitor_b();
      f33_publish_paired_source_difference_changes();
      f33_step_paired_source_difference_monitors_a();
      f33_step_paired_source_difference_monitors_b();
      f33_publish_paired_source_monitor_actions();
      FUN_000423bc();
      if (uVar1 - 0x20c < 0x317) {
        if (0x316 < uVar2 - 0x20c) {
          FUN_00041e6c();
        }
        FUN_00041e96();
      }
      f33_step_channel_phase_monitors_a();
      FUN_00042caa();
      FUN_00042b94();
      FUN_00042030();
      FUN_0004218a();
      f33_publish_channel_monitor_actions_a();
      FUN_0004337a();
      if (uVar1 - 0x20c < 0x317) {
        if (0x316 < uVar2 - 0x20c) {
          FUN_00042e2a();
        }
        FUN_00042e54();
      }
      f33_step_channel_phase_monitors_b();
      FUN_00043c6e();
      FUN_00043b56();
      FUN_00042fee();
      FUN_00043148();
      f33_publish_channel_monitor_actions_b();
      if (uVar1 - 0x301 < 0x222) {
        if (0x221 < uVar2 - 0x301) {
          f33_fill_constant_block_43dc6();
        }
        FUN_00043f1a();
      }
      FUN_0004441c();
      if (uVar1 - 0x20b < 0x318) {
        if (uVar2 - 0x20b < 0x318) {
          FUN_0004460c();
        }
        else {
          f33_reset_latched_monitor_febe79ac_445fc();
          FUN_0004460c();
          f33_reset_latched_monitor_febe79b8_446aa();
        }
        FUN_000446ba();
      }
      FUN_000440bc();
      FUN_0004426c();
      FUN_00044768();
      FUN_00044856();
      FUN_00043f58();
      FUN_0004400a();
      f33_publish_shared_condition_monitor_actions();
      f33_publish_local_channel_monitor_actions_a();
    }
    else {
      f33_return_only_stub_44ecc();
      FUN_0004523e();
      FUN_0003dd82();
      f33_step_paired_source_counter_monitor_a();
      FUN_0003df22();
      f33_step_paired_source_counter_monitor_b();
      f33_reset_windowed_monitor_febe757c_3e3ea();
      f33_step_paired_source_mask_monitor_a();
      f33_reset_windowed_monitor_febe758c_3e4bc();
      f33_step_paired_source_mask_monitor_b();
      f33_fill_constant_block_3e1da();
      f33_publish_paired_source_difference_changes();
      FUN_0003da72();
      f33_step_paired_source_difference_monitors_a();
      FUN_0003dbfe();
      f33_step_paired_source_difference_monitors_b();
      f33_return_only_stub_3e22e();
      f33_publish_paired_source_monitor_actions();
      FUN_000423b6();
      FUN_000423bc();
      FUN_000425c4();
      f33_step_channel_phase_monitors_a();
      f33_reset_windowed_monitor_febe7844_42c9a();
      FUN_00042caa();
      f33_reset_latched_monitor_febe7838_42b84();
      FUN_00042b94();
      FUN_00041fbe();
      FUN_00042030();
      FUN_0004215e();
      FUN_0004218a();
      f33_return_only_stub_427f0();
      f33_publish_channel_monitor_actions_a();
      FUN_00043374();
      FUN_0004337a();
      FUN_00043586();
      f33_step_channel_phase_monitors_b();
      f33_reset_windowed_monitor_febe7954_43c5e();
      FUN_00043c6e();
      f33_reset_latched_monitor_febe7948_43b46();
      FUN_00043b56();
      FUN_00042f7c();
      FUN_00042fee();
      FUN_0004311c();
      FUN_00043148();
      f33_return_only_stub_437b2();
      f33_publish_channel_monitor_actions_b();
      f33_reset_latched_monitor_febe79a0_4440c();
      FUN_0004441c();
      f33_reset_latched_monitor_febe7988_440ac();
      FUN_000440bc();
      f33_reset_latched_monitor_febe7994_4425c();
      FUN_0004426c();
      f33_reset_latched_monitor_febe79c4_44758();
      FUN_00044768();
      f33_reset_latched_monitor_febe79d0_44846();
      FUN_00044856();
      f33_reset_latched_monitor_febe7970_43f48();
      FUN_00043f58();
      f33_reset_latched_monitor_febe797c_43ffa();
      FUN_0004400a();
      f33_return_only_stub_44926();
      f33_publish_shared_condition_monitor_actions();
      f33_return_only_stub_452a6();
      f33_publish_local_channel_monitor_actions_a();
      f33_return_only_stub_454c2();
    }
    f33_publish_local_channel_monitor_actions_b();
  }
  if (uVar1 - 0x301 < 0x222) {
    if (uVar2 - 0x301 < 0x222) {
      FUN_00046090();
      FUN_00046366();
      FUN_00046b1e();
      FUN_00046e28();
      FUN_0004759c();
      FUN_000476a2();
      FUN_0004740c();
      FUN_000474d4();
      FUN_000477a8();
      FUN_00047944();
      FUN_00046a52();
      f33_publish_shared_snapshot_monitor_actions();
      FUN_00046994();
    }
    else {
      FUN_00046080();
      FUN_00046090();
      FUN_00046356();
      FUN_00046366();
      FUN_00046b0e();
      FUN_00046b1e();
      FUN_00046e18();
      FUN_00046e28();
      FUN_0004758c();
      FUN_0004759c();
      FUN_00047692();
      FUN_000476a2();
      FUN_000473fc();
      FUN_0004740c();
      FUN_000474c4();
      FUN_000474d4();
      FUN_00047798();
      FUN_000477a8();
      FUN_00047934();
      FUN_00047944();
      f33_reset_recoverable_monitor_febe7c68_46a42();
      FUN_00046a52();
      f33_return_only_stub_47114();
      f33_publish_shared_snapshot_monitor_actions();
      FUN_00046982();
      FUN_00046994();
      f33_return_only_stub_45254();
    }
    FUN_00045256();
  }
  if (0x102 < uVar1) {
    if (uVar2 < 0x103) {
      FUN_0003be52();
    }
    f33_aggregate_fault_actions();
    if (uVar2 < 0x103) {
      f33_return_only_stub_32722();
      f33_update_active_monitor_current_calibration();
      f33_return_only_stub_320c0();
      FUN_00032240();
      f33_return_only_stub_33ab4();
      f33_step_retained_fit_coherence();
      f33_return_only_stub_35530();
    }
    else {
      f33_update_active_monitor_current_calibration();
      FUN_00032240();
      f33_step_retained_fit_coherence();
    }
    FUN_00035598();
  }
  if (uVar1 == 0x600) {
    if (uVar2 != 0x600) {
      f33_return_only_stub_32622();
    }
    FUN_00032624();
  }
  if (0x1ff < uVar1) {
    if (uVar2 < 0x200) {
      f33_return_only_stub_35cea();
      f33_update_limit_budget_branch0();
      f33_return_only_stub_35d56();
      f33_update_limit_budget_branch1();
      f33_reset_owner9_budget_limit_state();
    }
    else {
      f33_update_limit_budget_branch0();
      f33_update_limit_budget_branch1();
    }
    f33_publish_owner9_budget_limit();
  }
  FUN_00057f00();
  return;
}



/* R7/R8 low16 current/prior mode. Mode>0100 updates aggregate and direct output owners; crossing
   from<=0100 also resets direct enables/codes before publication. Mode>=0200 advances offset
   selector;0300..0400 clears reserved monitor action slot;>0101 updates additional paired outputs.
   Ends57F00. These are mode-dependent calls, not a second steering permission system. */

void f33_update_mode_owned_application_requests(uint context,ushort mode,ushort previous_mode)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)previous_mode;
  uVar1 = (uint)mode;
  if (0x1ff < uVar1) {
    if (uVar2 < 0x200) {
      f33_return_only_stub_36298();
      f33_update_transient_current_reference_qualification();
      FUN_00037920();
      FUN_0003792a();
      FUN_00037956();
      FUN_00037960();
      f33_initialize_phase_offset_selector();
    }
    else {
      f33_update_transient_current_reference_qualification();
      FUN_0003792a();
      FUN_00037960();
    }
    f33_advance_phase_offset_selector();
  }
  if (uVar1 - 0x300 < 0x101) {
    if (0x100 < uVar2 - 0x300) {
      f33_return_only_stub_45ccc();
    }
    f33_clear_reserved_monitor_action_slot();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      f33_return_only_stub_571b2();
      f33_publish_aggregate_output_requests();
      f33_initialize_direct_output_requests();
      f33_publish_direct_output_requests();
      FUN_0005711a();
      FUN_00057130();
      FUN_00056d7a();
      FUN_00056e34();
      FUN_00056e7c();
      FUN_00056ed0();
      FUN_000569c2();
      f33_update_channel_requests();
      FUN_00056b8e();
      FUN_00056be2();
      FUN_000568f2();
      FUN_00056908();
      FUN_00056954();
      FUN_00056982();
      FUN_000567fe();
      FUN_000568ac();
      FUN_00056b1c();
      FUN_00056b32();
      f33_fill_constant_block_56c3c();
      FUN_00056cb0();
      FUN_00050c38();
      FUN_00050c58();
      FUN_00057eb4();
      FUN_00057ebc();
      f33_return_only_stub_570a8();
    }
    else {
      f33_publish_aggregate_output_requests();
      f33_publish_direct_output_requests();
      FUN_00057130();
      FUN_00056e34();
      FUN_00056ed0();
      f33_update_channel_requests();
      FUN_00056be2();
      FUN_00056908();
      FUN_00056982();
      FUN_000568ac();
      FUN_00056b32();
      FUN_00056cb0();
      FUN_00050c58();
      FUN_00057ebc();
    }
    FUN_000570aa();
  }
  if (0x101 < uVar1) {
    if (uVar2 < 0x102) {
      f33_return_only_stub_53db4();
      f33_return_only_stub_53db6();
      f33_return_only_stub_56332();
    }
    else {
      f33_return_only_stub_53db6();
    }
    f33_return_only_stub_56334();
  }
  FUN_00057f00();
  return;
}



/* Steady-mode counterpart: current planes when low16 mode>100h; aggregate actions then calibration
   adoption when mode>102h. No transition initializers. Current conditioning therefore precedes
   active-calibration adoption in this call. */

void f33_step_steady_channel_monitor_slice(uint unused_r6,ushort current_mode)

{
  uint uVar1;
  
  uVar1 = (uint)current_mode;
  if (0xff < uVar1) {
    FUN_0005672c();
    FUN_000566ac();
    f33_copy_cell_block_50b26();
    f33_snapshot_acquisition_status_flags();
    f33_snapshot_acquisition_range_fields();
  }
  if (0x100 < uVar1) {
    f33_condition_monitor_current_planes();
    FUN_000495b6();
  }
  if (0xff < uVar1) {
    FUN_00048230();
  }
  if (0x100 < uVar1) {
    f33_update_scalar_availability();
  }
  if (0x102 < uVar1) {
    if (uVar1 < 0x523) {
      f33_step_acquisition_status_a_monitor();
      f33_step_acquisition_status_b_monitor();
      f33_step_acquisition_range_a_monitor();
      f33_step_acquisition_range_b_monitor();
      f33_publish_acquisition_monitor_actions();
    }
    f33_compose_local_status_fault_actions();
  }
  if (uVar1 - 0x200 < 0x323) {
    FUN_0004523e();
    f33_step_paired_source_counter_monitor_a();
    f33_step_paired_source_counter_monitor_b();
    f33_step_paired_source_mask_monitor_a();
    f33_step_paired_source_mask_monitor_b();
    f33_publish_paired_source_difference_changes();
    f33_step_paired_source_difference_monitors_a();
    f33_step_paired_source_difference_monitors_b();
    f33_publish_paired_source_monitor_actions();
    FUN_000423bc();
    if (uVar1 - 0x20c < 0x317) {
      FUN_00041e96();
    }
    f33_step_channel_phase_monitors_a();
    FUN_00042caa();
    FUN_00042b94();
    FUN_00042030();
    FUN_0004218a();
    f33_publish_channel_monitor_actions_a();
    FUN_0004337a();
    if (uVar1 - 0x20c < 0x317) {
      FUN_00042e54();
    }
    f33_step_channel_phase_monitors_b();
    FUN_00043c6e();
    FUN_00043b56();
    FUN_00042fee();
    FUN_00043148();
    f33_publish_channel_monitor_actions_b();
    if (uVar1 - 0x301 < 0x222) {
      FUN_00043f1a();
    }
    FUN_0004441c();
    if (uVar1 - 0x20b < 0x318) {
      FUN_0004460c();
      FUN_000446ba();
    }
    FUN_000440bc();
    FUN_0004426c();
    FUN_00044768();
    FUN_00044856();
    FUN_00043f58();
    FUN_0004400a();
    f33_publish_shared_condition_monitor_actions();
    f33_publish_local_channel_monitor_actions_a();
    f33_publish_local_channel_monitor_actions_b();
  }
  if (uVar1 - 0x301 < 0x222) {
    FUN_00046090();
    FUN_00046366();
    FUN_00046b1e();
    FUN_00046e28();
    FUN_0004759c();
    FUN_000476a2();
    FUN_0004740c();
    FUN_000474d4();
    FUN_000477a8();
    FUN_00047944();
    FUN_00046a52();
    f33_publish_shared_snapshot_monitor_actions();
    FUN_00046994();
    FUN_00045256();
  }
  if (0x102 < uVar1) {
    f33_aggregate_fault_actions();
    f33_update_active_monitor_current_calibration();
    FUN_00032240();
    f33_step_retained_fit_coherence();
    FUN_00035598();
  }
  if (uVar1 == 0x600) {
    FUN_00032624();
  }
  if (0x1ff < uVar1) {
    f33_update_limit_budget_branch0();
    f33_update_limit_budget_branch1();
    f33_publish_owner9_budget_limit();
  }
  FUN_00057f00();
  return;
}



/* Steady-mode counterpart: low16 mode>0100 updates aggregate/direct output owners and other
   configured requests without entry reset;>=0200 advances phase offset,0300..0400 clears reserved
   monitor slot,>0101 updates additional paired outputs. Ends57F00; no implied physical scheduling
   interval. */

void f33_update_steady_application_requests(uint context,ushort mode)

{
  uint uVar1;
  
  uVar1 = (uint)mode;
  if (0x1ff < uVar1) {
    f33_update_transient_current_reference_qualification();
    FUN_0003792a();
    FUN_00037960();
    f33_advance_phase_offset_selector();
  }
  if (uVar1 - 0x300 < 0x101) {
    f33_clear_reserved_monitor_action_slot();
  }
  if (0x100 < uVar1) {
    f33_publish_aggregate_output_requests();
    f33_publish_direct_output_requests();
    FUN_00057130();
    FUN_00056e34();
    FUN_00056ed0();
    f33_update_channel_requests();
    FUN_00056be2();
    FUN_00056908();
    FUN_00056982();
    FUN_000568ac();
    FUN_00056b32();
    FUN_00056cb0();
    FUN_00050c58();
    FUN_00057ebc();
    FUN_000570aa();
  }
  if (0x101 < uVar1) {
    f33_return_only_stub_53db6();
    f33_return_only_stub_56334();
  }
  FUN_00057f00();
  return;
}



void FUN_0005ec24(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      f33_return_only_stub_50c98();
    }
    f33_snapshot_local_status_link_flags();
  }
  if (param_2 == 0x101) {
    if (param_3 != 0x101) {
      f33_return_only_stub_56788();
    }
    FUN_0005678a();
  }
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      f33_return_only_stub_509a2();
      f33_refresh_diagnostic_application_availability();
      f33_return_only_stub_49b3a();
      FUN_00049e22();
      FUN_000498f6();
      f33_reconcile_application_normal_network_policy();
      f33_return_only_stub_49f1e();
      f33_update_internal_source_admission_lifecycle();
      f33_return_only_stub_49706();
      f33_update_application_receive_statuses();
      f33_return_only_stub_4ae70();
      FUN_0004ae72();
      f33_return_only_stub_4aed4();
      FUN_0004aed6();
      f33_return_only_stub_4af6a();
      FUN_0004af6c();
      f33_return_only_stub_4afea();
      FUN_0004afec();
      f33_return_only_stub_4b12c();
      FUN_0004b12e();
      f33_return_only_stub_4b1f4();
      FUN_0004b1f6();
      f33_return_only_stub_4b240();
      FUN_0004b242();
      f33_return_only_stub_4b376();
      f33_refresh_route30_health_inputs();
      f33_return_only_stub_4b40c();
      FUN_0004b40e();
      f33_return_only_stub_4b470();
      FUN_0004b472();
      f33_return_only_stub_4b59c();
      FUN_0004b59e();
      f33_return_only_stub_4b688();
      FUN_0004b68a();
      f33_return_only_stub_4b7d4();
      FUN_0004b7d6();
      f33_return_only_stub_4b86c();
      FUN_0004b86e();
      f33_return_only_stub_4b8f2();
      FUN_0004b8f4();
      f33_return_only_stub_4b9f2();
      FUN_0004b9f4();
      f33_return_only_stub_4bb60();
      FUN_0004bb62();
      f33_return_only_stub_4bc26();
      FUN_0004bc28();
      f33_return_only_stub_4bcbe();
      FUN_0004bcc0();
      f33_return_only_stub_4bd44();
      FUN_0004bd46();
      f33_return_only_stub_4bece();
      FUN_0004bed0();
      f33_return_only_stub_4bf4c();
      FUN_0004bf4e();
      f33_return_only_stub_4bfb0();
      FUN_0004bfb2();
      f33_return_only_stub_4b04c();
      FUN_0004b04e();
      f33_return_only_stub_4b0ae();
      FUN_0004b0b0();
      f33_return_only_stub_4b4d2();
      FUN_0004b4d4();
      f33_return_only_stub_4ae28();
      FUN_0004ae2a();
      f33_return_only_stub_4b192();
      FUN_0004b194();
      FUN_0004aad4();
      FUN_0004aae8();
      f33_return_only_stub_4a4b0();
      FUN_0004a702();
      f33_return_only_stub_4a7aa();
      FUN_0004aa5c();
      f33_fill_constant_block_4ad1a();
      FUN_0004ada2();
      f33_return_only_stub_4a448();
      FUN_0004a49e();
      f33_return_only_stub_4adcc();
      FUN_0004adce();
      f33_return_only_stub_4abbc();
      FUN_0004abbe();
      FUN_0004ac14();
      FUN_0004ac28();
      f33_return_only_stub_4cf64();
    }
    else {
      f33_refresh_diagnostic_application_availability();
      FUN_00049e22();
      f33_reconcile_application_normal_network_policy();
      f33_update_internal_source_admission_lifecycle();
      f33_update_application_receive_statuses();
      FUN_0004ae72();
      FUN_0004aed6();
      FUN_0004af6c();
      FUN_0004afec();
      FUN_0004b12e();
      FUN_0004b1f6();
      FUN_0004b242();
      f33_refresh_route30_health_inputs();
      FUN_0004b40e();
      FUN_0004b472();
      FUN_0004b59e();
      FUN_0004b68a();
      FUN_0004b7d6();
      FUN_0004b86e();
      FUN_0004b8f4();
      FUN_0004b9f4();
      FUN_0004bb62();
      FUN_0004bc28();
      FUN_0004bcc0();
      FUN_0004bd46();
      FUN_0004bed0();
      FUN_0004bf4e();
      FUN_0004bfb2();
      FUN_0004b04e();
      FUN_0004b0b0();
      FUN_0004b4d4();
      FUN_0004ae2a();
      FUN_0004b194();
      FUN_0004aae8();
      FUN_0004a702();
      FUN_0004aa5c();
      FUN_0004ada2();
      FUN_0004a49e();
      FUN_0004adce();
      FUN_0004abbe();
      FUN_0004ac28();
    }
    FUN_0004d094();
    if (param_3 < 0x100) {
      f33_return_only_stub_47ade();
      FUN_00047ae0();
      f33_return_only_stub_47ac2();
    }
    else {
      FUN_00047ae0();
    }
    FUN_00047ac4();
  }
  if (0x102 < param_2) {
    uVar1 = param_1 & 0x10;
    if (param_3 < 0x103) {
      FUN_0004825c();
      if (uVar1 != 0) {
        f33_update_thermistor_channels();
      }
      FUN_000483b6();
      if (uVar1 != 0) goto LAB_0005eeaa;
LAB_0005eeae:
      if (param_2 < 0x103) goto LAB_0005ef00;
    }
    else if (uVar1 != 0) {
      f33_update_thermistor_channels();
LAB_0005eeaa:
      FUN_000483bc();
      goto LAB_0005eeae;
    }
    if (param_2 < 0x523) {
      if (param_3 - 0x103 < 0x420) {
        f33_update_qualified_local_status_monitor();
        f33_update_paired_local_status_monitor();
        f33_update_individual_local_status_a();
      }
      else {
        f33_reset_latched_monitor_febe74b0_3d746();
        f33_update_qualified_local_status_monitor();
        FUN_0003d826();
        f33_update_paired_local_status_monitor();
        f33_reset_recoverable_monitor_febe74cc_3d906();
        f33_update_individual_local_status_a();
        f33_reset_recoverable_monitor_febe74d8_3d9b8();
      }
      f33_update_individual_local_status_b();
    }
    if (param_3 < 0x103) {
      FUN_0003d5e4();
    }
    f33_publish_local_status_link_fault();
  }
LAB_0005ef00:
  uVar1 = param_2 - 0x200;
  if (uVar1 < 0x323) {
    if (param_3 - 0x200 < 0x323) {
      FUN_00042a6a();
      FUN_00043a2c();
      f33_step_local_channel_mismatch_a_monitor();
      f33_step_local_output_status_a_monitor();
      f33_step_local_channel_mismatch_b_monitor();
    }
    else {
      f33_reset_latched_monitor_febe782c_42a5a();
      FUN_00042a6a();
      f33_reset_latched_monitor_febe793c_43a1c();
      FUN_00043a2c();
      f33_reset_scalar_monitor_45410_45400();
      f33_step_local_channel_mismatch_a_monitor();
      f33_reset_scalar_monitor_45356_45346();
      f33_step_local_output_status_a_monitor();
      f33_reset_scalar_monitor_4562a_4561a();
      f33_step_local_channel_mismatch_b_monitor();
      f33_reset_scalar_monitor_45572_45562();
    }
    f33_step_local_output_status_b_monitor();
  }
  if (uVar1 < 0xe) {
    if (param_2 == 0x200) {
      if (param_3 == 0x200) {
        f33_step_sample_difference_window_a();
      }
      else {
        FUN_00040042();
        f33_step_sample_difference_window_a();
        FUN_00040222();
      }
      f33_step_sample_difference_window_b();
    }
    if (param_2 == 0x201) {
      if (param_3 == 0x201) {
        f33_step_bounded_sample_or_status_a();
      }
      else {
        FUN_0003f702();
        f33_step_bounded_sample_or_status_a();
        FUN_0003f88e();
      }
      f33_step_bounded_sample_or_status_b();
    }
    if (param_2 == 0x202) {
      if (param_3 == 0x202) {
        f33_step_baseline_sample_threshold_a();
      }
      else {
        FUN_0004087e();
        f33_step_baseline_sample_threshold_a();
        FUN_000409f6();
      }
      f33_step_baseline_sample_threshold_b();
    }
    if (param_2 == 0x203) {
      if (param_3 == 0x203) {
        f33_step_requested_state_sample_threshold_a();
      }
      else {
        FUN_0003fa1a();
        f33_step_requested_state_sample_threshold_a();
        FUN_0003fbf4();
      }
      f33_step_requested_state_sample_threshold_b();
    }
    if (param_2 == 0x204) {
      if (param_3 == 0x204) {
        f33_step_startup_status_bit_triplet_a();
      }
      else {
        FUN_00041596();
        f33_step_startup_status_bit_triplet_a();
        FUN_000417ce();
      }
      f33_step_startup_status_bit_triplet_b();
    }
    if (param_2 == 0x205) {
      if (param_3 == 0x205) {
        f33_step_delayed_status_bit_triplet_a();
      }
      else {
        FUN_0003e5a6();
        f33_step_delayed_status_bit_triplet_a();
        FUN_0003e83e();
      }
      f33_step_delayed_status_bit_triplet_b();
    }
    if (param_2 == 0x206) {
      if (param_3 == 0x206) {
        f33_step_command_status_bit_clear_a();
      }
      else {
        FUN_0003f2d6();
        f33_step_command_status_bit_clear_a();
        FUN_0003f4ec();
      }
      f33_step_command_status_bit_clear_b();
    }
    if (param_2 == 0x207) {
      if (param_3 == 0x207) {
        f33_step_observed_state_sample_regions_a();
      }
      else {
        FUN_00040b6e();
        f33_step_observed_state_sample_regions_a();
        FUN_00040e08();
      }
      f33_step_observed_state_sample_regions_b();
    }
    if (param_2 == 0x208) {
      if (param_3 != 0x208) {
        FUN_0003eff0();
      }
      f33_step_coupled_sample_threshold_both();
    }
    if (param_2 == 0x209) {
      if (param_3 == 0x209) {
        f33_step_asserted_state_sample_threshold_a();
      }
      else {
        f33_reset_asserted_state_sample_threshold_a_3fdce();
        f33_step_asserted_state_sample_threshold_a();
        f33_reset_asserted_state_sample_threshold_b_3ff08();
      }
      f33_step_asserted_state_sample_threshold_b();
    }
    if (param_2 == 0x20a) {
      if (param_3 == 0x20a) {
        f33_step_matched_state2_status_bit_a();
      }
      else {
        FUN_00040402();
        f33_step_matched_state2_status_bit_a();
        FUN_0004063e();
      }
      f33_step_matched_state2_status_bit_b();
    }
    if (param_2 == 0x20b) {
      if (param_3 == 0x20b) {
        f33_step_sample_range_triplet_a();
      }
      else {
        FUN_000410c0();
        f33_step_sample_range_triplet_a();
        FUN_0004132a();
      }
      f33_step_sample_range_triplet_b();
    }
    if (param_2 == 0x20c) {
      if (param_3 == 0x20c) {
        f33_step_matched_state2_startup_triplet_a();
      }
      else {
        FUN_00041a06();
        f33_step_matched_state2_startup_triplet_a();
        FUN_00041c36();
      }
      f33_step_matched_state2_startup_triplet_b();
    }
    if (param_2 == 0x20d) {
      if (param_3 == 0x20d) {
        f33_step_matched_state2_status_bit_triplet_a();
      }
      else {
        FUN_0003eadc();
        f33_step_matched_state2_status_bit_triplet_a();
        FUN_0003ed0c();
      }
      f33_step_matched_state2_status_bit_triplet_b();
    }
    if (uVar1 < 0xe) {
      if (0xd < param_3 - 0x200) {
        f33_return_only_stub_3ef1a();
      }
      FUN_0003efd4();
    }
  }
  if (param_2 - 0x301 < 0x222) {
    uVar1 = param_1 & 8;
    if (param_3 - 0x301 < 0x222) {
      if (uVar1 != 0) {
        f33_step_paired_scalar_relation_monitor();
        f33_step_qualified_scalar_relation_a_monitor();
        f33_step_qualified_scalar_relation_b_monitor();
        f33_step_admitted_scalar_receive_condition_monitor();
      }
    }
    else {
      f33_reset_scalar_monitor_45838_45828();
      if (uVar1 != 0) {
        f33_step_paired_scalar_relation_monitor();
      }
      f33_reset_scalar_monitor_4599c_4598c();
      if (uVar1 != 0) {
        f33_step_qualified_scalar_relation_a_monitor();
      }
      f33_reset_scalar_monitor_45a6c_45a5c();
      if (uVar1 != 0) {
        f33_step_qualified_scalar_relation_b_monitor();
      }
      f33_reset_scalar_monitor_456fa_456ea();
      if (uVar1 != 0) {
        f33_step_admitted_scalar_receive_condition_monitor();
      }
      f33_return_only_stub_45b1e();
    }
    f33_publish_scalar_relation_monitor_actions();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      FUN_0003cb48();
      f33_update_communication_qualification_monitors();
      f33_return_only_stub_3ce62();
      f33_publish_selected_source_fault_edges();
      f33_return_only_stub_3d028();
      f33_publish_source_family_fault_edges();
      f33_return_only_stub_3d54c();
      FUN_0003d54e();
      f33_reset_latched_monitor_febe7490_3d426();
      f33_update_received_content_monitor_a();
      f33_reset_latched_monitor_febe749c_3d4c0();
      f33_update_received_content_monitor_b();
      f33_return_only_stub_3d31a();
    }
    else {
      f33_update_communication_qualification_monitors();
      f33_publish_selected_source_fault_edges();
      f33_publish_source_family_fault_edges();
      FUN_0003d54e();
      f33_update_received_content_monitor_a();
      f33_update_received_content_monitor_b();
    }
    f33_compose_communication_status_fault_actions();
    uVar1 = param_1 & 0x10;
    if (param_3 < 0x103) {
      f33_reset_scalar_monitor_45e74_45e64();
      if (uVar1 != 0) {
        f33_step_raw_thermistor_range_a_monitor();
      }
      f33_reset_scalar_monitor_45f32_45f22();
      if (uVar1 != 0) {
        f33_step_raw_thermistor_range_b_monitor();
      }
      f33_return_only_stub_45fd2();
      if (uVar1 != 0) goto LAB_0005f23e;
    }
    else if (uVar1 != 0) {
      f33_step_raw_thermistor_range_a_monitor();
      f33_step_raw_thermistor_range_b_monitor();
LAB_0005f23e:
      f33_publish_thermistor_range_monitor_actions();
    }
    if (0x102 < param_2) {
      if (param_3 < 0x103) {
        f33_reload_ba_admission_records();
        f33_poll_ba_retained_start();
        FUN_00035c02();
        FUN_00035c38();
        f33_fill_constant_block_35aea();
        FUN_00035b78();
        f33_restore_monitor_current_calibration();
        f33_refresh_monitor_current_calibration();
        thunk_FUN_00032398();
        FUN_00032580();
        FUN_000346f0();
        FUN_000347e2();
        FUN_000356c8();
      }
      else {
        f33_poll_ba_retained_start();
        FUN_00035c38();
        FUN_00035b78();
        f33_refresh_monitor_current_calibration();
        FUN_00032580();
        FUN_000347e2();
      }
      f33_step_learned_quad_record_completion();
    }
  }
  if (param_2 == 0x512) {
    if (param_3 != 0x512) {
      FUN_00033d32();
    }
    f33_step_fit_completion();
  }
  if (param_2 == 0x600) {
    if (param_3 == 0x600) {
      f33_step_mode600_fit_request();
    }
    else {
      FUN_00032c86();
      f33_step_mode600_fit_request();
      FUN_00033d32();
    }
    f33_step_fit_completion();
  }
  if (param_2 - 0x101 < 0x10d) {
    if (0x10c < param_3 - 0x101) {
      FUN_00031f18();
    }
    f33_request_published_mode200_phase();
  }
  if (0x700 < param_2) {
    if (param_3 < 0x701) {
      f33_initialize_thermal_shutdown_counter();
    }
    if ((param_1 >> 3 & 1) != 0) {
      f33_step_thermal_shutdown_request();
    }
  }
  if (0x1ff < param_2) {
    param_1 = param_1 & 0x10;
    if (param_3 < 0x200) {
      FUN_000360ce();
      FUN_000360e0();
      FUN_0003b134();
      if (param_1 != 0) {
        f33_run_init_chain_3b398();
      }
      FUN_0003b502();
      if (param_1 != 0) {
        FUN_0003b88e();
      }
      f33_restore_thermal_drive_epoch_maxima();
      if (param_1 != 0) {
        f33_update_thermal_drive_epoch_maxima();
      }
      f33_return_only_stub_39758();
      if (param_1 != 0) {
        FUN_0003984a();
      }
      FUN_00039bfe();
      if (param_1 != 0) {
        f33_update_ecu_source2_thermal_estimate();
      }
      FUN_0003a26c();
      if (param_1 != 0) {
        f33_publish_ecu_source2_thermal_limit_maps();
      }
      FUN_0003991c();
      if (param_1 != 0) {
        f33_update_ecu_source4_thermal_estimate();
      }
      FUN_00039bb2();
      if (param_1 != 0) {
        f33_publish_ecu_source4_thermal_limit_maps();
      }
      FUN_0003905a();
      if (param_1 != 0) {
        f33_update_ecu_source5_thermal_estimate();
      }
      FUN_00039392();
      if (param_1 != 0) {
        f33_publish_ecu_source5_thermal_limit_maps();
      }
      FUN_0003acf8();
      if (param_1 != 0) {
        f33_update_ecu_source3_thermal_estimate();
      }
      FUN_0003b0e8();
      if (param_1 != 0) {
        f33_publish_ecu_source3_thermal_limit_maps();
      }
      FUN_000393de();
      f33_poll_thermal_history_record_status();
      FUN_0003a55a();
      if (param_1 != 0) {
        f33_update_motor_thermal_estimate();
      }
      FUN_0003a99c();
      if (param_1 != 0) {
        f33_publish_motor_thermal_limit_maps();
      }
      f33_fill_constant_block_3a2b8();
      f33_arbitrate_thermal_current_limits();
      f33_reset_latched_monitor_febe704c_3b468();
      if (param_1 != 0) {
        FUN_0003b478();
      }
      f33_reset_latched_monitor_febe7040_3b3c0();
      if (param_1 != 0) {
        FUN_0003b3d0();
      }
      f33_return_only_stub_3a9e8();
      if (param_1 == 0) goto LAB_0005f45c;
    }
    else {
      FUN_000360e0();
      if (param_1 != 0) {
        f33_run_init_chain_3b398();
        FUN_0003b88e();
        f33_update_thermal_drive_epoch_maxima();
        FUN_0003984a();
        f33_update_ecu_source2_thermal_estimate();
        f33_publish_ecu_source2_thermal_limit_maps();
        f33_update_ecu_source4_thermal_estimate();
        f33_publish_ecu_source4_thermal_limit_maps();
        if (param_1 != 0) {
          f33_update_ecu_source5_thermal_estimate();
          f33_publish_ecu_source5_thermal_limit_maps();
          f33_update_ecu_source3_thermal_estimate();
          f33_publish_ecu_source3_thermal_limit_maps();
        }
      }
      f33_poll_thermal_history_record_status();
      if (param_1 != 0) {
        f33_update_motor_thermal_estimate();
        f33_publish_motor_thermal_limit_maps();
      }
      f33_arbitrate_thermal_current_limits();
      if (param_1 == 0) goto LAB_0005f45c;
      FUN_0003b478();
      FUN_0003b3d0();
    }
    f33_update_thermal_history_qualification();
  }
LAB_0005f45c:
  f33_publish_foreground_ecu_outputs();
  return;
}



void FUN_0005f464(uint param_1,ushort param_2,ushort param_3)

{
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      FUN_0004bffa();
      f33_run_init_chain_4c590();
      FUN_0004c5f0();
      FUN_0004c784();
      f33_return_only_stub_4c978();
      FUN_0004c97a();
      f33_return_only_stub_4ce06();
      FUN_0004ce08();
      f33_return_only_stub_4c7a8();
      FUN_0004c7aa();
      f33_return_only_stub_4cece();
      FUN_0004ced0();
      f33_return_only_stub_4c8de();
    }
    else {
      f33_run_init_chain_4c590();
      FUN_0004c784();
      FUN_0004c97a();
      FUN_0004ce08();
      FUN_0004c7aa();
      FUN_0004ced0();
    }
    FUN_0004c8e0();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      FUN_00057e16();
    }
    FUN_00057e26();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      f33_return_only_stub_56f30();
      FUN_00056f32();
      f33_return_only_stub_56f2a();
      f33_return_only_stub_56f2c();
      f33_return_only_stub_56f8c();
      FUN_00056f8e();
      f33_return_only_stub_57000();
      FUN_00057002();
      f33_return_only_stub_567c8();
    }
    else {
      FUN_00056f32();
      f33_return_only_stub_56f2c();
      FUN_00056f8e();
      FUN_00057002();
    }
    FUN_000567ca();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      FUN_00051e8a();
      f33_service_diagnostic_record_transaction();
      FUN_00052ad4();
      f33_run_init_chain_52de4();
      f33_return_only_stub_54240();
      f33_return_only_stub_54242();
      FUN_00054488();
      FUN_00054566();
      FUN_00054746();
      if ((param_1 & 0x10) != 0) {
        FUN_000549c8();
      }
      FUN_00054ce2();
      FUN_000551bc();
      f33_return_only_stub_564ca();
      f33_return_only_stub_564cc();
      FUN_00050fae();
      if ((param_1 >> 1 & 1) != 0) {
        f33_update_diagnostic_classifier_output();
      }
      FUN_00051612();
      f33_service_diagnostic_request_lifecycle();
      FUN_00056fc8();
      FUN_00056fce();
      f33_return_only_stub_56756();
    }
    else {
      f33_service_diagnostic_record_transaction();
      f33_run_init_chain_52de4();
      f33_return_only_stub_54242();
      FUN_00054566();
      if ((param_1 & 0x10) != 0) {
        FUN_000549c8();
      }
      FUN_000551bc();
      f33_return_only_stub_564cc();
      if ((param_1 >> 1 & 1) != 0) {
        f33_update_diagnostic_classifier_output();
      }
      f33_service_diagnostic_request_lifecycle();
      FUN_00056fce();
    }
    FUN_00056758();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      f33_return_only_stub_57056();
    }
    FUN_00057058();
  }
  if (param_2 == 0x702) {
    if (param_3 != 0x702) {
      f33_return_only_stub_567a4();
    }
    FUN_000567a6();
  }
  if (0x8ff < param_2) {
    if (param_3 < 0x900) {
      FUN_00056cf0();
    }
    FUN_00056cf6();
  }
  f33_publish_foreground_ecu_outputs();
  return;
}



void FUN_0005f610(uint param_1,uint param_2)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    f33_snapshot_local_status_link_flags();
  }
  if (param_2 == 0x101) {
    FUN_0005678a();
  }
  if (0xff < param_2) {
    f33_refresh_diagnostic_application_availability();
    FUN_00049e22();
    f33_reconcile_application_normal_network_policy();
    f33_update_internal_source_admission_lifecycle();
    f33_update_application_receive_statuses();
    FUN_0004ae72();
    FUN_0004aed6();
    FUN_0004af6c();
    FUN_0004afec();
    FUN_0004b12e();
    FUN_0004b1f6();
    FUN_0004b242();
    f33_refresh_route30_health_inputs();
    FUN_0004b40e();
    FUN_0004b472();
    FUN_0004b59e();
    FUN_0004b68a();
    FUN_0004b7d6();
    FUN_0004b86e();
    FUN_0004b8f4();
    FUN_0004b9f4();
    FUN_0004bb62();
    FUN_0004bc28();
    FUN_0004bcc0();
    FUN_0004bd46();
    FUN_0004bed0();
    FUN_0004bf4e();
    FUN_0004bfb2();
    FUN_0004b04e();
    FUN_0004b0b0();
    FUN_0004b4d4();
    FUN_0004ae2a();
    FUN_0004b194();
    FUN_0004aae8();
    FUN_0004a702();
    FUN_0004aa5c();
    FUN_0004ada2();
    FUN_0004a49e();
    FUN_0004adce();
    FUN_0004abbe();
    FUN_0004ac28();
    FUN_0004d094();
    FUN_00047ae0();
    FUN_00047ac4();
  }
  if (0x102 < param_2) {
    if ((param_1 >> 4 & 1) != 0) {
      f33_update_thermistor_channels();
      FUN_000483bc();
    }
    if (param_2 < 0x523) {
      f33_update_qualified_local_status_monitor();
      f33_update_paired_local_status_monitor();
      f33_update_individual_local_status_a();
      f33_update_individual_local_status_b();
    }
    f33_publish_local_status_link_fault();
  }
  uVar1 = param_2 - 0x200;
  if (uVar1 < 0x323) {
    FUN_00042a6a();
    FUN_00043a2c();
    f33_step_local_channel_mismatch_a_monitor();
    f33_step_local_output_status_a_monitor();
    f33_step_local_channel_mismatch_b_monitor();
    f33_step_local_output_status_b_monitor();
  }
  if (uVar1 < 0xe) {
    if (param_2 == 0x200) {
      f33_step_sample_difference_window_a();
      f33_step_sample_difference_window_b();
    }
    if (param_2 == 0x201) {
      f33_step_bounded_sample_or_status_a();
      f33_step_bounded_sample_or_status_b();
    }
    if (param_2 == 0x202) {
      f33_step_baseline_sample_threshold_a();
      f33_step_baseline_sample_threshold_b();
    }
    if (param_2 == 0x203) {
      f33_step_requested_state_sample_threshold_a();
      f33_step_requested_state_sample_threshold_b();
    }
    if (param_2 == 0x204) {
      f33_step_startup_status_bit_triplet_a();
      f33_step_startup_status_bit_triplet_b();
    }
    if (param_2 == 0x205) {
      f33_step_delayed_status_bit_triplet_a();
      f33_step_delayed_status_bit_triplet_b();
    }
    if (param_2 == 0x206) {
      f33_step_command_status_bit_clear_a();
      f33_step_command_status_bit_clear_b();
    }
    if (param_2 == 0x207) {
      f33_step_observed_state_sample_regions_a();
      f33_step_observed_state_sample_regions_b();
    }
    if (param_2 == 0x208) {
      f33_step_coupled_sample_threshold_both();
    }
    if (param_2 == 0x209) {
      f33_step_asserted_state_sample_threshold_a();
      f33_step_asserted_state_sample_threshold_b();
    }
    if (param_2 == 0x20a) {
      f33_step_matched_state2_status_bit_a();
      f33_step_matched_state2_status_bit_b();
    }
    if (param_2 == 0x20b) {
      f33_step_sample_range_triplet_a();
      f33_step_sample_range_triplet_b();
    }
    if (param_2 == 0x20c) {
      f33_step_matched_state2_startup_triplet_a();
      f33_step_matched_state2_startup_triplet_b();
    }
    if (param_2 == 0x20d) {
      f33_step_matched_state2_status_bit_triplet_a();
      f33_step_matched_state2_status_bit_triplet_b();
    }
    if (uVar1 < 0xe) {
      FUN_0003efd4();
    }
  }
  if (param_2 - 0x301 < 0x222) {
    if ((param_1 >> 3 & 1) != 0) {
      f33_step_paired_scalar_relation_monitor();
      f33_step_qualified_scalar_relation_a_monitor();
      f33_step_qualified_scalar_relation_b_monitor();
      f33_step_admitted_scalar_receive_condition_monitor();
    }
    f33_publish_scalar_relation_monitor_actions();
  }
  if (0x102 < param_2) {
    f33_update_communication_qualification_monitors();
    f33_publish_selected_source_fault_edges();
    f33_publish_source_family_fault_edges();
    FUN_0003d54e();
    f33_update_received_content_monitor_a();
    f33_update_received_content_monitor_b();
    f33_compose_communication_status_fault_actions();
    if ((param_1 >> 4 & 1) != 0) {
      f33_step_raw_thermistor_range_a_monitor();
      f33_step_raw_thermistor_range_b_monitor();
      f33_publish_thermistor_range_monitor_actions();
      if (param_2 < 0x103) goto LAB_0005f87a;
    }
    f33_poll_ba_retained_start();
    FUN_00035c38();
    FUN_00035b78();
    f33_refresh_monitor_current_calibration();
    FUN_00032580();
    FUN_000347e2();
    f33_step_learned_quad_record_completion();
  }
LAB_0005f87a:
  if (param_2 == 0x512) {
    f33_step_fit_completion();
  }
  if (param_2 == 0x600) {
    f33_step_mode600_fit_request();
    f33_step_fit_completion();
  }
  if (param_2 - 0x101 < 0x10d) {
    f33_request_published_mode200_phase();
  }
  if ((0x700 < param_2) && ((param_1 >> 3 & 1) != 0)) {
    f33_step_thermal_shutdown_request();
  }
  if (0x1ff < param_2) {
    FUN_000360e0();
    param_1 = param_1 & 0x10;
    if (param_1 != 0) {
      f33_run_init_chain_3b398();
      FUN_0003b88e();
      f33_update_thermal_drive_epoch_maxima();
      FUN_0003984a();
      f33_update_ecu_source2_thermal_estimate();
      f33_publish_ecu_source2_thermal_limit_maps();
      f33_update_ecu_source4_thermal_estimate();
      f33_publish_ecu_source4_thermal_limit_maps();
      if (param_1 != 0) {
        f33_update_ecu_source5_thermal_estimate();
        f33_publish_ecu_source5_thermal_limit_maps();
        f33_update_ecu_source3_thermal_estimate();
        f33_publish_ecu_source3_thermal_limit_maps();
      }
    }
    f33_poll_thermal_history_record_status();
    if (param_1 != 0) {
      f33_update_motor_thermal_estimate();
      f33_publish_motor_thermal_limit_maps();
    }
    f33_arbitrate_thermal_current_limits();
    if (param_1 != 0) {
      FUN_0003b478();
      FUN_0003b3d0();
      f33_update_thermal_history_qualification();
    }
  }
  f33_publish_foreground_ecu_outputs();
  return;
}



void FUN_0005f91c(uint param_1,ushort param_2)

{
  if (0xff < param_2) {
    f33_run_init_chain_4c590();
    FUN_0004c784();
    FUN_0004c97a();
    FUN_0004ce08();
    FUN_0004c7aa();
    FUN_0004ced0();
    FUN_0004c8e0();
  }
  if (0x100 < param_2) {
    FUN_00057e26();
  }
  if (0x102 < param_2) {
    FUN_00056f32();
    f33_return_only_stub_56f2c();
    FUN_00056f8e();
    FUN_00057002();
    FUN_000567ca();
  }
  if (0x101 < param_2) {
    f33_service_diagnostic_record_transaction();
    f33_run_init_chain_52de4();
    f33_return_only_stub_54242();
    FUN_00054566();
    if ((param_1 >> 4 & 1) != 0) {
      FUN_000549c8();
    }
    FUN_000551bc();
    f33_return_only_stub_564cc();
    if ((param_1 >> 1 & 1) != 0) {
      f33_update_diagnostic_classifier_output();
    }
    f33_service_diagnostic_request_lifecycle();
    FUN_00056fce();
    FUN_00056758();
  }
  if (0x102 < param_2) {
    FUN_00057058();
  }
  if (param_2 == 0x702) {
    FUN_000567a6();
  }
  if (0x8ff < param_2) {
    FUN_00056cf6();
  }
  f33_publish_foreground_ecu_outputs();
  return;
}



void FUN_0005f9ce(void)

{
  switch(DAT_febe39da & 3) {
  case 0:
    FUN_00060a10();
    FUN_00060c20();
    break;
  case 1:
    FUN_00060462();
    break;
  case 2:
    FUN_00061f96();
    FUN_00061b90();
    FUN_00062018();
    break;
  case 3:
    FUN_000612dc();
    FUN_000628b2();
  }
  return;
}



/* Sequential initializer chain: 6 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_5fa12(void)

{
  FUN_000607d0();
  f33_write_configured_output_port_level_b(0);
  f33_write_configured_output_port_level_b(1);
  FUN_00061eb8();
  f33_write_channel_requested_level(0);
  f33_write_channel_requested_level(1);
  return;
}



void FUN_0005fa3a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90e0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + iVar1) = 0;
  } while (uVar2 < 0x50);
  uVar2 = 0;
  DAT_feef90e4 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef81e0u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90e8 = 0;
  return;
}



void FUN_0005fa84(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90ec = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + iVar1) = 0;
  } while (uVar2 < 0x60);
  uVar2 = 0;
  DAT_feef90f0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef8a20u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90f4 = 0;
  return;
}



void FUN_0005face(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_0005fa3a();
  FUN_0005fa84();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffa))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff8))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff7))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffc))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffb))))) = 0;
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_5fafe(void)

{
  DAT_fff89110 = 2;
  DAT_fff91340 = 0;
  DAT_fff92340 = 0;
  DAT_fff91384 = 2;
  DAT_fff92384 = 2;
  DAT_fff91398 = 1;
  DAT_fff92398 = 1;
  DAT_fff913c0 = 0x10;
  DAT_fff923c0 = 0x10;
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  DAT_fff91800 = 0xfff;
  DAT_fff92800 = 0xfff;
  return;
}



void FUN_0005fb52(void)

{
  char cVar1;
  ushort uVar2;
  
  uVar2 = 0;
  DAT_fff91480 = 1;
  DAT_fff92480 = 1;
  for (; ((cVar1 = DAT_fff914a4, cVar1 != '\0' || (cVar1 = DAT_fff924a4, cVar1 != '\0')) &&
         (uVar2 < DAT_00030f24)); uVar2 = uVar2 + 1) {
    f33_spin_wait(1);
  }
  return;
}



int FUN_0005fb96(uint param_1)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3e;
  uVar4 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f28;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  if (param_1 < 2) {
    do {
      iVar3 = (int)uVar4;
      if (bVar2 <= bVar10) break;
      FUN_0005fb52();
      iVar3 = (int)uVar4;
      bVar1 = iVar8 != 0;
      iVar8 = 0;
      if (bVar1) {
        for (uVar5 = 0; (int)(param_1 + uVar5 + -9) < 0; uVar5 = uVar5 + 2 & 0xff) {
          if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff91200u + (uint32_t)(param_1 + uVar5) * 4u)))) & 0x7ff8) * 2 < uVar6) {
            iVar8 = 0x5a;
          }
        }
      }
      bVar1 = iVar7 != 0;
      iVar7 = 0;
      if (bVar1) {
        for (uVar5 = 0; (int)(param_1 + uVar5 + -10) < 0; uVar5 = uVar5 + 2 & 0xff) {
          if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff92200u + (uint32_t)(param_1 + uVar5) * 4u)))) & 0x7ff8) * 2 < uVar6) {
            iVar7 = 0x5a;
          }
        }
      }
      if ((iVar8 == 0) && (iVar7 == 0)) {
        iVar9 = 0;
      }
      bVar10 = bVar10 + 1;
    } while (iVar9 != 0);
    (*((byte *)camry_host_ptr((uint32_t)(param_1 + iVar3 + -0x7ffc)))) = bVar10;
    iVar8 = iVar9;
  }
  return iVar8;
}



void FUN_0005fc3c(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 0x80000004;
  DAT_fff923c8 = 0x80000004;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2 & 0xff;
    *(uint *)(((undefined *)camry_host_ptr(0xfff91004u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff91004u)) + iVar1) | 0x10000;
  } while ((int)(uVar2 - 8) < 0);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2 & 0xff;
    *(uint *)(((undefined *)camry_host_ptr(0xfff92004u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff92004u)) + iVar1) | 0x10000;
  } while ((int)(uVar2 - 9) < 0);
  return;
}



int FUN_0005fc94(void)

{
  bool bVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  undefined8 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3d;
  uVar5 = 0xfebeb800;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f26;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  do {
    iVar4 = (int)uVar5;
    if (bVar2 <= bVar10) break;
    FUN_0005fb52();
    iVar4 = (int)uVar5;
    bVar1 = iVar8 != 0;
    iVar8 = 0;
    if (bVar1) {
      uVar3 = 0;
      do {
        if (uVar6 < (*(uint *)(((undefined *)camry_host_ptr(0xfff91204u)) + uVar3 * 4) & 0x7ff8) * 2) {
          iVar8 = 0x5a;
        }
        uVar3 = uVar3 + 2 & 0xff;
      } while ((int)(uVar3 - 8) < 0);
    }
    bVar1 = iVar7 != 0;
    iVar7 = 0;
    if (bVar1) {
      uVar3 = 0;
      do {
        if (uVar6 < (*(uint *)(((undefined *)camry_host_ptr(0xfff92204u)) + uVar3 * 4) & 0x7ff8) * 2) {
          iVar7 = 0x5a;
        }
        uVar3 = uVar3 + 2 & 0xff;
      } while ((int)(uVar3 - 9) < 0);
    }
    if ((iVar8 == 0) && (iVar7 == 0)) {
      iVar9 = 0;
    }
    bVar10 = bVar10 + 1;
  } while (iVar9 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar4 + -0x7ff7)))) = bVar10;
  return iVar9;
}



void FUN_0005fd2e(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  DAT_fff913c4 = 0;
  uVar2 = 0;
  DAT_fff923c4 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar1) & 0xfffcffff;
  } while (uVar2 < 9);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(uint *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar1) & 0xfffcffff;
  } while (uVar2 < 10);
  return;
}



void FUN_0005fdd8(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 0x80000004;
  DAT_fff923c8 = 0x80000004;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2;
    *(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar1) | 0x10000;
  } while (uVar2 < 9);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2;
    *(uint *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar1) | 0x10000;
  } while (uVar2 < 10);
  return;
}



int FUN_0005fe24(void)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3d;
  uVar4 = 0xfebeb800;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f26;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  do {
    iVar3 = (int)uVar4;
    if (bVar2 <= bVar10) break;
    FUN_0005fb52();
    iVar3 = (int)uVar4;
    bVar1 = iVar8 != 0;
    iVar8 = 0;
    if (bVar1) {
      uVar5 = 0;
      do {
        if (uVar6 < ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff91200u + (uint32_t)(uVar5) * 4u)))) & 0x7ff8) * 2) {
          iVar8 = 0x5a;
        }
        uVar5 = uVar5 + 2;
      } while (uVar5 < 9);
    }
    bVar1 = iVar7 != 0;
    iVar7 = 0;
    if (bVar1) {
      uVar5 = 0;
      do {
        if (uVar6 < ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff92200u + (uint32_t)(uVar5) * 4u)))) & 0x7ff8) * 2) {
          iVar7 = 0x5a;
        }
        uVar5 = uVar5 + 2;
      } while (uVar5 < 10);
    }
    if ((iVar8 == 0) && (iVar7 == 0)) {
      iVar9 = 0;
    }
    bVar10 = bVar10 + 1;
  } while (iVar9 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar3 + -0x7ff8)))) = bVar10;
  return iVar9;
}



void FUN_0005ff08(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = 0;
  do {
    iVar2 = uVar1 * 4;
    uVar1 = uVar1 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar2) = *(undefined4 *)(((undefined *)camry_host_ptr(0x30f74u)) + iVar2);
  } while (uVar1 < 9);
  uVar1 = 0;
  do {
    iVar2 = uVar1 * 4;
    uVar1 = uVar1 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar2) = *(undefined4 *)(((undefined *)camry_host_ptr(0x30f4cu)) + iVar2);
  } while (uVar1 < 10);
  DAT_fff91494 = 0;
  DAT_fff92494 = 0;
  DAT_fff91498 = 8;
  DAT_fff92498 = 9;
  DAT_fff9149c = 0;
  DAT_fff9249c = 0;
  DAT_fff91490 = 0;
  DAT_fff92490 = 0;
  iVar2 = FUN_0005fd82();
  iVar3 = FUN_0005feb2();
  if ((iVar2 == 0) && (iVar3 == 0)) {
    DAT_fff913d8 = 4;
    DAT_fff923d8 = 4;
    return;
  }
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_0005ff98(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfff91000u)) + iVar1) = *(undefined4 *)(((undefined *)camry_host_ptr(0x30f98u)) + iVar1);
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfff92000u)) + iVar1) = *(undefined4 *)(((undefined *)camry_host_ptr(0x30ff8u)) + iVar1);
  } while (uVar3 < 0x18);
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 8;
    iVar2 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31059u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31081u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105au + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31082u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff9149cu + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31058u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff9249cu + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31080u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 5);
  DAT_fff91408 = 0;
  DAT_fff92408 = 0;
  DAT_fff91434 = 0;
  DAT_fff92434 = 0;
  DAT_fff91430 = 0x1a;
  DAT_fff92430 = 0xe;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 8;
    iVar2 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105bu + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31083u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 5);
  DAT_fff91420 = 0x32;
  DAT_fff92420 = 0x32;
  DAT_fff91424 = 0;
  DAT_fff92424 = 0;
  return;
}


