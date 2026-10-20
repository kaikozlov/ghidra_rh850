#include "common.h"

void snapshot_ecu_foreground_acquisition(void)

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
  DAT_febe6648 = ((int)(int16_t)DAT_febe7e3a);
  DAT_febe664a = ((int)(int16_t)DAT_febe7e3c);
  DAT_febe664c = ((int)(int16_t)DAT_febe7e3e);
  DAT_febe664e = ((int)(int16_t)DAT_febe7e40);
  DAT_febe6650 = ((int)(int16_t)DAT_febe7e42);
  DAT_febe6652 = ((int)(int16_t)DAT_febe7e44);
  DAT_febe6654 = ((int)(int16_t)DAT_febe7e46);
  DAT_febe6656 = ((int)(int16_t)DAT_febe7e48);
  DAT_febe6658 = ((int)(int16_t)DAT_febe7e4a);
  DAT_febe665a = ((int)(int16_t)DAT_febe7e4c);
  DAT_febe665c = ((int)(int16_t)DAT_febe7e4e);
  DAT_febe665e = ((int)(int16_t)DAT_febe7e50);
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
  DAT_febe6528 = six_channel_fit_work.state;
  DAT_febe6688 = ((int)(int16_t)DAT_febe7d4a);
  DAT_febe668a = ((int)(int16_t)DAT_febe7d4c);
  DAT_febe668c = ((int)(int16_t)DAT_febe7d4e);
  DAT_febe668e = ((int)(int16_t)DAT_febe7d50);
  DAT_febe6690 = ((int)(int16_t)DAT_febe7d54);
  DAT_febe6692 = ((int)(int16_t)DAT_febe7d56);
  DAT_febe6694 = ((int)(int16_t)DAT_febe7d58);
  DAT_febe6696 = ((int)(int16_t)DAT_febe7d5a);
  DAT_febe6698 = ((int)(int16_t)DAT_febe7d5c);
  DAT_febe669a = ((int)(int16_t)DAT_febe7d60);
  DAT_febe669c = ((int)(int16_t)DAT_febe7d62);
  DAT_febe669e = ((int)(int16_t)DAT_febe7d66);
  DAT_febe66a0 = DAT_febe7d68;
  DAT_febe64e0 = ((int)(int16_t)DAT_febe5f34);
  DAT_febe64e2 = ((int)(int16_t)DAT_febe5f36);
  DAT_febe64e4 = DAT_febe5f38;
  DAT_febe64e8 = DAT_febe5f40;
  DAT_febe64ec = DAT_febe5f44;
  DAT_febe66a4 = ((int)(int16_t)DAT_febe7ea8);
  DAT_febe652a = six_channel_fit_work.unsigned_max[0];
  DAT_febe66a6 = ((int)(int16_t)DAT_febe7eaa);
  DAT_febe652c = six_channel_fit_work.unsigned_max[1];
  DAT_febe6570 = six_channel_fit_work.second_center[5];
  DAT_febe652e = six_channel_fit_work.unsigned_max[2];
  DAT_febe6572 = six_channel_fit_work.component_angle[0];
  DAT_febe6530 = six_channel_fit_work.unsigned_max[3];
  DAT_febe6532 = six_channel_fit_work.unsigned_max[4];
  DAT_febe6574 = six_channel_fit_work.component_angle[1];
  DAT_febe6534 = six_channel_fit_work.unsigned_max[5];
  DAT_febe6576 = six_channel_fit_work.component_angle[2];
  DAT_febe6536 = six_channel_fit_work.unsigned_min[0];
  DAT_febe6538 = six_channel_fit_work.unsigned_min[1];
  DAT_febe653a = six_channel_fit_work.unsigned_min[2];
  DAT_febe653c = six_channel_fit_work.unsigned_min[3];
  DAT_febe653e = six_channel_fit_work.unsigned_min[4];
  DAT_febe6540 = six_channel_fit_work.unsigned_min[5];
  DAT_febe6542 = six_channel_fit_work.first_gain[0];
  DAT_febe6544 = six_channel_fit_work.first_gain[1];
  DAT_febe6546 = six_channel_fit_work.first_gain[2];
  DAT_febe6548 = six_channel_fit_work.first_gain[3];
  DAT_febe654a = six_channel_fit_work.first_gain[4];
  DAT_febe654c = six_channel_fit_work.first_gain[5];
  DAT_febe654e = six_channel_fit_work.first_center[0];
  DAT_febe6550 = six_channel_fit_work.first_center[1];
  DAT_febe6552 = six_channel_fit_work.first_center[2];
  DAT_febe6554 = six_channel_fit_work.first_center[3];
  DAT_febe6556 = six_channel_fit_work.first_center[4];
  DAT_febe6558 = six_channel_fit_work.first_center[5];
  DAT_febe655a = six_channel_fit_work.second_gain[0];
  DAT_febe655c = six_channel_fit_work.second_gain[1];
  DAT_febe655e = six_channel_fit_work.second_gain[2];
  DAT_febe6560 = six_channel_fit_work.second_gain[3];
  DAT_febe6562 = six_channel_fit_work.second_gain[4];
  DAT_febe6564 = six_channel_fit_work.second_gain[5];
  DAT_febe6566 = six_channel_fit_work.second_center[0];
  DAT_febe6568 = six_channel_fit_work.second_center[1];
  DAT_febe656a = six_channel_fit_work.second_center[2];
  DAT_febe656c = six_channel_fit_work.second_center[3];
  DAT_febe656e = six_channel_fit_work.second_center[4];
  DAT_febe66e6 = ((int)(int16_t)DAT_febe6e12);
  DAT_febe66e8 = ((int)(int16_t)DAT_febe6e14);
  DAT_febe66ea = ((int)(int16_t)DAT_febe6e16);
  DAT_febe66ec = ((int)(int16_t)DAT_febe6e18);
  DAT_febe66fc = DAT_febe6e28;
  DAT_febe6700 = DAT_febe6e2c;
  DAT_febe6704 = DAT_febe6e30;
  DAT_febe6708 = DAT_febe6e34;
  DAT_febe66ee = ((int)(int16_t)DAT_febe6e1a);
  DAT_febe66f0 = ((int)(int16_t)DAT_febe6e1c);
  DAT_febe66f2 = ((int)(int16_t)DAT_febe6e1e);
  DAT_febe66f4 = ((int)(int16_t)DAT_febe6e20);
  DAT_febe66f6 = ((int)(int16_t)DAT_febe6e22);
  DAT_febe66f8 = ((int)(int16_t)DAT_febe6e24);
  DAT_febe66e0 = DAT_febe6e0c;
  DAT_febe66e1 = DAT_febe6e0d;
  DAT_febe66e2 = DAT_febe6e0e;
  DAT_febe66e3 = DAT_febe6e0f;
  DAT_febe66e4 = DAT_febe6e10;
  DAT_febe66fa = ((int)(int16_t)DAT_febe6e26);
  DAT_febe6714 = DAT_febe6d78;
  DAT_febe670c = ((int)(int16_t)DAT_febe6d70);
  DAT_febe670e = ((int)(int16_t)DAT_febe6d72);
  DAT_febe6710 = ((int)(int16_t)DAT_febe6d74);
  DAT_febe6712 = ((int)(int16_t)DAT_febe6d76);
  DAT_febe6718 = ((int)(int16_t)DAT_febe6e00);
  DAT_febe671c = ((int)(int16_t)DAT_febe6d7c);
  DAT_febe671e = ((int)(int16_t)DAT_febe6d7e);
  DAT_febe6720 = ((int)(int16_t)DAT_febe6d80);
  DAT_febe6722 = ((int)(int16_t)DAT_febe6d82);
  DAT_febe6724 = ((int)(int16_t)DAT_febe6d84);
  DAT_febe6726 = ((int)(int16_t)DAT_febe6d86);
  DAT_febe65b0 = ((int)(int16_t)DAT_febe6c40);
  DAT_febe65b2 = ((int)(int16_t)DAT_febe6c42);
  DAT_febe65b4 = ((int)(int16_t)DAT_febe6c44);
  DAT_febe65b6 = ((int)(int16_t)DAT_febe6c46);
  DAT_febe65bc = DAT_febe6c60;
  DAT_febe65b8 = ((int)(int16_t)DAT_febe6c4a);
  return;
}

