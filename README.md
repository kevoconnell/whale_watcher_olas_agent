# watch_whales

This is a simple Olas agent that watches for whales on a given ethereum blockchain


## Get started


1.) get a RPC URL, we recommend [Alchemy](https://www.alchemy.com/), put your URL in a .env under the RPC_URL

2.) adjust WHALE_THRESHOLD to the amount you want. for simplicity sake we recommend ~75 ETH

3.) run the following

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

