# start_kernel详解系列之【setup_arch】
<!-- TOC -->

- [文章目录](#)

<!-- TOC END -->


[start_kernel详解系列之【setup_arch】](https://blog.csdn.net/iriczhao/article/details/124083152)

## 文章目录

start_kernel详解系列之【setup_arch】
一、开篇
二、setup_arch函数分析
（2-1）配置处理器
（2-2）设置machine_desc结构变量参数和machine_name字符串
（2-3）设置init_mm结构的参数
（2-4）备份命令行参数
（2-5）设置linux启动早期参数
（2-6）页表初始化
（2-7）请求标准资源
（2-8）创建设备树节点
（2-9）构建cpu逻辑映射关系
（2-10）psci初始化
（2-11）对称多处理器下的初始化
（2-12）架构早期初始化
三、结尾