void copy_cell_block_5d5e0(void)

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
  DAT_febe64f0 = ((int)(int16_t)DAT_febe7dea);
  DAT_febe64f2 = ((int)(int16_t)DAT_febe7dec);
  DAT_febe64f4 = ((int)(int16_t)DAT_febe7dee);
  DAT_febe64f6 = ((int)(int16_t)DAT_febe7df0);
  DAT_febe64f8 = ((int)(int16_t)DAT_febe7df2);
  DAT_febe64fa = ((int)(int16_t)DAT_febe7df4);
  DAT_febe64fc = ((int)(int16_t)DAT_febe7df6);
  DAT_febe64fe = ((int)(int16_t)DAT_febe7df8);
  DAT_febe66a8 = ((int)(int16_t)DAT_febe7e0c);
  DAT_febe675c = DAT_febe7bfc;
  DAT_febe6770 = ((int)(int16_t)DAT_febee408);
  DAT_febe6772 = ((int)(int16_t)DAT_febee40a);
  DAT_febe6774 = ((int)(int16_t)DAT_febee40c);
  DAT_febe6776 = ((int)(int16_t)DAT_febee40e);
  DAT_febe6768 = DAT_febee400;
  DAT_febe6778 = ((int)(int16_t)DAT_febee410);
  DAT_febe677a = ((int)(int16_t)DAT_febee412);
  DAT_febe6769 = DAT_febee401;
  DAT_febe676a = DAT_febee402;
  DAT_febe676b = DAT_febee403;
  DAT_febe676c = DAT_febee404;
  DAT_febe677c = ((int)(int16_t)DAT_febee414);
  DAT_febe676d = DAT_febee405;
  DAT_febe677e = ((int)(int16_t)DAT_febee416);
  DAT_febe676e = DAT_febee406;
  DAT_febe6780 = DAT_febee418;
  DAT_febe676f = DAT_febee407;
  return;
}

