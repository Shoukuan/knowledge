---
title: DDR4 初始化与校准
type: note
status: active
tags: ["DDR4", "存储", "初始化", "校准", "内存训练"]
aliases: ["DDR4初始化", "DDR training", "DDR calibration"]
sources: ["https://www.systemverilog.io/design/ddr4-initialization-and-calibration/"]
updated_at: 2026-05-01
---
# DDR4 初始化与校准

DDR4 上电到可操作需 4 个阶段。

## 阶段一：上电初始化

上电 → 释放 RESET → 激活 CKE → 使能差分时钟 → MRS 编程模式寄存器（频率、CL、CWL）→ ZQCL → IDLE

## 阶段二：ZQ 校准

每个 DQ 引脚背后有并联 ~240Ω 电阻 bank，因工艺偏差需精确调谐。

- `ZQ` 引脚接 **±1% 240Ω** 精密电阻作参考
- 比较器调整 VOH[0:4] 至输出 = VDDq/2
- 校准值分发到所有 DQ 引脚

**目的**：校准驱动强度（READ）和终端电阻（WRITE），适配不同 PCB 布局。

## 阶段三：Vref DQ 校准

DDR4 用 **POD（Pseudo Open Drain）** 替代 DDR3 SSTL。接收端依赖内部参考电压 `VrefDQ` 判断 0/1，通过 MR6 设置。

## 阶段四：读/写训练

### Write Leveling
MR1[7]=1 进入 leveling 模式：控制器发 DQS 脉冲 → DRAM 用 DQS 采样 CK 返回 → 调 DQS 延迟直到 0→1 跳变 → 锁定。

### Read Centering
找数据眼中心：发连续 READ → 调读延迟 → 定左/右边界 → 设在中心。

### Write Centering
WRITE→READ→SHIFT→COMPARE 循环：调写延迟 → 比较回读 → 确定有效范围 → DQ 对齐 DQS。

## 周期性校准

- **ZQCS**：定期重校电阻（温漂补偿）
- **周期性 Read Centering**：重算读延迟

## DDR4 vs DDR3

| | DDR3 | DDR4 |
|------|------|------|
| 端接 | SSTL/CTT | POD |
| 参考电压 | Vdd/2 外部分压 | 内部 VrefDQ |
| Bank | 8 banks | 16 banks (4×4) |
| 速率 | 800-2133 MT/s | 1600-3200+ MT/s |
