#!/usr/bin/bash

SERVICENAME="beltlight"
DELETEPICKLE=false

git fetch

if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then

    while true; do
        read -p "Delete saved[pickle] data? [yN] " yn
        case $yn in
            [Yy]* ) DELETEPICKLE=true; break;;
            [Nn]* ) DELETEPICKLE=false; break;;
            * ) DELETEPICKLE=false; break;;
        esac
    done

    echo "stopped $SERVICENAME service"

    if [ "$DELETEPICKLE" = true ] ; then
        rm $SERVICENAME.pickle
        echo "deleted $SERVICENAME.pickle file"
    fi

    git pull

    systemctl start $SERVICENAME
	journalctl -u $SERVICENAME -f
else
    echo "$SERVICENAME already up-to-date"
fi