void snapshot_monitor_inputs(void)

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
  DAT_febe64cc = output_request_status;
  DAT_febe64c8 = ((volatile uint8_t *)camry_host_ptr(0xfebe8b24u))[0];
  DAT_febe64c9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b24u + (uint32_t)(1) * 1u))));
  DAT_febe6618 = DAT_febe8b18;
  DAT_febe64d4 = DAT_febe8ae4;
  DAT_febe64d0 = DAT_febe8ac8;
  DAT_febe64d1 = DAT_febe8acb;
  DAT_febe661c = DAT_febe8af0;
  DAT_febe64dc = channel_request_state.observed_mismatch;
  DAT_febe64d8 = channel_request_state.channel0_state;
  DAT_febe64d9 = channel_request_state.channel1_state;
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
  DAT_febe6750 = ((volatile uint8_t *)camry_host_ptr(0xfebe79dcu))[0];
  DAT_febe6751 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(1) * 1u))));
  DAT_febe6752 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(2) * 1u))));
  DAT_febe6753 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(3) * 1u))));
  DAT_febe6754 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(4) * 1u))));
  DAT_febe6755 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(5) * 1u))));
  DAT_febe6756 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(6) * 1u))));
  DAT_febe6757 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(7) * 1u))));
  DAT_febe6759 = DAT_febe79e5;
  DAT_febe6758 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(8) * 1u))));
  DAT_febe65c8 = ((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0];
  DAT_febe65c9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u))));
  DAT_febe65ca = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(2) * 1u))));
  DAT_febe65cb = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u))));
  DAT_febe65cc = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(4) * 1u))));
  DAT_febe65cd = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(5) * 1u))));
  DAT_febe65ce = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u))));
  DAT_febe65cf = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u))));
  DAT_febe65d0 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u))));
  DAT_febe65d1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u))));
  DAT_febe65d2 = DAT_febe7566;
  DAT_febe65d3 = DAT_febe7567;
  DAT_febe65d4 = DAT_febe7568;
  DAT_febe65d7 = DAT_febe7575;
  DAT_febe65d5 = DAT_febe7569;
  DAT_febe65d6 = DAT_febe7574;
  DAT_febe65dc = DAT_febe7578;
  DAT_febe65d8 = ((int)(int16_t)DAT_febe7576);
  DAT_febe65e0 = ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0];
  DAT_febe65e1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u))));
  DAT_febe65e2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u))));
  DAT_febe65e3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u))));
  DAT_febe65e4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(4) * 1u))));
  DAT_febe65e5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(5) * 1u))));
  DAT_febe65e6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(6) * 1u))));
  DAT_febe65e7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(7) * 1u))));
  DAT_febe65e8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u))));
  DAT_febe65e9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u))));
  DAT_febe65eb = DAT_febe7cb7;
  DAT_febe65ea = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(10) * 1u))));
  DAT_febe65ec = DAT_febe7cb8;
  DAT_febe65ed = DAT_febe7cc4;
  DAT_febe65ee = DAT_febe7cc5;
  DAT_febe6760 = DAT_febe686c;
  DAT_febe6762 = ((int)(int16_t)DAT_febe6870);
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
  DAT_febe6502 = monitor_current_active_calibration.coefficients.negative_residual_gain[0];
  DAT_febe6504 = monitor_current_active_calibration.coefficients.negative_residual_gain[1];
  DAT_febe6506 = monitor_current_active_calibration.coefficients.negative_residual_gain[2];
  DAT_febe6508 = monitor_current_active_calibration.coefficients.negative_residual_gain[3];
  DAT_febe650a = monitor_current_active_calibration.coefficients.negative_residual_gain[4];
  DAT_febe650c = monitor_current_active_calibration.coefficients.negative_residual_gain[5];
  DAT_febe650e = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0];
  DAT_febe6510 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1];
  DAT_febe6512 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2];
  DAT_febe6514 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3];
  DAT_febe6516 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4];
  DAT_febe6518 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5];
  DAT_febe651a = monitor_current_active_calibration.coefficients.bias[0];
  DAT_febe651c = monitor_current_active_calibration.coefficients.bias[1];
  DAT_febe651e = monitor_current_active_calibration.coefficients.bias[2];
  DAT_febe6520 = monitor_current_active_calibration.coefficients.bias[3];
  DAT_febe6522 = monitor_current_active_calibration.coefficients.bias[4];
  DAT_febe6500 = monitor_current_active_calibration.changed;
  DAT_febe6524 = monitor_current_active_calibration.coefficients.bias[5];
  DAT_febe6501 = monitor_current_active_calibration.range_error;
  DAT_febe657a = published_fit_coefficients.first_center[0];
  DAT_febe657c = published_fit_coefficients.first_center[1];
  DAT_febe657e = published_fit_coefficients.first_center[2];
  DAT_febe6580 = published_fit_coefficients.first_center[3];
  DAT_febe6582 = published_fit_coefficients.first_center[4];
  DAT_febe6584 = published_fit_coefficients.first_center[5];
  DAT_febe6586 = published_fit_coefficients.first_gain[0];
  DAT_febe6588 = published_fit_coefficients.first_gain[1];
  DAT_febe658a = published_fit_coefficients.first_gain[2];
  DAT_febe658c = published_fit_coefficients.first_gain[3];
  DAT_febe658e = published_fit_coefficients.first_gain[4];
  DAT_febe6590 = published_fit_coefficients.first_gain[5];
  DAT_febe6592 = published_fit_coefficients.second_center[0];
  DAT_febe6594 = published_fit_coefficients.second_center[1];
  DAT_febe6596 = published_fit_coefficients.second_center[2];
  DAT_febe6598 = published_fit_coefficients.second_center[3];
  DAT_febe659a = published_fit_coefficients.second_center[4];
  DAT_febe659c = published_fit_coefficients.second_center[5];
  DAT_febe659e = published_fit_coefficients.second_gain[0];
  DAT_febe65a0 = published_fit_coefficients.second_gain[1];
  DAT_febe65a2 = published_fit_coefficients.second_gain[2];
  DAT_febe65a4 = published_fit_coefficients.second_gain[3];
  DAT_febe65a6 = published_fit_coefficients.second_gain[4];
  DAT_febe65a8 = published_fit_coefficients.second_gain[5];
  DAT_febe65aa = published_fit_coefficients.component_angle[0];
  DAT_febe65ac = published_fit_coefficients.component_angle[1];
  DAT_febe65ae = published_fit_coefficients.component_angle[2];
  DAT_febe6578 = DAT_febe6a24;
  DAT_febe6579 = DAT_febe6a25;
  DAT_febe66c8 = ((int)(int16_t)DAT_febe689a);
  DAT_febe66ca = ((int)(int16_t)DAT_febe689c);
  DAT_febe66cc = ((int)(int16_t)DAT_febe689e);
  DAT_febe66ce = ((int)(int16_t)DAT_febe68a0);
  DAT_febe66d0 = ((int)(int16_t)DAT_febe68a2);
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
  DAT_febe678c = ((int)(int16_t)DAT_febee608);
  DAT_febe6784 = DAT_febee600;
  DAT_febe6794 = DAT_febee610;
  DAT_febe6785 = DAT_febee601;
  DAT_febe6786 = DAT_febee602;
  DAT_febe6787 = DAT_febee603;
  DAT_febe678e = DAT_febee60a;
  DAT_febe6788 = DAT_febee604;
  DAT_febe6789 = DAT_febee605;
  DAT_febe678a = DAT_febee606;
  DAT_febe6790 = ((int)(int16_t)DAT_febee60c);
  return;
}

