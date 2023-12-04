## 数据库插入使用说明

该版本是使用批量造数据然后一次性提交当天txt文件实现的

该脚本为单线程版本，即造完当天数据后再插入。后期可改完双进程，一个进程造数据，一个进程插入数据库，这样脚本执行时间会大大缩减

<font color="orange">该脚本SQL为10.12之前上线版本SQL，新需求SQL变更后需要自行修改 234 、245、 255行代码</font>。注意字符串拼接方式，可不填写字段使用`+'"\t\t"'+` 方式拼接

![image-20231012163520741](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012163520741.png)

![image-20231012163531964](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012163531964.png)

![image-20231012163541230](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012163541230.png)



## 数据库权限查看与配置

#### 查看 secure_file_priv 路径

`SHOW VARIABLES LIKE "secure_file_priv";`

![image-20231012161813222](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012161813222.png)

可以看出，mysql 安全文件路径为`/var/lib/mysql-files/data`。

如果脚本中的 baseFile 字段路径不为该安全路径，请更改 196 行

![image-20231012162922288](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012162922288.png)



#### 将 local_infile 改为 ON 

在mysql 8.0.22 运行load data local 从本地文本导入数据时，报错："ERROR 3948(42000): Loading local data is disabled - this must be enabled on both the client and server sides".[https://blog.csdn.net/young_kp/article/details/109523153]

首先，检查一个全局系统变量 'local_infile' 的状态：

`show global variables like 'local_infile';`

![image-20231012162643926](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012162643926.png)

如果不是ON，则需要执行以下代码

`set global local_infile=1;`

![image-20231012162738538](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012162738538.png)

<font color="red">**注：每次重启 mysql 后需要重新设置，包括最大连接数**</font>

**查看MySQL最大连接数**

`show variables like "%max_connections%";`

![image-20231204145856893](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231204145856893.png)

**修改最大连接数(重启后失效)**

`set global max_connections = 1000;`





#### 好像可以不用设置

在 docker 配置的 mysql 文件中`/docker/mysql8/conf/my.cnf` 最后写入该代码`local_infile = 1`

![image-20231012164941321](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012164941321.png)



## 脚本配置

#### 设置执行时间

脚本第 207 行为设置从哪一天开始插入，即三张表的开始时间和结束时间都为该时间（有需求可以自行改代码）

![image-20231012163149793](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012163149793.png)

208 行为要造数据的天数，<font color="red">**造数据天数不要超过造数的当月时间。**</font>

例如：我要从9月25号造数据，207行设置为：`start_date = datetime.strptime("2023-09-25 16:53:04", "%Y-%m-%d %H:%M:%S")`

那 days 就要小于6天，`end_date = start_date + timedelta(days=5)` 

这里208 行days 设置成5天，不超过本月。（因为262行、265行、268行为当月数据表，详见设置提交表）



#### 设置每天插入数量

在 226 行可以设置每天插入数量，默认是 50w

![image-20231012165243453](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012165243453.png)



#### 设置提交表

![](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012164401124.png)

代码中提交表是固定的，如果你要插入10月的数据，就需要更改表名称了。

注意插入表的开始时间，以及插入表的结束时间，是否超过了提交表的名称时间



## 数据清理

**导入后的原始数据及时清理，很占空间！！**！

默认原始数据路径：`/var/lib/mysql-files/data`



## 成果

![image-20231012165309119](C:\Users\William\AppData\Roaming\Typora\typora-user-images\image-20231012165309119.png)

