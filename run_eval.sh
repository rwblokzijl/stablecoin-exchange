#!/bin/bash

# export TRANSACTIONS_TO_DO=1024
export TRANSACTIONS_TO_DO=10
export PROCESSES=()

# A=( 2:1:32 \
#     2:2:32 \
#     4:1:32 \
#     4:2:32 \
#     4:4:32 \
#     8:1:32 \
#     8:2:32 \
#     8:4:32 \
#     8:8:32 )

# A=( 4:4:1 \
#     4:4:2 \
#     4:4:4 \
#     4:4:8 \
#     4:4:16)

# A=( 2:1:2 \
#     2:1:4)

# A=( 2:1:2 )

function run_docker {
    docker system prune -f
    docker volume rm gateway_sync
    docker network prune -y
    rm backend/eval/keys/* || true
    docker-compose -f docker-compose-eval.yml up --scale gateway=$GATEWAYS --scale client=$CLIENTS --build | tee eval_data/$a.log
    rm backend/eval/keys/* || true
}

function clean_up {
    # Perform program exit housekeeping
    echo KILLING
    kill -9 $PROCESSES
    exit
}

trap clean_up SIGHUP SIGINT SIGTERM

function run_local {
	(rm eval/keys/*          || true) > /dev/null 2>&1
	(rm eval/sync/*     || true) > /dev/null 2>&1
	(rm eval/database/* || true) > /dev/null 2>&1

    # export CLIENTS=$CLIENTS
    # export GATEWAYS=$GATEWAYS
    # export CHECKPOINT_EVERY=$CHECKPOINT_EVERY

    export PORT=8090
    export BASE_DIR=eval

    export IS_GATEWAY=1
    for i in $(seq 1 $GATEWAYS)
    do
        echo STARTNG GATEWAY $PORT
        pipenv run python stablecoin/run_eval.py &
        PROCESSES+=($!)
        ((PORT=PORT+1))
    done

    IS_GATEWAY=0
    for i in $(seq 1 $CLIENTS)
    do
        echo STARTNG CLIENT $PORT
        pipenv run python stablecoin/run_eval.py &
        PROCESSES+=($!)
        ((PORT=PORT+1))
    done
    wait $PROCESSES
    PROCESSES=()
    sleep 1
	return
}

# cd ./backend

for a in ${A[@]}
do
    export CLIENTS=${a%:*:*}
    tmp=${a#"$CLIENTS"}
    tmp=${tmp#:}
    export GATEWAYS=${tmp%:*}
    tmp=${tmp#"$GATEWAYS"}
    export CHECKPOINT_EVERY=${tmp#:}

    run_docker
    # run_local

done