void dispatch_acquisition_and_fit_mode_entry_bit0_5dc7e(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  if (0xff < param_2) {
    uVar1 = param_1 & 1;
    if (param_3 < 0x100) {
      reset_current_control_even_call_flag_56684();
      if (uVar1 != 0) {
        update_current_control_even_call_flag_5668a();
      }
      reset_current_control_four_call_gate_566f0();
      if (uVar1 != 0) {
        update_current_control_four_call_gate_566fa();
      }
      return_only_stub_50b68();
      if (uVar1 != 0) {
        copy_acquisition_banks_to_application();
      }
      return_only_stub_50bba();
      if (uVar1 != 0) goto LAB_0005dcda;
    }
    else if (uVar1 != 0) {
      update_current_control_even_call_flag_5668a();
      update_current_control_four_call_gate_566fa();
      copy_acquisition_banks_to_application();
LAB_0005dcda:
      copy_serial_acquisition_to_application();
    }
  }
  if (0x100 < param_2) {
    uVar1 = param_1 & 1;
    if (param_3 < 0x101) {
      fill_constant_block_486aa();
      if (uVar1 != 0) {
        condition_measured_phase_currents();
      }
      thunk_seed_selected_electrical_angle_words_47d78();
      if (uVar1 != 0) {
        update_electrical_angle_feedback();
      }
      clear_wrapped_value_7d74_47d34();
      if (uVar1 != 0) {
        wrap_signed_value_by_06660000_47d3a();
      }
      fill_constant_block_47b3c();
      if (uVar1 != 0) {
        compute_shifted_angle_polynomial_pairs_47b70();
      }
      fill_constant_block_47ea4();
      if (uVar1 != 0) {
        update_wrapped_difference_and_fixed_point_filter_47eb8();
      }
      clear_negated_ratio_filter_history_4963e();
      if (uVar1 != 0) goto LAB_0005dd4c;
    }
    else if (uVar1 != 0) {
      condition_measured_phase_currents();
      update_electrical_angle_feedback();
      wrap_signed_value_by_06660000_47d3a();
      compute_shifted_angle_polynomial_pairs_47b70();
      update_wrapped_difference_and_fixed_point_filter_47eb8();
LAB_0005dd4c:
      filter_negated_scaled_signed_ratio_4964c();
    }
  }
  if (param_2 - 0x200 < 0x323) {
    uVar1 = param_1 & 1;
    if (param_3 - 0x200 < 0x323) {
      if (uVar1 != 0) {
        accumulate_paired_source_difference_counts();
        step_channel_difference_latch_a();
LAB_0005dd96:
        step_channel_difference_latch_b();
      }
    }
    else {
      clear_754f_through_7552_flags_3e0b4();
      if (uVar1 != 0) {
        accumulate_paired_source_difference_counts();
      }
      fill_constant_block_4246e();
      if (uVar1 != 0) {
        step_channel_difference_latch_a();
      }
      fill_constant_block_43430();
      if (uVar1 != 0) goto LAB_0005dd96;
    }
  }
  if (param_2 == 0x512) {
    if (param_3 != 0x512) {
      return_only_stub_32d24();
    }
    if ((param_1 & 1) != 0) {
      step_six_channel_fit();
    }
  }
  if (param_2 == 0x600) {
    uVar1 = param_1 & 1;
    if (param_3 == 0x600) {
      if (uVar1 == 0) goto LAB_0005dde6;
      step_mode600_stimulus_fit();
    }
    else {
      initialize_mode600_stimulus_fit();
      if (uVar1 != 0) {
        step_mode600_stimulus_fit();
      }
      return_only_stub_32d24();
      if (uVar1 == 0) goto LAB_0005dde6;
    }
    step_six_channel_fit();
  }
LAB_0005dde6:
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      initialize_terminal_output_ramp();
    }
    if ((param_1 & 1) != 0) {
      step_terminal_output_ramp();
    }
  }
  return;
}

