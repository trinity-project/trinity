# Trinity
Trinity is a universal off-chain scaling solution, which aims to achieve real-time payments with low transaction fees, scalability and privacy protection for mainchain assets. Using state channel technology, Trinity will significantly increase the transaction throughput of underlying chains as well as the assets on smart contracts. TNC cross-chain converter facilitates the data and value flow between multiple chains. Trinity will be a fully autonomous and decentralized performance-enhancing network for the entire ecosystem and provides all-round support to Dapps on bottom layer chains in the future. https://trinity.tech

Trinity-neo
trinity-neo is the implementation of trinity protocol based on NEO.

# Trinity-NEO Network Configuration Guide


note：Trinity routing nodes require the configuration environment be no less than python3.6.    
As Trinity develops, this file may not apply to the new version. This file was tested on Ubuntu16.04 desktop.

## Trinity-NEO Runtime Environment Preparation

Install system library and system tools

``` shell
sudo apt-get install screen git libleveldb-dev libssl-dev g++
```
Install mongodb and launch the service


``` shell
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5

echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list

sudo apt-get update

sudo apt-get install mongodb-org

sudo service mongod start

```

*Ref：mongodb configuration details, please visit:  https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/*

Configure python3.6

``` shell
sudo apt-get install software-properties-common

sudo add-apt-repository ppa:jonathonf/python-3.6

sudo apt-get update

sudo apt-get install python3.6 python3.6-dev
```

Install pip3.6

``` shell
sudo wget https://bootstrap.pypa.io/get-pip.py

sudo python3.6 get-pip.py
```

Install virtualenv

``` shell
sudo pip3.6 install virtualenv
```

## Get Trinity-neo Source Code

``` shell
git clone https://github.com/trinity-project/trinity.git /home
```

Open trinity source code catalo

``` shell
cd /home/trinity
```

Create and activate virtual environment

``` shell
virtualenv -p /usr/bin/python3.6 venv

source venv/bin/activate
```

Install trinity node requirement package

``` shell
pip install -r requirements
```

## Install Trinity Routing Node Gateway

Open gateway configuration file

``` shell
vi gateway/config.py
```

Find'cg_public_ip_port = "localhost:8089"'
and Put user’s public ip address at the localhost

eg：cg_public_ip_port = "8.8.8.8:8089"

Create a new session window

``` shell
screen -S TrinityGateway #TrinityGateway: 用户可替换该名称
```

Enter virtual environment

``` shell
source venv/bin/activate
```

Run the Gateway service

``` shell
python start.py
```

The code below indicates the Gateway successfully started

```shell
###### Trinity Gateway Start Successfully! ######

```

Use ctrl+a+d to close current TrinityGateway session window

Note: call the function below to re-open the existing TrinityGateway session window

```shell
screen -r TrinityGateway
```

## Install Trinity Routing Node Wallet 

Revise configuration file

``` shell
vi wallet/configure.py 
```
The default configure file applies to the testnet, for which configure_testnet.py and configure_mainnet.py co-exist in the wallet catalog. For the mainnet, simply copy configure_mainnet.py and paste it to configure.py. 

Please refer to notes for configuration details.

Create a new session window

``` shell
    screen -S TrinityWallet
```

Activate python3.6 virtualenv

``` shell
   source venv/bin/activate
```

Run the Gateway service（Enter trinity/ wallet source code catelog)

 - Mainnet Wallet

``` shell
    python3.6 prompt.py -m
```

- Testnet Wallet

```shell
   python3.6 prompt.py
```

close or reopen the gateway session please refer to the details of 'run the gateway service'


## Channel Nodes Interworking

After trinity CLI wallet running, the subsequent channel and wallet operations can be performed on the wallet console.

Input help to the wallet console to view all trinity CLI wallet commands.

Here are a few channel-related commands:

1.Use create wallet command to create an address before using state channels.

```shell
trinity> create wallet /root/test/test.json # /root/test/test.json is the path of wallet
```

2.Use open wallet command to open existing wallet. Note: open a wallet with channel function, or the function will be restricted.

```shell
trinity> open wallet /root/test/test.json
```
Note:After creating or re-opening a wallet, the wallet will automatically connect to the gateway and enable channel function. If channel function was not enabled within 30s, please call channel function to open it manually
   
3.Use channel enable command to activate channel function before operating on state channels.

```shell
trinity> channel enable 
```

4.channel show uri

trinity> channel show uri

5.Use channel create

```shell
trinity> channel create xxxxxxxxxxxxx@xx.xx.xx.xx:xxxx TNC 80000
```

Note:TNC deposit is calculated on $800 USD, which means 800 TNC is required if TNC current price is $1 USD. The command below will tell how much TNC is needed currently for deposit. This is only valid for TNC channel.  

6.Call channel depoist_limit to check the minimum TNC deposit

```shell
trinity> channel depoist_limit
```

7.Call channel tx to execute off-chain transactions. tx parameters supports pymentlink code, or use uri + asset + value

```shell
trinity> channel tx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # payment link code
```
or

``` shell
trinity> channel tx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@xx.xx.xx.xx:xxxx TNC 10
```

8.Call channel payment to generate payment code

```shell
trinity> channel payment TNC 10 "mytest"
```

9.Call channel close to complete settlement and close the channel

```shell
trinity> channel close xxxxxxxxxxxxxxx
```

10.channel peer is for peer node review

```shell
trinity> channel peer
```
