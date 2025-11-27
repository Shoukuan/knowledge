* Wide band Macro model for project = 0000_CPA_Sim_1

* Remove the _WB from the file name to use it.
* This file is invalid if spiceModel_WT.sp is not present in the same folder

.include spiceModel_WT.sp

.subckt a0000_CPA_Sim_1
+ FCHIP_VDD_15_Group_0 FCHIP_VDD_15_Group_1 FCHIP_VDD_15_Group_2
+ FCHIP_VDD_15_Group_3 Group_COMP1_part_COMP1_VDD_15_1 FCHIP_VSS_Group_0
+ FCHIP_VSS_Group_1 FCHIP_VSS_Group_2 FCHIP_VSS_Group_3
+ Group_COMP1_part_COMP1_VSS_2 BGA_VDD_15_SINK_ BGA_VSS_SINK_

V0 Group_COMP1_part_COMP1_VSS_2 0 0.0


xpackage
+ FCHIP_VDD_15_Group_0 FCHIP_VDD_15_Group_1 FCHIP_VDD_15_Group_2
+ FCHIP_VDD_15_Group_3 Group_COMP1_part_COMP1_VDD_15_1 FCHIP_VSS_Group_0
+ FCHIP_VSS_Group_1 FCHIP_VSS_Group_2 FCHIP_VSS_Group_3 BGA_VDD_15_SINK_
+ BGA_VSS_SINK_
+ package
.ends a0000_CPA_Sim_1