void update_mode_owned_current_feedback(uint workmask,ushort mode,ushort previous_mode)

{
  uint uVar1;
  
  if (0x1ff < mode) {
    uVar1 = workmask & 1;
    if (previous_mode < 0x200) {
      return_only_stub_36142();
      if (uVar1 != 0) {
        transform_measured_phase_currents();
      }
      return_only_stub_38faa();
      if (uVar1 != 0) {
        refresh_current_reference_envelope_qualification();
      }
      initialize_bank0_current_reference_feedback();
      if (uVar1 != 0) {
        update_bank0_current_reference_feedback();
      }
      initialize_bank1_current_reference_feedback();
      if (uVar1 == 0) goto LAB_0005de62;
    }
    else {
      if (uVar1 == 0) goto LAB_0005de62;
      transform_measured_phase_currents();
      refresh_current_reference_envelope_qualification();
      update_bank0_current_reference_feedback();
    }
    update_bank1_current_reference_feedback();
  }
LAB_0005de62:
  if (0x100 < mode) {
    if (previous_mode < 0x101) {
      initialize_output_code_limit_requests();
    }
    if ((workmask & 1) != 0) {
      reduce_phase_output_code_limits();
    }
  }
  publish_current_control_snapshot();
  return;
}

void dispatch_acquisition_and_fit_mode_step_bit0_5de82(uint param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if ((0xff < param_2) && ((param_1 & 1) != 0)) {
    update_current_control_even_call_flag_5668a();
    update_current_control_four_call_gate_566fa();
    copy_acquisition_banks_to_application();
    copy_serial_acquisition_to_application();
  }
  if ((0x100 < param_2) && ((param_1 & 1) != 0)) {
    condition_measured_phase_currents();
    update_electrical_angle_feedback();
    wrap_signed_value_by_06660000_47d3a();
    compute_shifted_angle_polynomial_pairs_47b70();
    update_wrapped_difference_and_fixed_point_filter_47eb8();
    filter_negated_scaled_signed_ratio_4964c();
  }
  if ((param_2 - 0x200 < 0x323) && ((param_1 & 1) != 0)) {
    accumulate_paired_source_difference_counts();
    step_channel_difference_latch_a();
    step_channel_difference_latch_b();
  }
  if ((param_2 == 0x512) && ((param_1 & 1) != 0)) {
    step_six_channel_fit();
  }
  if ((param_2 == 0x600) && ((param_1 & 1) != 0)) {
    step_mode600_stimulus_fit();
    step_six_channel_fit();
  }
  if ((0x1ff < param_2) && ((param_1 & 1) != 0)) {
    step_terminal_output_ramp();
  }
  return;
}

