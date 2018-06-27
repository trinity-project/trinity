# Trinity Network部署帮助文档

[TOC]

> *注意：
Trinity 路由节点部署对python3.6有环境依赖，要求部署环境的python版本不低于python3.6。
随着Trinity项目的不断演进，本文档有可能不适用未来发布的Trinity版本；本文档使用Ubuntu16.04桌面版进行测试验证。*

## Trinity 运行环境准备工作

安装系统库及系统工具

``` shell
sudo apt-get install screen git libleveldb-dev libssl-dev g++
```
安装mongodb并启动服务


``` shell
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5

echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list

sudo apt-get update

sudo apt-get install mongodb-org

sudo service mongod start

```

*参考：mongodb部署相关细节请访问 https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/*

安装python3.6

``` shell
sudo apt-get install software-properties-common

sudo add-apt-repository ppa:jonathonf/python-3.6

sudo apt-get update

sudo apt-get install python3.6 python3.6-dev
```

安装pip3.6

``` shell
sudo wget https://bootstrap.pypa.io/get-pip.py

sudo python3.6 get-pip.py
```

安装virtualenv

``` shell
sudo pip3.6 install virtualenv
```

## Trinity 源码包获取

``` shell
git clone https://github.com/trinity-project/trinity.git /home
```

进入trinity源码目录

``` shell
cd /home/trinity
```

创建及激活虚拟环境

``` shell
virtualenv -p /usr/bin/python3.6 venv

source venv/bin/activate
```

安装trinity节点依赖包

``` shell
pip install -r requirements
```

## Trinity 路由节点网关部署

打开gateway配置文件

``` shell
vi gateway/config.py
```

将`cg_public_ip_port = "localhost:8089"`中的localhost配置为用户自己的公网ip地址。

如：cg_public_ip_port = "8.8.8.8:8089"

新建会话窗口

``` shell
screen -S TrinityGateway #TrinityGateway: 用户可替换该名称
```

进入虚拟环境

``` shell
source venv/bin/activate
```

运行网关服务

``` shell
python start.py
```

控制台输出如下消息启动成功

```shell
###### Trinity Gateway Start Successfully! ######

```

使用`ctrl+a+d`键盘按键退出当前TrinityGateway会话窗口

注：若需要重连已创建的名为TrinityGateway的会话窗口，可使用如下命令

```shell
screen -r TrinityGateway
```

## Trinity 路由节点钱包部署

修改配置文件

``` shell
vi wallet/configure.py 
```
默认configure文件为测试网配置文件，同时在wallet目录下有configure_testnet.py和configure_mainnet.py两个配置文件，如果部署主网可简单将configure_mainnet.py的内容复制到configure.py中。
具体配置信息请参考配置文件注释说明。


创建新窗口会话

``` shell
    screen -S TrinityWallet #TrinityWallet: 用户可替换该名称
```

激活python3.6 virtualenv(进入到venv所在的文件夹目录)

``` shell
   source venv/bin/activate
```

运行钱包服务（进入trinity/wallet源码目录）

 - 主链钱包

``` shell
    python3.6 prompt.py -m #主链钱包
```

- 测试网钱包

```shell
   python3.6 prompt.py #测试网钱包
```

退出或重连网关会话请参考网关运行章节中的内容。


## Channel节点交互

trinity CLI钱包运行之后，即可在钱包控制台进行钱包及通道的相关操作了。

钱包控制台输入help查看所有trinity CLI钱包命令。

这里仅介绍几个和通道相关的命令：

1.使用状态通道前，需要先使用create wallet 命令创建一个地址。

```shell
trinity> create wallet /root/test/test.json # /root/test/test.json 为钱包文件路径
```

2.open wallet 打开已有钱包，注意：这里应该打开带有通道功能的钱包，否则通能功能将被限制。

```shell
trinity> open wallet /root/test/test.json
```
注：
新建钱包或打开钱包以后，wallet会主动连接gateway并打开channel功能，如果30s内没有自动打开channel功能，请使用以下命令手动打开channel功能.
   
3.channel enable命令进行channel功能的使能，只有使能channel功能之后才能进行状态通道相关的其他操作。

```shell
trinity> channel enable 
```
4.channel show uri 查看钱包uri
```shell
trinity> channel show uri
```
5.channel create创建通道。

```shell
trinity> channel create xxxxxxxxxxxxx@xx.xx.xx.xx:xxxx TNC 80000 
# create 后的参数：peer节点uri(PublicKey@ip_address:port）, asset_type, depoist
```

*注：
TNC押金数量是以800美金的价格计算。假设当前TNC价值1美金，那最低需要800个TNC才能保障通道建立成功，可以通过如下命令获取当前时间所需要的TNC押金，目前这条规则仅对TNC通道有效*

6.channel depoist_limit查看当前TNC押金最小值。

```shell
trinity> channel depoist_limit
```

7.channel tx命令进行状态通道的链下交易操作，tx后的参数可以支持paymentlink码，也可以是uri + asset + value。

```shell
trinity> channel tx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # payment link 码
```
或

``` shell
trinity> channel tx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@xx.xx.xx.xx:xxxx TNC 10
```

8.channel payment生成付款码。

```shell
trinity> channel payment TNC 10 "mytest" # payment 后面的参数是 asset type， value，comments， comments可以为空
```

9.channel close命令进行状态通道的结算并关闭通道。

```shell
trinity> channel close xxxxxxxxxxxxxxx #close后的参数为 channel name
```

10.channel peer查看当前channel的peer节点

```shell
trinity> channel peer
```