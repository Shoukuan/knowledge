# 【原创】linux设备模型之kset/kobj/ktype分析
<!-- TOC -->


<!-- TOC END -->


[【原创】linux设备模型之kset/kobj/ktype分析](https://www.cnblogs.com/LoyenWang/p/13334196.html)

kobject代表内核对象，结构体本身不单独使用，而是嵌套在其他高层结构中，用于组织成拓扑关系；
sysfs文件系统中一个目录对应一个kobject；

**kset是包含多个kobject的集合；**
如果需要在sysfs的目录中包含多个子目录，那需要将它定义成一个kset；
kset结构体中包含struct kobject字段，可以使用该字段链接到更上一层的结构，用于构建更复杂的拓扑结构；
sysfs中的设备组织结构很大程度上根据kset组织的，/sys/bus目录就是一个kset对象

kobj_type用于表征kobject的类型，指定了删除kobject时要调用的函数

```C
# include <linux/kernel.h>
# include <linux/module.h>
# include <linux/slab.h>
# include <linux/kobject.h>

//自定义一个结构，包含了struct kobject子结构
struct test_kobj {
    int value;
    struct kobject kobj;
};

//自定义个属性结构体，包含了struct attribute结构
struct test_kobj_attribute {
    struct attribute attr;
    ssize_t (*show)(struct test_kobj *obj, struct test_kobj_attribute *attr, char *buf);
    ssize_t (*store)(struct test_kobj *obj, struct test_kobj_attribute *attr, const char *buf, size_t count);
};

//声明一个全局结构用于测试
struct test_kobj *obj;

//用于初始化sysfs_ops中的函数指针
static ssize_t test_kobj_attr_show(struct kobject *kobj, struct attribute *attr, char *buf)
{
    struct test_kobj_attribute *test_kobj_attr;
    ssize_t ret = -EIO;

    test_kobj_attr = container_of(attr, struct test_kobj_attribute, attr);
    
    //回调到具体的实现函数
    if (test_kobj_attr->show)
        ret = test_kobj_attr->show(container_of(kobj, struct test_kobj, kobj), test_kobj_attr, buf);
    
    return ret;
}

//用于初始化sysfs_ops中的函数指针
static ssize_t test_kobj_attr_store(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count)
{
    struct test_kobj_attribute *test_kobj_attr;
    ssize_t ret = -EIO;

    test_kobj_attr = container_of(attr, struct test_kobj_attribute, attr);
    
    //回调到具体的实现函数
    if (test_kobj_attr->store)
        ret = test_kobj_attr->store(container_of(kobj, struct test_kobj, kobj), test_kobj_attr, buf, count);
    
    return ret;
}

//用于初始化kobj_ktype
const struct sysfs_ops test_kobj_sysfs_ops = {
    .show = test_kobj_attr_show,
    .store = test_kobj_attr_store,
};

//用于初始化kobj_ktype，最终用于释放kobject
void obj_release(struct kobject *kobj)
{
    struct test_kobj *obj = container_of(kobj, struct test_kobj, kobj);

    printk(KERN_INFO "test kobject release %s\n", kobject_name(&obj->kobj));
    
    kfree(obj);
}

//定义kobj_ktype，用于指定kobject的类型，初始化的时候使用
static struct kobj_type test_kobj_ktype = {
    .release = obj_release,
    .sysfs_ops = &test_kobj_sysfs_ops,
};

//show函数的具体实现
ssize_t name_show(struct test_kobj *obj, struct test_kobj_attribute *attr, char *buffer)
{
    return sprintf(buffer, "%s\n", kobject_name(&obj->kobj));
}

//show函数的具体实现
ssize_t value_show(struct test_kobj *obj, struct test_kobj_attribute *attr, char *buffer)
{
    return sprintf(buffer, "%d\n", obj->value);
}

//store函数的具体实现
ssize_t value_store(struct test_kobj *obj, struct test_kobj_attribute *attr, const char *buffer, size_t size)
{
    sscanf(buffer, "%d", &obj->value);

    return size;
}

//定义属性，最终注册进sysfs系统
struct test_kobj_attribute name_attribute = __ATTR(name, 0664, name_show, NULL);
struct test_kobj_attribute value_attribute = __ATTR(value, 0664, value_show, value_store);
struct attribute *test_kobj_attrs[] = {
    &name_attribute.attr,
    &value_attribute.attr,
    NULL,
};

//定义组
struct attribute_group test_kobj_group = {
    .name = "test_kobj_group",
    .attrs = test_kobj_attrs,
};

//模块初始化函数
static int __init test_kobj_init(void)
{
    int retval;
    printk(KERN_INFO "test_kobj_init\n");
    obj = kmalloc(sizeof(struct test_kobj), GFP_KERNEL);
    if (!obj) {
        return -ENOMEM;
    }
    
    obj->value = 1;
    memset(&obj->kobj, 0, sizeof(struct kobject));
    //添加进sysfs系统
    kobject_init_and_add(&obj->kobj, &test_kobj_ktype, NULL, "test_kobj");

    //在sys文件夹下创建文件
    retval = sysfs_create_files(&obj->kobj, (const struct attribute **)test_kobj_attrs);
    if (retval) {
        kobject_put(&obj->kobj);
        return retval;
    }
    
    //在sys文件夹下创建group
    retval = sysfs_create_group(&obj->kobj, &test_kobj_group);
    if (retval) {
        kobject_put(&obj->kobj);
        return retval;
    }
    
    return 0;
}

//模块清理函数
static void __exit test_kobj_exit(void)
{
    printk(KERN_INFO "test_kobj_exit\n");

    kobject_del(&obj->kobj);
    kobject_put(&obj->kobj);
    
    return;
}

module_init(test_kobj_init);
module_exit(test_kobj_exit);

MODULE_AUTHOR("LoyenWang");
MODULE_LICENSE("GPL");

```

