# Freertos使用

[[野火]FreeRTOS 内核实现与应用开发实战—基于STM32](https://doc.embedfire.com/rtos/freertos/zh/latest/index.html)

[Freertos API引用](https://freertos.org/zh-cn-cmn-s/a00106.html)

## 创建项目

现在，所有必需的文件都已就绪，您需要创建一个项目（或 makefile）来成功构建这些文件。 很显然，这些文件只包含存根，所以还不会完成任何操作，但是一旦开始构建，就可以用工作函数逐渐替换存根。
该项目需要包含以下文件：

- Source/tasks.c  
- Source/Queue.c  
- Source/List.c  
- Source/portable/[compiler name]/[processor name]/port.c  
- Source/portable/MemMang/heap_1.c (or heap_2.c or heap_3.c or heap_4.c)  
- Demo/[processor name]/main.c  
- Demo/[Processor name]/ParTest/ParTest.c  

下列目录需要在包含路径中，请使用 Demo/[Process name] 目录中的相对路径-而不是绝对路径：  

- Demo/Common (i.e. ../Common)  
- Demo/[Processor Name]  
- Source/include  
- Source/portable/[Compiler name]/[Processor name]  

## 流缓冲区

字节流可以是任意长度，且并不一定具有开头或结尾。可以一次写入任意数量的字节，也可以一次读取任意数量的字节

```C
/* Structure that hold state information on the buffer. */
typedef struct StreamBufferDef_t                 /*lint !e9058 Style convention uses tag. */
{
    volatile size_t xTail;                       /* Index to the next item to read within the buffer. */
    volatile size_t xHead;                       /* Index to the next item to write within the buffer. */
    size_t xLength;                              /* The length of the buffer pointed to by pucBuffer. */
    size_t xTriggerLevelBytes;                   /* The number of bytes that must be in the stream buffer before a task that is waiting for data is unblocked. */
    volatile TaskHandle_t xTaskWaitingToReceive; /* Holds the handle of a task waiting for data, or NULL if no tasks are waiting. */
    volatile TaskHandle_t xTaskWaitingToSend;    /* Holds the handle of a task waiting to send data to a message buffer that is full. */
    uint8_t * pucBuffer;                         /* Points to the buffer itself - that is - the RAM that stores the data passed through the buffer. */
    uint8_t ucFlags;

    #if ( configUSE_TRACE_FACILITY == 1 )
        UBaseType_t uxStreamBufferNumber; /* Used for tracing purposes. */
    #endif

    #if ( configUSE_SB_COMPLETED_CALLBACK == 1 )
        StreamBufferCallbackFunction_t pxSendCompletedCallback;    /* Optional callback called on send complete. sbSEND_COMPLETED is called if this is NULL. */
        StreamBufferCallbackFunction_t pxReceiveCompletedCallback; /* Optional callback called on receive complete.  sbRECEIVE_COMPLETED is called if this is NULL. */
    #endif
} StreamBuffer_t;
```

### xstreamBufferSend()

注意：在 FreeRTOS 对象中唯一的流缓冲区实现 （消息缓冲区实现也是如此，因为消息缓冲区构建在 **假定只有一个任务或中断会写到 缓冲区（写入器），而且只有一个任务或中断会从 缓冲区（读取器）读取**。  
写入器和读取器为不同的任务或中断是安全的， 或中断，但与其他 FreeRTOS 对象不同， 拥有多个不同的编写器或多个不同的读取器是不安全的。  
**如果有 多个不同的写入器，那么应用程序写入器必须把对写入 API 函数（如 xStreamBufferSend()）的每个调用放在一个临界区内， 并使用发送阻塞时间 0。 同样，如果有多个不同的读取器， 那么应用程序必须把对读取 API 函数（如 xStreamBufferReceive()）的每个调用放在一个临界区内， 并使用接收阻塞时间 0**。  

## 消息缓冲区

可以将长度为 10、20 和 123 字节的消息写入消息缓冲区，或者从同一消息缓冲区中读取这些消息。10 字节的消息只能以 10 字节消息而不是单独字节的形式读取。  
消息缓冲区构建在流缓冲区实施之上。  
