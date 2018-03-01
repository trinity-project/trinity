#!/bin/sh

BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`
NODEB_DIR="$BASEDIR/src/NodeB"
TRINITY_PROXY="$BASEDIR/src/proxy"
MONITOR_CONTRACT="$BASEDIR/src/neo_python_tool"

LOG_FILE="/var/log/rebase_code.log"

help_menu()
{
    echo "Usage : bash start_trinity.sh [OPTIONS]"
    echo "Details of OPTIONS and Parameters"
    echo
    echo "-h, --help                     Display the help and exit."
    echo
    echo "0, ----start-nodeb             Start trinity NODE-B."
    echo "1, ----start-proxy             Start trinity proxy api node."
    echo "2, ----start-monitor           Start contract monitor node."
    echo "3, ----start-nodeb             Start all nodes above."
}

start_nodeb_app()
{
    cd $NODEB_DIR && python3 ./runserver.py &
}

start_proxy_api_app()
{
    cd $TRINITY_PROXY && python3 api.py &
}

start_contract_monitor_app()
{
    cd $MONITOR_CONTRACT && python3 monitor_contract.py &
}

while [ $# != 0 ]; do
    curr_option="$1"
    case "$curr_option" in
        -h|--help) # help command
            help_menu
            exit 0
            ;;

        0|--start-nodeb)
            start_nodeb_app
            exit 0
            ;;

        1|--start-proxy)
            start_proxy_api_app
            exit 0
            ;;

        2|--start-monitor)
            start_contract_monitor_app
            exit 0
            ;;

        3|--start-all)
            start_nodeb_app
            sleep 5

            start_proxy_api_app
            sleep 5

            start_contract_monitor_app
            exit 0
            ;;

        *)
            echo "UnKnown argument : $#"
            help_menu
            exit 0
            ;;
    esac
    shift
done
