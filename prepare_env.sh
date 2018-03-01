#!/bin/sh
BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`

# set the environment variables
export PYTHONPATH=$PYTHONPATH:$BASEDIR/src

# requirements
INSTALL_PACKAGE="$BASEDIR/requirements.txt"
if [ 0 -ne `pipp3 install -r $INSTALL_PACKAGE` ]; then
    echo -e 'Please check your python environment ...'
    echo -e 'requirements packages failed to be installed ...'
fi
