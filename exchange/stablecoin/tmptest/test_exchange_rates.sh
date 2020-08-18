#!/bin/bash

RATE=$( curl -s http://localhost:8000/exchange/e2t/rate )
echo $RATE

RATE=$( curl -s http://localhost:8000/exchange/t2e/rate )
echo $RATE

RATE=$(curl -sG --data-urlencode base=200 http://localhost:8000/exchange/e2t/rate)
echo $RATE

RATE=$(curl -sG --data-urlencode base=200 http://localhost:8000/exchange/t2e/rate)
echo $RATE

