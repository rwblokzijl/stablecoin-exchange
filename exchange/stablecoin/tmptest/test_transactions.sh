#!/bin/bash

WALLET=ABC123
IBAN=COUTERP1

echo wallet:

# Get balance
TRANSACTIONS=$(curl -sG --data-urlencode wallet=$WALLET http://localhost:8000/transactions/wallet)
echo $TRANSACTIONS

echo iban:

TRANSACTIONS=$(curl -sG --data-urlencode iban=$IBAN http://localhost:8000/transactions/iban)
echo $TRANSACTIONS

