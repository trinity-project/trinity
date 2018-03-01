#!/bin/sh
BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`

# set the environment variables
export PYTHONPATH=$PYTHONPATH:$BASEDIR/src

# requirements
INSTALL_PACKAGE="$BASEDIR/requirements.txt"
pip3 install -r $INSTALL_PACKAGE
if [ 0 -ne $? ]; then
    echo -e 'Please check your python environment ...'
    echo -e 'requirements packages failed to be installed ...'
fi
