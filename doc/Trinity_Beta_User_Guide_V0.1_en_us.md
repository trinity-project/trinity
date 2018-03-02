# Trinity Beta V0.1 User Guide 

## User Guide Index
1. NEO-CLI Node Deployment 
1. Trinity Service Node Deployment
1. Trinity Wallet Node Deployment
1. TestNet TNC Faucet
1. Channel Interaction

Note: As the Trinity Project develops, this user guide may not be applicable to future versions. The user guide uses Ubuntu16.04 PC version to test. 

## NEO-CLI  Node Deployment
Trinity is an off-chain scaling solution for Neo. The Trinity service node is based on the NEO-CLI node to be implemented. Therefore, the NEO-CLI node should be deployed before the Trinity service node is deployed.

This user guide is for test on neo-cli-ubuntu.16.04-x64.zip of Neo CLI v2.7.1.

Please refer to the following links to deploy the NEO-CLI node:

http://docs.neo.org/en-us/node/setup.html

For the convenience of test, we suggest that you switch the NEO-CLI node to NEO testnet. Please refer to the following links on how to switch:

http://docs.neo.org/en-us/node/testnet.html

Note: As the Trinity service node needs to use the API provided by NEO-CLI, after deployment of NEO-CLI, open the API while starting the node. Run the following command to start the NEO-CLI node:

```
dotnet neo-cli.dll /rpc
```
After the NEO-CLI node is successfully started, you can run command to check node status. It is suggested that follow-up deployment be made after the node is synced on the block. For NEO-CLI command reference, please go to the following links:

http://docs.neo.org/en-us/node/cli.html

The NEO-CLI node should remain open to provide necessary API services to the Trinity service node.

## Trinity service Node Deployment
Development of the Trinity service node is based on the code of python3, thus dependent on python3. It is required that the Trinity service node be deployed on python3.5.2 or above.

Run the following command to get master.zip of the Trinity service node:

```
wget https://github.com/trinity-project/trinity/archive/master.zip
```

Run the following command to get trinity-master source code directory after unzipping master.zip:

```
unzip master.zip
```
Enter trinity-master/directory. Run the following command to install python dependent package of the Trinity service node:

```
pip3 install -r requirements.txt
```
Enter trinity-master/src/directory. Run the following command to configurate python environment variables:

```
export PYTHONPATH=$PWD
```
Run the following command to install mysql database:

```
sudo apt-get install mysql-server
```
Set root as the user password of mysql during installation. Create database test after the installation is completed:

```
mysql -uroot -p
create database test；
exit;
```
Enter trinity-master/src/NodeB/directory. Run the following command to start block sync of nodeb:

```
python3 store_block_data.py -->null &
```

Enter trinity-master/src/NodeB/directory. Run the following command to start RPC service of nodeb:

```
python3 runserver.py &
```
Note: The two services of nodeb correspond to config.py files under the same directory. The Trinity service node and the NEO CLI node are deployed on the same server and there is no need to change the config file using TestNet. The file can be set accordingly under other circumstances.

Enter trinity-master/src/neo_python_tool/directory. Run the following command to start monitor service of the Trinity service node:

```
python3 monitor_contract.py &
```
Enter trinity-master/src/proxy/directory. Run the following command to start gateway service of the Trinity service node:

```
python3 api.py &
```
Note: The corresponding config file of gateway service is configure.json in trinity-master/src/ directory. The Trinity service node and the NEO CLI node are deployed on the same server and there is no need to change the config file using TestNet. The file can be set accordingly under other circumstances.

## Trinity wallet Node Deployment
The current Trinity wallet is a web version. Run the following command to get master.zip of the Trinity wallet node web version:

```
wget https://github.com/trinity-project/wallet-website/archive/master.zip
```

Run the following command to get the source code directory of wallet-website-master after unzipping master.zip 
```
unzip master.zip
```

Use your explorer to open index.html in wallet-website-master to log in on the web version of the Trinity wallet.

It is worth mentioning that the current Trinity wallet web version only supports PEM private key. Please make copies of your private key and keep it in a secure place during the test. 

## TestNet TNC Faucet
As TNC Faucet is based on NEO TestNet, you can test Trinity on NEO TestNet. Each address can get 10 TNC each time. 

Faucet address：

```
http://106.15.91.150
```


## Channel Interaction
Visit Trinity wallet web version and enter the wallet interface:

![wallet](https://github.com/trinity-project/wallet-website/blob/master/images/1519905471365.png?raw=true)

More details about Transfer and Channel in the pic:
- Transfer

    Transfer is the traditional on-chain transaction mode where all transactions are broadcast on-chain.
    
- Channel

    Channel is the off-chain state channel transaction mode that covers the entire life cycle of the state channels. Deposits are put on-chain and payments are made instantaneously off-chain. When the channels are closed, settlement will appear on-chain. 
