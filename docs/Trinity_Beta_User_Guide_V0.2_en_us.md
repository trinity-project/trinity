# Trinity Beta V0.2 User Guide 

## User Guide Index
1. Trinity Source Code Package

1. Trinity Network Node Deployment

1. Trinity CLI Wallet Deployment

1. TestNet TNC Faucet

1. Trinity Network Explorer

1. Channel Interaction

Note：
1. Trinity v0.2 is dependent on python3.6, thus requiring python3.6 or above to run.

1. As the Trinity Project develops, this user guide may not be applicable to future versions. The user guide uses Ubuntu16.04 PC version to test.

## Trinity Source Code Package

Go to the following link to get Trinity source code package:

```
git clone https://github.com/trinity-project/trinity.git 
```
Run the following command to deploy Trinity dependency environment：


```
sudo apt-get install python3.6 python3.6-dev python3.6-venv python3-pip libleveldb-dev libssl-dev g++ 
```
Enter Trinity directory. Run the following command to install Trinity dependency：


```
pip3.6 install -r requirements 
```
Enter Trinity directory. Run the following command to configurate python environment variables:

```
export PYTHONPATH=$PWD 
```
Install mongodb database：


```
sudo apt-get install -y mongodb-org 
```

Start mongodb database:


```
sudo service mongod start 
```

## Trinity Network Node Deployment 
Open trinity/gateway/config.py. Configurate the ip address of cg_public_ip_port as the ip address of the node on public network. The port number stays the same. 

Enter trinity/gateway directory. Run the following command to start Trinity network node：


```
python3.6 start.py -->null & 
```

## Trinity CLI Wallet Deployment
Open trinity/wallet/config.py. Change the field value of Fee in Configure property to set the router transaction fee of the wallet node. The default transaction fee is 0.01TNC.

Enter trinity/wallet directory. Run the following command to start Trinity CLI wallet：

```
python3.6 prompt.py  
```
Wait until the trinity CLI wallet is synced on the block to execute follow-up operations.

Note: 
1. The wallet should remain open. 

2. Execute channel-related operations after the wallet is synced on the block.

## TestNet TNC Faucet
As TNC Faucet is based on NEO TestNet, you can test Trinity on NEO TestNet.

Each address can request 10 TNC each time.

Facet address：

```
http://106.15.91.150
```

## Trinity Network Explorer
Check details and status of Trinity network nodes on Trinity explorer. 

Explorer address：

```
http://106.15.91.150:8033
```
## Channel Interaction

After the Trinity CLI wallet is synced on the block, perform wallet and channel-related operations on wallet dashboard. Insert ‘help’ on the dashboard to check all commands of the trinity CLI wallet.

The following are several channel-related commands：

1. Before using state channels, run ‘create wallet’ to create an address.

1. Run ‘channel open’ to enable channel-related functions. Channel-related operations can only be executed after enabling channel functions. 

1. Run ‘channel create’ to create state channels.

1. Run ‘channel tx’ to make off-chain state channel transactions. 

1. Run ‘channel close’ to settle and delete state channel transactions.
