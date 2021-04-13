#!/bin/bash

export CLIENTS="${1:-2}"
export GATEWAYS="${2:-$CLIENTS}"
export TRANSACTIONS_TO_DO=100
export CHECKPOINT_EVERY=5

if [ "$CLIENTS" -lt "$GATEWAYS" ]; then
    echo more gateways than clients...
    exit
fi

echo running evuation with $GATEWAYS GATEWAYS and $CLIENTS CLIENTS

docker system prune -f
docker volume rm gateway_sync
rm backend/eval/keys/* || true
docker-compose -f docker-compose-eval.yml up --scale gateway=$GATEWAYS --scale client=$CLIENTS --build
rm backend/eval/keys/* || true
