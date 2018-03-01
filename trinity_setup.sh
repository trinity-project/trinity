#!/bin/sh

BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`
NODEB_DIR="$BASEDIR/src/NodeB"
TRINITY_PROXY="$BASEDIR/src/proxy"
MONITOR_CONTRACT="$BASEDIR/src/neo_python_tool"

help_menu()
{
    echo "Usage : bash start_trinity.sh [OPTIONS]"
    echo "Details of OPTIONS and Parameters"
    echo
    echo "-h, --help                     Display the help and exit."
    echo
    echo "1, ----start-nodeb             Start trinity NODE-B."
    echo "2, ----start-proxy             Start trinity proxy api node."
    echo "3, ----start-monitor           Start contract monitor node."
    echo "4, ----start-all               Start all nodes above."
}

start_nodeb_service()
{
    cd $NODEB_DIR && python3 ./runserver.py &
}

start_proxy_api_service()
{
    cd $TRINITY_PROXY && python3 api.py &
}

start_contract_monitor_service()
{
    cd $MONITOR_CONTRACT && python3 monitor_contract.py &
}

start_all_trinity_nodes_service()
{
    start_nodeb_service
    sleep 1

    start_proxy_api_service
    sleep 1

    start_contract_monitor_service
}

trinity_node_setup_step()
{
    TITLE="Start Trinity Nodes <it better to startup nodeb at first>"

    TEXT[1]="NodeB - Toggle NodeB service sync info from OnChain"
    FUNC[1]="start_nodeb_service"

    TEXT[2]="sNode - Toggle Proxy service node"
    FUNC[2]="start_proxy_api_service"

    TEXT[3]="Monitor - Toggle monitor service for updating the channels"
    FUNC[3]="start_contract_monitor_service"

    TEXT[4]="Start all Trinity Nodes services"
    FUNC[4]="start_all_trinity_nodes_service"
}

QUIT=0
quit()
{
    QUIT=1
}

if [ $# != 0 ]; then
    last=0
    for key in "$@"; do
        if [[ "$key" =~ ^-.*$ ]]; then
            break
        fi
        ((last += 1))
    done
    args="${@:$last+1}"

    case "${@:1:$last}" in
        -h|--help) # help command
            help_menu
            ;;

        1|--start-nodeb)
            start_nodeb_service
            ;;

        2|--start-proxy)
            start_proxy_api_service
            ;;

        3|--start-monitor)
            start_contract_monitor_service
            ;;

        4|--start-all)

            ;;
        *)
            >&2 echo "Unknown arguments : $@"
            help_menu
            exit 1
            ;;
    esac
else
    TOTAL_TRINITY_NODES=3
    STEPS[1]="trinity_node_setup_step"
    echo 'QUIT is $QUIT'
    while [ "$QUIT" == "0" ]; do
        OPTION_NUM=1

        for s in $(seq ${#STEPS[@]}) ; do
            ${STEPS[s]}

            echo "----------------------------------------------------------"
            echo -e " TRINITY STEP $s: ${TITLE}"
            echo "----------------------------------------------------------"

            for i in $(seq ${#TEXT[@]}) ; do
                echo -e "[$OPTION_NUM] ${TEXT[i]}"
                OPTIONS[$OPTION_NUM]=${FUNC[i]}
                let "OPTION_NUM+=1"
            done

            unset TEXT
            unset FUNC

            echo ""
        done

        echo "[$OPTION_NUM - Q] To exit Script"
        OPTIONS[$OPTION_NUM]="quit"
        echo ""
        echo -n "Option: "
        read our_entry
    if [ "$our_entry" == "q" ] || [ "$our_entry" == "Q" ]; then
        our_entry=$OPTION_NUM
    fi
    echo ""
    ${OPTIONS[our_entry]}
    done
fi
