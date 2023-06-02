# embybot - 针对Emby公益服的开服机器人，实现功能如下：
-  通过机器人创建Eemby账号，并同步设置好账号的相关权限-**全员可用**；
-  通过指令重置Emby账户密码，自定义设置账户密码-**全员可用**；
-  通过指令查询账户用户名-**全员可用**；
-  通过指令添加服务器线路信息-**管理员可用**；
-  通过指令查询公益服账户注册总数-**管理员可用**；
-  通过指令查询公益服服务器负载状态-**全员可用**；

## 使用方法
- 拉取项目

```shell
git clone https://github.com/07031218/embybot.git && cd embybot
```

- 修改项目根目录的`.env`文件，填写TG机器人的API-TOKEN；

- 修改项目根目录的`config.py`文件，根据注释提示填写好相关数据；

- phpmyadmin中新建数据库，导入项目中的`mysql.sql`恢复数据，数据表`users`记录存储Emby注册用户的相关数据，`line`数据表记录存储服务器线路信息，`severs`数据表可用来存储记录其他服emby服务器的相关信息；

- 回到项目根目录，执行`pip3 install -r requirements.txt`安装所需的相关依赖；

- 完成以上动作之后，执行python3 bot.py启动机器人

## 机器人指令大全：

- `/create` - 注册公益服账户

- `/check` - 查询公益服用户名

- `/reset` - 重置公益服密码

- `/setpw` - 自定义公益服账户密码

- `/checkurl` - 查询公益服线路信息

- `/counts` - 查询公益服账户总数

- `/addurl` - 添加公益服线路信息

- `/addserver` - 添加群友公益服信息

- `/checkserver` - 查询群友公益服信息

- `/status` - 查询公益服负载情况

## 机器人进程守护可通过添加systemd服务来实现

```shell
cat >/etc/systemd/system/embybot.service <<EOF
[Unit]
Description=embybot
After=rc-local.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/root/embtbot/ # 填写embybot目录路径
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```
- 启动服务
```shell
systemctl start emboybot
```

- 设置开机启动
```shell
systemctl enable embybot
```
- 机器人运行状态查看
```shell
systemctl status embybot
```
