# Trinity Beta V0.1版本试用指引

## 试用指引索引
1. NEO-CLI节点部署
2. Trinity service节点部署
3. Trinity wallet节点部署
4. TestNet TNC水龙头
5. Channel交互

注意：随着Trinity项目的不断演进，本指引有可能不适用未来发布的Trinity版本；本指引使用Ubuntu16.04桌面版进行测试验证。

## NEO-CLI节点部署
Trinity为基于NEO的链下扩容方案，Trinity service节点是基于NEO-CLI节点进行技术实现的，部署Trinity service节点之前需要先部署NEO-CLI节点。

本指引是基于Neo CLI v2.7.1版本的neo-cli-ubuntu.16.04-x64.zip包进行测试验证的。

NEO-CLI节点部署请参考如下链接：

http://docs.neo.org/zh-cn/node/setup.html


为了方便试用验证，建议切换NEO-CLI节点至NEO的测试网，切换testnet方法参考如下链接：

http://docs.neo.org/zh-cn/node/testnet.html


注意：由于Trinity service节点需要使用NEO-CLI提供的API，NEO-CLI部署完毕之后，需要启动节点的同时开启 API，即需要使用如下命令启动NEO-CLI节点：

```
dotnet neo-cli.dll /rpc
```
NEO-CLI节点启动成功之后，可使用命令进行节点状态的查看，建议等待节点完成区块同步之后再进行后续的部署操作；NEO-CLI命令参考如下链接：

http://docs.neo.org/zh-cn/node/cli.html


NEO-CLI节点需要持续保持在启动状态，以便为Trinity service节点提供必要的api服务。

## Trinity service节点部署
Trinity service节点基于python3的库进行开发，对python3有依赖，部署该节点的python环境要求不低于python3.5.2版本。

通过如下方式获取Trinity service节点源码压缩包master.zip:

```
wget https://github.com/trinity-project/trinity/archive/master.zip
```

通过如下命令对master.zip进行解压缩之后得到trinity-master源码目录：

```
unzip master.zip
```
进入trinity-master/目录，通过以下命令进行Trinity service节点的python依赖包的安装：

```
pip3 install -r requirements.txt
```
进入trinity-master/src/目录，通过以下命令配置python环境变量：

```
export PYTHONPATH=$PWD
```
通过以下命令安装mysql数据库：

```
sudo apt-get install mysql-server
```
安装过程中将mysql的root用户密码设置为root，完成安装后新建一个名称为test的数据库：

```
mysql -uroot -p
create database test；
exit;
```
进入trinity-master/src/NodeB/目录，通过如下命令启动nodeb的块同步服务：

```
python3 store_block_data.py -->null &
```

进入trinity-master/src/NodeB/目录，通过如下命令启动nodeb的RPC服务：

```
python3 runserver.py &
```
注意：nodeb的两个服务对应的配置文件为同目录下的config.py文件，trinity service节点与NEO CLI节点部署在同一个服务器上且使用TestNet测试不需要修改该配置文件，其他情况自行设置即可。

进入trinity-master/src/neo_python_tool/目录，通过如下命令启动trinity service节点的monitor服务：

```
python3 monitor_contract.py &
```
进入trinity-master/src/proxy/目录，通过如下命令启动trinity service节点的gateway服务：

```
python3 api.py &
```
注意：gateway服务对应的配置文件为trinity-master/src/目录下的configure.json文件，trinity service节点与NEO CLI节点部署在同一个服务器上且使用TestNet测试不需要修改该配置文件，其他情况自行设置即可。

## Trinity wallet节点部署
Trinity wallet当前版本为web版,通过如下方式获取Trinity wallet节点web源码压缩包master.zip：

```
wget https://github.com/trinity-project/wallet-website/archive/master.zip
```

通过如下命令对master.zip进行解压缩之后得到wallet-website-master源码目录：
```
unzip master.zip
```

使用浏览器打开wallet-website-master目录下的index.html即可登陆Trinity wallet的web页面。

值得一提的是当前Trinity wallet web版仅支持明文私钥格式，试用时务必做好私钥的安全备份工作。

## TestNet TNC水龙头
TNC水龙头是基于NEO TestNet的，以便大家在NEO TestNet上进行Trinity试用，每个地址每次可获得10个TNC。

水龙头地址：

```
http://106.15.91.150
```


## Channel节点交互
访问Trinity wallet的web页面，进入web版钱包界面，如下：

![wallet](https://github.com/trinity-project/wallet-website/blob/master/images/1519905471365.png?raw=true)

重点介绍下图片上红框中Transfer和Channel的两项：
- Transfer

    传统的链上交易方式，所有交易上链广播。
    
- Channel

    链下状态通道交易方式，涵盖状态通道的整个生命周期，押金上链进行信用背书，余额即时转账进行链下支付，通道关闭智能合约自动链上结算。
