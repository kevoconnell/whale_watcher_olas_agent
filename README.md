# watch_whales

This is a simple Olas agent that watches for whales on a given ethereum blockchain

## Requirements
1.) Poetry < 2.0.0
2.) Python > 3.9, <3.11
3.) Docker Desktop



## Get started

1.) poetry shell

2.) pip install 'open-autonomy[all]' && pip install open-aea-ledger-ethereum

3.) get a RPC URL, we recommend [Alchemy](https://www.alchemy.com/), put your URL in a .env under the RPC_URL

4.) adjust WHALE_THRESHOLD to the amount you want. for simplicity sake we recommend ~75 ETH

5.) run the following

```
cd whale_watcher

# Generate and add Ethereum key
aea -s generate-key ethereum && aea -s add-key ethereum

# Install dependencies
aea -s install

# Set up certificates for P2P communication
aea -s issue-certificates

# Start the agent
aea -s run
```

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

