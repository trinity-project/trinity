Trinity Network部署帮助文档
==================================

### [Trinity 运行环境准备工作](#prepare_trinity_environment)

### [Trinity 源码包获取](#get_trinity_sources)

### [Trinity 网关节点部署](#deploy_trinity_gateway)

### [Trinity 钱包节点部署](#deploy_trinity_wallet)

### [TestNet TNC水龙头](#trinity_faucet)

### [Trinity 网络浏览器](#trinity_explorer)

### [Channel交互](#trinity_channel)

----


<h3 id="prepare_trinity_environment">Trinity 运行环境准备工作</h3>

* #### Ubuntu 1604桌面版或服务器版

    * **安装系统库及系统工具**

    ```
    sudo apt-get install screen git libleveldb-dev libssl-dev g++
    ```

    * **安装mongodb**

    *参考：更多细节请访问 https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/ *

    ```
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5

    echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list

    sudo apt-get update

    sudo apt-get install mongodb-org

    ```

    * **启动mongodb数据库服务**

    ```
    sudo service mongod start
    ```

* #### Python3.6 运行环境

    * **安装python3.6**

    **添加python3.6安装包**

    ```
    sudo apt-get install software-properties-common

    sudo add-apt-repository ppa:jonathonf/python-3.6

    sudo apt-get update
    ```

    **安装python3.6**

    ```
    sudo apt-get install python3.6 python3.6-dev
    ```

    * **安装pip3.6**

    ```
    sudo wget https://bootstrap.pypa.io/get-pip.py
    sudo python3.6 get-pip.py
    ```

    * **安装virtualenv**

    ```
    sudo pip3.6 install virtualenv
    ```


<h3 id="get_trinity_sources">Trinity 源码包获取</h3>

* #### 克隆Trinity源码

    ```
    git clone https://github.com/trinity-project/trinity.git [User-Path]
    ```

    *User-Path ：用户指定的目录。若用户没有指定目录，克隆目录默认目录为当前目录下的trinity文件夹。*

* ##### 安装Trinity网络的Python依赖库文件

    * **进入trinity源码目录**

    ```
    cd trinity
    ```

    * **创建及激活python3.6虚拟环境**

    ```
    virtualenv -p /usr/bin/python3.6 venv

    source venv/bin/activate
    ```

    * **安装依赖库**

    ```
    pip install -r requirements

    deactivate  // 退出python3.6虚拟环境
    ```


<h3 id="deploy_trinity_gateway">Trinity 网关节点部署</h3>

* #### 修改配置文件

    * **主链网关配置**

        **编辑网关配置文件**

        ```
        cd gateway

        vi config.py

        将`cg_public_ip_port`中localhost替换为用户自己的公网。
        ```

        **返回trinity目录**

        ```
        cd ..
        ```

    * **测试链网关配置**

        同 "主链网关配置"

* #### 运行

    * **主链网关运行**

    **创建新窗口会话**

    ```
    screen -S TrinityGateway
    ```

    *TrinityGateway: 用户可替换该名称。*


    * **激活python3.6 virtualenv**

    ```
    source venv/bin/activate
    ```

    * **运行网关服务**

    ```
    cd gateway

    python start.py &
    ```

    * **退出或重连网关会话**

    ```
    若需要退出当前screen，可使用`ctrl+a+d`退出。

    若需要重连已创建的screen进程，可使用`screen -r TrinityGateway`
    ```

<h3 id="deploy_trinity_wallet">Trinity 钱包节点部署</h3>

* #### 修改配置文件

    * **主链钱包节点配置**

    **编辑钱包配置文件**

    ```
    cd wallet

    vi configure.py

    修改Configure属性的Fee字段设置该钱包节点的路由手续费。默认手续费：0.01 TNC。

    修改Configure属性的AssetType中TNC对应的值为：0x08e8c4400f1af2c20c28e0018f29535eb85d15b6。

    将Configure属性的BlockChain的值替换为下列数据：
        "RPCClient":"http://localhost:10332", # neocli client json-rpc
        "NeoUrlEnhance": "http://47.93.214.2:21332",
        "NeoNetUrl" : "http://47.93.214.2:10332"

    配置完成后，执行`cd ..`返回到上一级目录。
    ```

    **配置钱包全节点信息**

    ```
    cd lightwallet

    vi Settings.py

    将setup_mainnet函数中的self.NODEURL = "http://main:" 替换为self.NODEURL = "http://47.93.214.2:21332":
    ```


    * **测试网钱包节点配置**

    ```
    cd wallet

    vi configure.py

    修改Configure属性的Fee字段设置该钱包节点的路由手续费。默认手续费：0.01 TNC。

    配置完成后，执行`cd ..`返回到上一级目录。
    ```

* #### 运行

    * **主链钱包运行

    **创建新窗口会话**

    ```
    screen -S TrinityWallet
    ```

    *TrinityWallet: 用户可替换该名称。*

    * **激活python3.6 virtualenv**

    ```
    source venv/bin/activate
    ```

    * **运行钱包服务**

    ```
    cd wallet

    python prompt.py -m
    ```

    * **退出或重连网关会话**

    ```
    若需要退出当前screen，可使用`ctrl+a+d`退出。

    若需要重连已创建的screen进程，可使用`screen -r TrinityWallet`
    ```

    * **测试网钱包运行

    **创建新窗口会话**

    ```
    screen -S TrinityWalletTestnet
    ```

    *TrinityWallet: 用户可替换该名称。*

    * **激活python3.6 virtualenv**

    ```
    同 主链钱包运行部分。
    ```

    * **运行钱包服务**

    ```
    cd wallet

    python prompt.py
    ```

    * **退出或重连网关会话**

    ```
    同 主链钱包运行部分。
    ```

* **`注意：`**

```
1· 钱包需要持续保持打开状态。
```


<h3 id="trinity_faucet">TestNet TNC水龙头</h3>

TNC水龙头是基于NEO TestNet的，以便大家在NEO TestNet上进行Trinity试用，每个地址每次可获得10个TNC。

水龙头地址：

http://106.15.91.150


<h3 id="trinity_explorer">Trinity 网络浏览器</h3>

Trinity网络浏览器可以实时查看trinity网络节点的详细信息及状态。

浏览器地址：

http://106.15.91.150:8033


<h3 id="trinity_channel">Channel节点交互</h3>


trinity CLI钱包区块同步完成之后，即可在钱包控制台进行钱包及通道的相关操作了。

钱包控制台输入help查看所有trinity CLI钱包命令。

这里仅介绍几个和通道相关的命令：

1. 使用状态通道前，需要先使用create wallet 命令创建一个地址。

2. 使用channel open命令进行channel功能的使能，只有使能channel功能之后才能进行状态通道相关的其他操作。

3. 使用channel create命令进行状态通道的创建操作。

4. 使用channel tx命令进行状态通道的链下交易操作。

5. 使用channel close命令进行状态通道的结算删除工作。


* **`注意：`**

当前软件版本在创建通道时，TNC押金数量是以$800美金的价格计算。假设当前TNC价值$1美金，那最低需要800个TNC才能保障通道建立成功。
