#!/bin/bash

export TRANSACTIONS_TO_DO=1024
# export TRANSACTIONS_TO_DO=10
export PROCESSES=()

# array of experiment to run:
# format: $client:$gateway:$checkpoint_freq:$test_tps
A=()

# # # exp 3: as function of gateway count
# A+=( \
#     2:2:1:0
#     3:3:1:0
#     4:2:1:0
#     4:4:1:0

#     # 2:2:1:1 these seem to have issues
#     # 4:2:1:1
#     # 3:3:1:1
#     # 4:4:1:1
# )

# A+=( \

#     # cp 1
#     2:1:1:0
#     3:1:1:0
#     4:1:1:0
#     5:1:1:0
#     6:1:1:0
#     7:1:1:0
#     8:1:1:0
#     9:1:1:0

#     # cp 4
#     2:1:4:0
#     3:1:4:0
#     4:1:4:0
#     5:1:4:0
#     6:1:4:0
#     7:1:4:0
#     8:1:4:0
#     9:1:4:0
# )


# no delay
A+=( \

    # cp 1
    1:1:1:1
    2:1:1:1
    3:1:1:1
    4:1:1:1
    5:1:1:1
    6:1:1:1
    7:1:1:1
    8:1:1:1
    9:1:1:1

    # cp 4
    1:1:4:1
    2:1:4:1
    3:1:4:1
    4:1:4:1
    5:1:4:1
    6:1:4:1
    7:1:4:1
    8:1:4:1
    9:1:4:1

)

# exp 2: as function of checkpoint_freq
A+=(7:1:2:0)
# A+=(7:1:2:1)
for f in $(seq 6 2 32); do # checkpoint_freq 10-32 (2-8 are already in test 1)
    A+=(7:1:$f:0)
    # A+=(7:1:$f:1)
done


# # exp 1: as function of users
# for f in 1 $(seq 2 2 8); do # checkpoint_freq 1 2 4 6 8
#     for c in $(seq 2 7); do # n_clients 2 - 7 (1 gateway 7 clients is max because 8 cores)
#         A+=($c:1:$f:0)
#         A+=($c:1:$f:1)
#     done
# done

# simple test
# A=( 2:1:2 )

# echo ${A[@]} | tr " " "\n"
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
