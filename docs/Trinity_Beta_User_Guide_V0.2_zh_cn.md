# Trinity Beta V0.2版本试用指引

## 试用指引索引
1. Trinity 源码包获取
2. Trinity 网络节点部署
3. Trinity CLI 钱包部署
4. TestNet TNC水龙头
5. Trinity 网络浏览器
6. Channel交互

注意：
1. Trinity v0.2版本对python3.6有依赖，要求部署环境的python版本不低于python3.6。

2. 随着Trinity项目的不断演进，本指引有可能不适用未来发布的Trinity版本；本指引使用Ubuntu16.04桌面版进行测试验证。


## Trinity 源码包获取

通过访问如下链接获取Trinity CLI钱包源码包:

```
git clone https://github.com/trinity-project/trinity.git
```
apt-get install python3.6 python3.6-dev python3.6-venv python3-pip libleveldb-dev libssl-dev g++

通过以下命令部署Trinity 的依赖环境：
```
apt-get install python3.6 python3.6-dev python3.6-venv python3-pip libleveldb-dev libssl-dev g++
```

进入Trinity目录，通过以下命令安装Trinity 的依赖包：

```
pip3.6 install -r requirements
```

进入Trinity目录,通过以下命令配置python环境变量:

```
export PYTHONPATH=$PWD
```

## Trinity 网络节点部署

打开trinity/gateway/config.py文件，配置 cg_public_ip_port字段值的ip地址部分为自己节点的公网ip地址，端口号不变。

进入trinity/gateway目录，执行如下命令启动trinity 网络节点：

```
python3.6 start.py -->null &
```
## Trinity CLI 钱包部署

打开trinity/wallet/config.py文件，通过修改Configure属性的Fee字段的值来设置该钱包节点的路由手续费，当前默认收取0.01TNC的手续费。

进入trinity/wallet目录，执行如下命令启动trinity CLI钱包：

```
python3.6 prompt.py 
```

等待trinity CLI钱包进行区块同步，区块同步完成之后再继续进行后续操作。

注意：
1、钱包需要持续保持打开状态。
2、钱包区块同步完成之后再进行channel相关操作。

## TestNet TNC水龙头
TNC水龙头是基于NEO TestNet的，以便大家在NEO TestNet上进行Trinity试用，每个地址每次可获得10个TNC。

水龙头地址：

http://106.15.91.150

## Trinity 网络浏览器
Trinity网络浏览器可以实时查看trinity网络节点的详细信息及状态。

浏览器地址：

http://106.15.91.150:8033


## Channel节点交互

trinity CLI钱包区块同步完成之后，即可在钱包控制台进行钱包及通道的相关操作了。

钱包控制台输入help查看所有trinity CLI钱包命令。

这里仅介绍几个和通道相关的命令：

1. 使用状态通道前，需要先使用create wallet 命令创建一个地址。

2. 使用channel open命令进行channel功能的使能，只有使能channel功能之后才能进行状态通道相关的其他操作。

3. 使用channel create命令进行状态通道的创建操作。

4. 使用channel tx命令进行状态通道的链下交易操作。

5. 使用channel close命令进行状态通道的结算删除工作。
