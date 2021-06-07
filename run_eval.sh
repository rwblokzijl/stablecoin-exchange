#!/bin/bash

# export TRANSACTIONS_TO_DO=1024
export TRANSACTIONS_TO_DO=10
export PROCESSES=()

# client:gateway:checkpoint_freq:tps
A=(

#     # exp 3: as function of gateway count
#     2:2:1
#     3:3:1
#     4:2:1
#     4:4:1

#     # exp 1: as function of users
#     2:1:1
#     3:1:1
#     4:1:1
#     5:1:1
#     6:1:1
#     7:1:1
#     8:1:1
#     9:1:1

#     2:1:2
#     3:1:2
#     4:1:2
#     5:1:2
#     6:1:2
#     7:1:2
#     8:1:2
#     9:1:2

#     2:1:4
#     3:1:4
#     4:1:4
#     5:1:4
#     6:1:4
#     7:1:4
#     8:1:4
#     9:1:4

#     2:1:6
#     3:1:6
#     4:1:6
#     5:1:6
#     6:1:6
#     7:1:6
#     8:1:6
#     9:1:6

#     2:1:8
#     3:1:8
#     4:1:8
#     5:1:8
#     6:1:8
#     7:1:8
#     8:1:8
#     9:1:8

# # exp 2: as function of checkpoint_freq
    # # 8:1:2 # already in exp 1
    # 8:1:4
    # 8:1:6
    # 8:1:8

    # TODO:
    # 8:1:10
    # 8:1:12
    # 8:1:14
    # 8:1:16
    # 8:1:18
    # 8:1:20
    # 8:1:22
    # 8:1:24
    # 8:1:26
    # 8:1:28
    # 8:1:30
    # 8:1:32

    2:1:3:0
    2:1:3:1

)

# simple test
# A=( 2:1:2 )

# echo ${A[@]}
# exit

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
    (rm eval/keys/*     || true) > /dev/null 2>&1
    (rm eval/sync/*     || true) > /dev/null 2>&1
    (rm eval/database/* || true) > /dev/null 2>&1

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
    export CLIENTS=${a%:*:*:*}
    tmp=${a#"$CLIENTS"}
    tmp=${tmp#:}
    export GATEWAYS=${tmp%:*:*}
    tmp=${tmp#"$GATEWAYS"}
    tmp=${tmp#:}
    export CHECKPOINT_EVERY=${tmp%:*}
    tmp=${tmp#"$CHECKPOINT_EVERY"}
    export TPS_TEST=${tmp#:}

    # echo $CLIENTS
    # echo $GATEWAYS
    # echo $CHECKPOINT_EVERY
    # echo $TPS_TEST
    # echo -----

    run_docker
    # run_local

done
