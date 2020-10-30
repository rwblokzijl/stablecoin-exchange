# Stablecoin Demonstrator

This is a demonstration of a stablecoin that builds on the
[TrustChain](https://github.com/Tribler/py-ipv8) blockchain as part of a master
thesis at the  TU Delft Distributed Systems research group.

# General system description

In TrustChain...[x] the authors describe a CAP theorem like tradeoff between
**High Scalability**, **Full Decentralisation** and **Global Consensus**.
Where most blockchains choose until now have chosen Global Consensus and
Decentralisation, TrustChain optimised for scalability and Decentralisation.

This project aims to show how this system and its properties can be used to
create a fabric that the financial infrastructure of tomorrow can build on.

# System components

This prototype consists of 2 components that demonstrate the systems
capabilities.

[**The Wallet**](https://github.com/Bloodyfool/trustchain-superapp) is used by
anyone willing to hold and transact the stablecoin.

**The Exchange platform (this repo)** is controlled by a (central bank like) issuer. It
exchanges collateral (like Euros) for the Stablecoin.