void update_steady_current_feedback(uint workmask,ushort mode)

{
  if ((0x1ff < mode) && ((workmask & 1) != 0)) {
    transform_measured_phase_currents();
    refresh_current_reference_envelope_qualification();
    update_bank0_current_reference_feedback();
    update_bank1_current_reference_feedback();
  }
  if ((0x100 < mode) && ((workmask & 1) != 0)) {
    reduce_phase_output_code_limits();
  }
  publish_current_control_snapshot();
  return;
}

void return_only_stub_5df5a(void)

{
  return;
}

void dispatch_current_control_mode_entry_bit1_5df5c(uint param_1,ushort param_2,ushort param_3)

{
  uint uVar1;
  
  if (0x1ff < param_2) {
    uVar1 = param_1 & 2;
    if (param_3 < 0x200) {
      return_only_stub_387cc();
      if (uVar1 != 0) {
        latch_current_feedback_and_reference_inputs();
      }
      return_only_stub_387b8();
      if (uVar1 != 0) {
        reset_6e04_flags_and_snapshot_6af4_387ba();
      }
      initialize_eight_gain_filters_and_counters_3798c();
      if (uVar1 != 0) {
        select_and_filter_eight_control_gains_37a92();
      }
      return_only_stub_37e46();
      if (uVar1 != 0) {
        compose_current_feedback();
      }
      return_only_stub_38676();
      if (uVar1 != 0) {
        lookup_6d78_6d70_signed_five_map_signal_3879e();
      }
      return_only_stub_38500();
      if (uVar1 != 0) {
        map_sampled_command_to_base_first_current();
      }
      return_only_stub_37f90();
      if (uVar1 != 0) {
        select_feedback_bounded_first_current_request();
      }
      return_only_stub_38580();
      if (uVar1 != 0) {
        update_additional_first_current_request();
      }
      return_only_stub_3835c();
      if (uVar1 != 0) {
        select_actual_and_feedback_first_current_baselines();
      }
      return_only_stub_38394();
      if (uVar1 != 0) {
        map_first_current_command_with_6e0a_sign_384d8();
      }
      return_only_stub_38160();
      if (uVar1 != 0) {
        calculate_sixfold_current_correction();
      }
      return_only_stub_37f14();
      if (uVar1 != 0) {
        publish_corrected_current_reference_pairs();
      }
      clear_6e58_three_component_vector_38a4c();
      if (uVar1 != 0) {
        transform_summed_pairs_to_three_saturated_components_38a58();
      }
      clear_6e60_three_component_vector_38b5e();
      if (uVar1 != 0) {
        transform_differenced_pairs_to_three_saturated_components_38b6a();
      }
      fill_constant_block_37218();
      if (uVar1 != 0) {
        update_coupled_common_error_accumulator_37228();
      }
      fill_constant_block_370d6();
      if (uVar1 != 0) {
        update_clamped_differential_error_accumulator_370e6();
      }
      fill_constant_block_3759c();
      if (uVar1 != 0) {
        run_or_reset_6ccc_error_accumulator_3777e();
      }
      fill_constant_block_373be();
      if (uVar1 != 0) {
        run_or_reset_6ca0_error_accumulator_37538();
      }
      initialize_first_regulator_output_envelope_36910();
      if (uVar1 != 0) {
        compose_regulator_output_bank0();
      }
      initialize_second_regulator_output_envelope_36c1c();
      if (uVar1 != 0) {
        compose_regulator_output_bank1();
      }
      return_only_stub_377ec();
      if (uVar1 != 0) {
        refresh_shared_second_axis_envelope();
      }
      return_only_stub_378d2();
      if (uVar1 != 0) {
        apply_shared_second_axis_envelope();
      }
      return_only_stub_36f24();
      if (uVar1 != 0) {
        filter_weighted_envelope_sum_and_scale_four_outputs_36f26();
      }
      clear_6e68_three_component_vector_38c70();
      if (uVar1 != 0) {
        transform_first_regulated_phase_commands();
      }
      clear_6e70_three_component_vector_38d60();
      if (uVar1 != 0) {
        transform_second_regulated_phase_commands();
      }
      return_only_stub_37c4a();
      if (uVar1 != 0) {
        select_phase_modulation_modes();
      }
      clear_6be4_state_368aa();
      if (uVar1 != 0) {
        map_phase_compensation_gain();
      }
      return_only_stub_36676();
      if (uVar1 != 0) {
        refresh_phase_compensation_amplitude();
      }
      return_only_stub_3674e();
      if (uVar1 != 0) {
        compensate_first_regulated_phases();
      }
      return_only_stub_367fc();
      if (uVar1 != 0) {
        compensate_second_regulated_phases();
      }
      clear_6e40_and_6e44_states_38838();
      if (uVar1 != 0) {
        modulate_first_phase_triplet();
      }
      clear_6e50_and_6e54_states_38942();
      if (uVar1 != 0) {
        modulate_second_phase_triplet();
      }
      return_only_stub_38e50();
LAB_0005e1ae:
      if (uVar1 != 0) {
        publish_current_output_slot();
      }
    }
    else if (uVar1 != 0) {
      latch_current_feedback_and_reference_inputs();
      reset_6e04_flags_and_snapshot_6af4_387ba();
      select_and_filter_eight_control_gains_37a92();
      compose_current_feedback();
      lookup_6d78_6d70_signed_five_map_signal_3879e();
      map_sampled_command_to_base_first_current();
      select_feedback_bounded_first_current_request();
      update_additional_first_current_request();
      if (uVar1 != 0) {
        select_actual_and_feedback_first_current_baselines();
        map_first_current_command_with_6e0a_sign_384d8();
        calculate_sixfold_current_correction();
        publish_corrected_current_reference_pairs();
        transform_summed_pairs_to_three_saturated_components_38a58();
        transform_differenced_pairs_to_three_saturated_components_38b6a();
        if (uVar1 != 0) {
          update_coupled_common_error_accumulator_37228();
          update_clamped_differential_error_accumulator_370e6();
          run_or_reset_6ccc_error_accumulator_3777e();
          run_or_reset_6ca0_error_accumulator_37538();
          compose_regulator_output_bank0();
          compose_regulator_output_bank1();
          if (uVar1 != 0) {
            refresh_shared_second_axis_envelope();
            apply_shared_second_axis_envelope();
            filter_weighted_envelope_sum_and_scale_four_outputs_36f26();
            transform_first_regulated_phase_commands();
            if (uVar1 != 0) {
              transform_second_regulated_phase_commands();
              select_phase_modulation_modes();
              map_phase_compensation_gain();
              refresh_phase_compensation_amplitude();
              compensate_first_regulated_phases();
              compensate_second_regulated_phases();
              modulate_first_phase_triplet();
              modulate_second_phase_triplet();
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
      initialize_phase_output_slots();
      if (param_1 != 0) {
        select_phase_output_slots();
      }
      fill_constant_block_5745a();
      if (param_1 != 0) {
        stage_phase_output_history();
      }
      return_only_stub_57dee();
      if (param_1 == 0) goto LAB_0005e1f8;
    }
    else {
      if (param_1 == 0) goto LAB_0005e1f8;
      select_phase_output_slots();
      stage_phase_output_history();
    }
    stage_live_phase_halfword_compares();
  }
LAB_0005e1f8:
  publish_current_control_snapshot();
  return;
}
