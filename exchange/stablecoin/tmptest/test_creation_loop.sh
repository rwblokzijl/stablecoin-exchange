#!/bin/bash

WALLET=ABC123
IBAN=COUTERP1

# Create exchange payment
CREATE=$( curl -s --data-urlencode 'collatoral_cent=100' --data-urlencode "dest_wallet=$WALLET" http://localhost:8000/exchange/e2t )

# Get payment id
PID=$(echo $CREATE | jq -r '.payment_id')
echo $PID

# Get status of id
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
echo $STATUS | jq '.status'

# Get balance
BALANCE=$(curl -sG --data-urlencode wallet=$WALLET http://localhost:8000/transactions/balance)
echo $BALANCE #| jq '.balance'

# Set the status to complete
curl --data-urlencode "payment_id=${PID}" --data-urlencode "counterparty=$IBAN" http://localhost:8000/exchange/complete
curl --data-urlencode "payment_id=${PID}" --data-urlencode "counterparty=$IBAN" http://localhost:8000/exchange/complete
curl --data-urlencode "payment_id=${PID}" --data-urlencode "counterparty=$IBAN" http://localhost:8000/exchange/complete
curl --data-urlencode "payment_id=${PID}" --data-urlencode "counterparty=$IBAN" http://localhost:8000/exchange/complete

# Get status of id again
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
STATUS=$(curl -sG --data-urlencode payment_id=$PID http://localhost:8000/exchange/payment)
echo $STATUS | jq '.status'

# Get balance
BALANCE=$(curl -sG --data-urlencode wallet=$WALLET http://localhost:8000/transactions/balance)
echo $BALANCE #| jq '.balance'

