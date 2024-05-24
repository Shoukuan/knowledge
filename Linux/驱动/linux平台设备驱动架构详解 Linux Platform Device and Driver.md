# linux平台设备驱动架构详解 Linux Platform Device and Driver

[linux平台设备驱动架构详解 Linux Platform Device and Driver](https://blog.csdn.net/STN_LCD/article/details/78743422)

### platform总线下的驱动编写流程

- 首先定义一个platform_driver结构体变量

- 然后实现结构体中各个成员变量，重点是实现匹配方式以及probe函数

- 当我们定义并初始化好platform_driver结构体变量以后，需要在驱动入口函数里面调用platform_driver_register函数向内核注册一个platform驱动

- 驱动卸载函数中通过platform_driver_unregister函数卸载

框架流程如下

```C
struct xxx_dev{

        struct cdev cdev;
        /* 设备结构体其他具体内容 */
};

struct xxx_dev xxxdev; /*定义个设备结构体变量*/

static int xxx_open(struct inode *inode, struct file*filp)
{

        /* 函数具体内容 */
        return 0;
}

static ssize_t xxx_write(struct file *filp, const char __user*buf,
size_t cnt, loff_t *offt)
{

        /* 函数具体内容 */
        return 0;
}

/*

* 字符设备驱动操作集
*/
static struct file_operations xxx_fops = {

        .owner = THIS_MODULE,
         .open = xxx_open,
        .write = xxx_write,

};

/*

* platform 驱动的 probe 函数
* 驱动与设备匹配成功以后此函数就会执行
*/
static int xxx_probe(struct platform_device*dev)
{

        ......
        cdev_init(&xxxdev.cdev, &xxx_fops); /* 注册字符设备驱动 */
        /* 函数具体内容 */
        return 0;

}

static int xxx_remove(struct platform_device *dev)
{

        ......
        cdev_del(&xxxdev.cdev);/* 删除 cdev */
        /* 函数具体内容 */
        return 0;
}
/*匹配列表*/
static const struct of_device_id xxx_of_match[] = {

        {
         .compatible = "xxx-gpio" },
        {
         /* Sentinel */ }
};

/*

* platform 平台驱动结构体
*/
static struct platform_driver xxx_driver = {

        .driver = {

        .name = "xxx",
        .of_match_table = xxx_of_match,
        },
        .probe = xxx_probe,
        .remove = xxx_remove,

};

 /*驱动模块加载*/
static int __init xxxdriver_init(void)
{

        return platform_driver_register(&xxx_driver);
}

/*驱动模块卸载*/
static void __exit xxxdriver_exit(void)
{

         platform_driver_unregister(&xxx_driver);
}

 module_init(xxxdriver_init);
 module_exit(xxxdriver_exit);
 MODULE_LICENSE("GPL");
 MODULE_AUTHOR("yinwg");
```

### 以GPIO驱动为例

```DTS
/gpio_example {
    compatible = "mycompany,gpio-example";
    gpio_pin = <23>; /*使用的 GPIO 引脚编号*/
};
```

```C
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/cdev.h>
#include <linux/of.h>
#include <linux/of_device.h>

#define DEVICE_NAME "gpio_example"
#define CLASS_NAME "gpio_class"

static int gpio_pin;
static int major_number;
static struct class* gpio_class = NULL;
static struct cdev gpio_cdev;

static ssize_t gpio_read(struct file* filep, char* buffer, size_t len, loff_t* offset)
{
    int value = gpio_get_value(gpio_pin);
    char msg[2];

    msg[0] = value ? '1' : '0';
    msg[1] = '\n';

    if (copy_to_user(buffer, msg, 2)) {
        return -EFAULT;
    }

    return 2;
}

static ssize_t gpio_write(struct file* filep, const char* buffer, size_t len, loff_t* offset)
{
    char msg[2];

    if (copy_from_user(msg, buffer, len)) {
        return -EFAULT;
    }

    if (msg[0] == '1') {
        gpio_set_value(gpio_pin, 1);
    } else if (msg[0] == '0') {
        gpio_set_value(gpio_pin, 0);
    } else {
        return -EINVAL;
    }

    return len;
}

static struct file_operations fops = {
    .read = gpio_read,
    .write = gpio_write,
    .owner = THIS_MODULE,
};

static int gpio_probe(struct platform_device* pdev)
{
    struct device* dev = &pdev->dev;
    struct device_node* np = dev->of_node;
    int ret;

    if (!np) {
        dev_err(dev, "No device tree node found\n");
        return -EINVAL;
    }

    gpio_pin = of_get_named_gpio(np, "gpio_pin", 0);
    if (!gpio_is_valid(gpio_pin)) {
        dev_err(dev, "Invalid GPIO pin\n");
        return -EINVAL;
    }

    ret = gpio_request(gpio_pin, DEVICE_NAME);
    if (ret) {
        dev_err(dev, "Failed to request GPIO pin\n");
        return ret;
    }

    ret = gpio_direction_output(gpio_pin, 0);
    if (ret) {
        dev_err(dev, "Failed to set GPIO direction\n");
        gpio_free(gpio_pin);
        return ret;
    }

    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        dev_err(dev, "Failed to register character device\n");
        gpio_free(gpio_pin);
        return major_number;
    }

    gpio_class = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(gpio_class)) {
        unregister_chrdev(major_number, DEVICE_NAME);
        gpio_free(gpio_pin);
        return PTR_ERR(gpio_class);
    }

    if (!device_create(gpio_class, NULL, MKDEV(major_number, 0), NULL, DEVICE_NAME)) {
        class_destroy(gpio_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        gpio_free(gpio_pin);
        return -EINVAL;
    }

    cdev_init(&gpio_cdev, &fops);
    if (cdev_add(&gpio_cdev, MKDEV(major_number, 0), 1)) {
        device_destroy(gpio_class, MKDEV(major_number, 0));
        class_destroy(gpio_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        gpio_free(gpio_pin);
        return -EINVAL;
    }

    dev_info(dev, "GPIO example driver initialized\n");
    return 0;
}

static int gpio_remove(struct platform_device* pdev)
{
    cdev_del(&gpio_cdev);
    device_destroy(gpio_class, MKDEV(major_number, 0));
    class_destroy(gpio_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    gpio_free(gpio_pin);
    dev_info(&pdev->dev, "GPIO example driver removed\n");
    return 0;
}


static const struct of_device_id gpio_of_match[] = {
    { .compatible = "mycompany,gpio-example", },
    { /* Sentinel */ }
};
MODULE_DEVICE_TABLE(of, gpio_of_match);

static struct platform_driver gpio_driver = {
    .probe = gpio_probe,
    .remove = gpio_remove,
    .driver = {
        .name = DEVICE_NAME,
        .of_match_table = gpio_of_match,
    },
};
static int __init gpio_init(void)
{
    return platform_driver_register(&gpio_driver);
}

static void __exit gpio_exit(void)
{
    platform_driver_unregister(&gpio_driver);
}

module_init(gpio_init);
module_exit(gpio_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple GPIO platform driver example");
MODULE_VERSION("1.0");

```

### 设备树解析过程

kernel会为设备树root节点下所有带 compatible 属性的节点都分配并注册一个 platform_device 。 另外如果某个节点的compatible符合某些matches条件，则会为该节点下的所有带compatible属性的子节点(child) 也分配并注册一个platform_device

#### Platform_devce数据结构如下

```C
 struct platform_device {
    const char      *name;
    int             id;
    bool            id_auto;
    /* 以此挂入统一设备模型 */
    struct device   dev;
    u64             platform_dma_mask;
    /* io和irq资源的总数 */
    u32             num_resources;
    /* 指向resource数组 */
    struct resource*resource;

    const struct platform_device_id *id_entry;
};
```

#### 解析设备树以及生成platform_device的过程如下所示

```C
//第一层
/*kerner加载*/
start_kernel
--> arch_call_rest_init
    --> rest_init
        --> kernel_init
            --> kernel_init_freeable
                --> do_basic_setup
                    --> do_initcalls
                        --> of_platform_default_populate_init

//第二层
/*drivers/of/platform.c */
static int __init of_platform_default_populate_init(void)
{
        /* 检查of_root（"/"节点）是否为NULL*/
        if (!of_have_populated_dt())
                return -ENODEV;

        /* 进行实际的platform_device填充操作 */
        of_platform_default_populate(NULL, NULL, NULL);

        return 0;
}

/*在do_initcalls会被调用执行*/
arch_initcall_sync(of_platform_default_populate_init);

//第三层
const struct of_device_id of_default_bus_match_table[] = {
        { .compatible = "simple-bus", },
        { .compatible = "simple-mfd", },
        { .compatible = "isa", },
# ifdef CONFIG_ARM_AMBA
        { .compatible = "arm,amba-bus", },
# endif /*CONFIG_ARM_AMBA */
        {} /* Empty terminated list*/
};

int of_platform_default_populate(struct device_node *root,
                                 const struct of_dev_auxdata*lookup,
                                 struct device *parent)
{
        /* of_default_bus_match_table即为上述的matches条件，其他形参均为NULL */
        return of_platform_populate(root, of_default_bus_match_table, lookup,
                                    parent);
}
EXPORT_SYMBOL_GPL(of_platform_default_populate);

//第五层
int of_platform_populate(struct device_node *root,
                        const struct of_device_id*matches,
                        const struct of_dev_auxdata *lookup,
                        struct device*parent)
{
        struct device_node *child;
        int rc = 0;
        /* 传入的root为NULL，获取"/"节点 */
        root = root ? of_node_get(root) : of_find_node_by_path("/");
        /* 遍历"/"节点下所有的child节点 */
        for_each_child_of_node(root, child) {
                /* 分配并创建platform_device */
                rc = of_platform_bus_create(child, matches, lookup, parent, true);
                if (rc) {
                        of_node_put(child);
                        break;
                }
        }
        /* 设置已填充标志位，避免重复填充 */
        of_node_set_flag(root, OF_POPULATED_BUS);

        of_node_put(root);
        return rc;
}
EXPORT_SYMBOL_GPL(of_platform_populate);

//第六层
/* bus：root下的child节点

- matches：of_default_bus_match_table
- lookup：NULL
- parent：NULL
- strict：true
 */
static int of_platform_bus_create(struct device_node*bus,
                                  const struct of_device_id *matches,
                                  const struct of_dev_auxdata*lookup,
                                  struct device *parent, bool strict)
{
        const struct of_dev_auxdata*auxdata;
        struct device_node *child;
        struct platform_device*dev;
        const char *bus_id = NULL;
        void*platform_data = NULL;
        int rc = 0;

        /* 只为含"compatible"属性的节点创建platform_device */
        if (strict && (!of_get_property(bus, "compatible", NULL))) {
                return 0;
        }
        /* 跳过符合of_skipped_node_table条件的节点 */
        if (unlikely(of_match_node(of_skipped_node_table, bus))) {
                return 0;
        }
        /* 跳过已经创建过platform_device的节点 */
        if (of_node_check_flag(bus, OF_POPULATED_BUS)) {
                return 0;
        }
        /* 创建并填充platform_device */
        dev = of_platform_device_create_pdata(bus, bus_id, platform_data, parent);
        /* 1、创建platform_device失败，则直接返回，继续遍历root下其他child node
         * 2、创建platform_device成功，但当前node不符合matches条件，即compatible属性值
         *    不为"simple-bus"、"simple-mfd"、"isa"等时，也直接返回；否则继续为当前node
         *    下所有含compatible属性的child node创建并填充platform_device
         */
        if (!dev || !of_match_node(matches, bus))
                return 0;
        /* 遍历当前node下的所有child node */
        for_each_child_of_node(bus, child) {
                /* 递归调用of_platform_bus_create函数 */
                rc = of_platform_bus_create(child, matches, lookup, &dev->dev, strict);
                if (rc) {
                        of_node_put(child);
                        break;
                }
        }
        /* 设置已填充标志位：OF_POPULATED_BUS */
        of_node_set_flag(bus, OF_POPULATED_BUS);
        return rc;

}

//第七层
static struct platform_device *of_platform_device_create_pdata(
                                        struct device_node*np,
                                        const char *bus_id,
                                        void*platform_data,
                                        struct device *parent)
{
        struct platform_device *dev;
        /* of_device_is_available: 检查节点的status属性，如果没有该属性，或者属性值
         *                         为"ok"、"okay"，则认为该node是有效的
         */
        if (!of_device_is_available(np) ||
            of_node_test_and_set_flag(np, OF_POPULATED))
                return NULL;
        /* 创建platform_device结构体，并对结构体成员进行赋值:
         *如dev->dev.of_node = of_node_get(np)，即将当前的device_node结构体
         *      赋值给了platform_device->device.of_node成员，即完成绑定操作
         */
        dev = of_device_alloc(np, bus_id, parent);
        if (!dev)
                goto err_clear_flag;

        dev->dev.coherent_dma_mask = DMA_BIT_MASK(32);
        if (!dev->dev.dma_mask)
                dev->dev.dma_mask = &dev->dev.coherent_dma_mask;
        /* struct bus_type platform_bus_type = {
         *          .name           = "platform",
         *          .dev_groups     = platform_dev_groups,
         *          .match          = platform_match,
         *          .uevent         = platform_uevent,
         *          .dma_configure  = platform_dma_configure,
         *          .pm             = &platform_dev_pm_ops,
         * };
         * 设置struct device的总线类型，此后与platform_driver的匹配即是通过
         * platform_match函数
         */
        dev->dev.bus = &platform_bus_type;
        dev->dev.platform_data = platform_data;
        of_msi_configure(&dev->dev, dev->dev.of_node);
        /* 调用device_add加入统一设备模型 */
        if (of_device_add(dev) != 0) {
            ...
        }

        return dev;
}
```

至此，为所有设备树中符合条件的node都创建了platform_device结构体，node下描述的资源也解析到了platform_device 中，并通过i dev成员 将该node描述的设备加入了统一设备模型。

在统一设备模型中，每次device或者driver加入bus中，都会调用对应bus的match函数(如platform_match)对driver或者device 链表进行遍历，如有匹配项，则进入driver的probe函数。
