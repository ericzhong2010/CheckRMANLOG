#### RMAN备份日志检查与发送通知(邮件/微信)

----

@ Author: Eric.zhong

@Contact: ericzhong2010@qq.com

@Create Time: 2020/03/06

@File: CheckRMANLOG.py

@Info:  RMAN 备份日志检查与发送通知(邮件/微信)

----



#### 概要说明
公司有许多的客户都在运用ORACLE数据库，但由于客户对IT熟悉程度有限无法实现每日检查，也没有预算构筑监控系统。我只能曲线救国方式来保障客户业务的连续性。通过BAT脚本监控备份日志，如果有捕获的关键字，那么就发送出提示邮件。

如下是文章地址：
https://blog.csdn.net/weixin_38623994/article/details/97802712

此脚本有一些许多不足的地方，由于自己在学习PYTHON就将程序进行改版练练手的。



#### 简要步骤
##### 1. RMAN全备份脚本

RMANBackup_LEVEL0.bat

```
rman target / NOCATALOG CMDFILE 'C:\scripts\RMANBackup_LEVEL0.txt' MSGLOG 'D:\RMANBACKUP_LOG\RMAN_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%.LOG'

start CheckRMANLOG.exe
```

RMANBackup_LEVEL0.txt

```
run
{
configure retention policy to recovery window of 14 days;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO 'D:\RMANBACKUP\%F';
allocate channel d1 type disk;
backup incremental level 0 database include current controlfile format 'D:\RMANBACKUP\LEVEL0_%D_DB_%U_%MM%DD' plus archivelog format 'D:\RMANBACKUP\ARCH0_%D_DB_%U_%MM%DD' delete all input;
sql 'alter system archive log current';
release channel d1;
}
report obsolete;
crosscheck backup;
delete noprompt expired backup;
delete noprompt obsolete recovery window of 14 days;
delete noprompt archivelog until time 'SYSDATE-1';
```



##### 2. RMAN增备份脚本

RMANBackup_LEVEL1.bat

```
rman target / NOCATALOG CMDFILE 'C:\scripts\RMANBackup_LEVEL1.txt' MSGLOG 'D:\RMANBACKUP_LOG\RMAN_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%.LOG'

start CheckRMANLOG.exe
```

RMANBackup_LEVEL1.txt

```
run
{
configure retention policy to recovery window of 14 days;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO 'D:\RMANBACKUP\%F';
allocate channel d1 type disk;
backup incremental level 1 database include current controlfile format 'D:\RMANBACKUP\LEVEL1_%D_DB_%U_%MM%DD' plus archivelog format 'D:\RMANBACKUP\ARCH1_%D_DB_%U_%MM%DD' delete all input;
sql 'alter system archive log current';
release channel d1;
}
report obsolete;
crosscheck backup;
delete noprompt expired backup;
delete noprompt obsolete recovery window of 14 days;
delete noprompt archivelog until time 'SYSDATE-1';
```



##### 3. config配置文件

```
[Global]
CustomerName = 测试环境
LOGPath = D:\RMANBACKUP_LOG\
LOGPrefix = RMAN_
LOGExt = .log
Keyword = RMAN-,ORA-

[Wechat]
wechatstatus = 0
corpid = 企业识别号码
corpsecret = 企业应用密钥
touser = 企业微信收件人

[Email]
emailstatus = 1
mail_host = 邮箱服务器地址
mail_port = 25
mail_from = 发件人
mail_pass = 验证密码
receivers = 收件人[多收件人以逗号分隔]
```



#### 截图参考
- RMAN备份失败
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310143041596.png)
- RMAN备份成功
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310143252576.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zODYyMzk5NA==,size_16,color_FFFFFF,t_70)

- RMAN备份异常
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310143327406.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zODYyMzk5NA==,size_16,color_FFFFFF,t_70)
- 微信效果
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310143201456.png)



#### 常见问题

Q1:企业微信相关信息在哪里可以找到？

A1:企业微信申请 => https://work.weixin.qq.com/

**CropID 企业识别号码**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191105214853400.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zODYyMzk5NA==,size_16,color_FFFFFF,t_70)
**AgentID 企业号中的应用id
Secret 企业应用密钥**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191105215019640.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zODYyMzk5NA==,size_16,color_FFFFFF,t_70)

