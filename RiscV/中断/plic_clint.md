# PLIC CLINT

CLINT is a name we have used at SiFive to cover the local interrupts described in the privileged architecture standard v1.10, including the software interrupts, the timer interrupts, the external interrupt (which is usually in turn connected to a PLIC), and any additional local interrupts made visible in the mip/mie CSRs bits 16 and above. These same interrupt sources can now be also accessed via CLIC mode, which is a draft proposal with the Foundation.
