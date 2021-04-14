#!/bin/bash

# export CLIENTS="${1:-2}"
# export GATEWAYS="${2:-$CLIENTS}"
export TRANSACTIONS_TO_DO=1024
export CHECKPOINT_EVERY=32

# if [ "$CLIENTS" -lt "$GATEWAYS" ]; then
#     echo more gateways than clients...
#     exit
# fi

# echo running evuation with $GATEWAYS GATEWAYS and $CLIENTS CLIENTS

# A=( 2:1 \
#     2:2)

A=( 2:1 \
    2:2 \
    4:1 \
    4:2 \
    4:4 \
    8:1 \
    8:2 \
    8:4 \
    8:8 )

for a in ${A[@]}
do
    export CLIENTS=${a%:*}
    tmp=${a#"$CLIENTS"}
    export GATEWAYS=${tmp#:}

    docker system prune -f
    docker volume rm gateway_sync
    docker network prune -y
    rm backend/eval/keys/* || true
    docker-compose -f docker-compose-eval.yml up --scale gateway=$GATEWAYS --scale client=$CLIENTS --build | tee eval_data/$a.log
    rm backend/eval/keys/* || true
done

