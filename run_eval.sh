#!/bin/bash

export CLIENTS="${1:-2}"
export GATEWAYS="${2:-$CLIENTS}"

if [ "$CLIENTS" -lt "$GATEWAYS" ]; then
    echo more gateways than clients...
    exit
fi

echo running evuation with $GATEWAYS GATEWAYS and $CLIENTS CLIENTS

rm backend/eval/keys/* || true
docker-compose -f docker-compose-eval.yml up --scale gateway=$GATEWAYS --scale client=$CLIENTS --build
rm backend/eval/keys/* || true
