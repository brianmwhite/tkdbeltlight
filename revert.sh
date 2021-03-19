#!/usr/bin/bash

SERVICENAME="beltlight"
DELETEPICKLE=false

echo "reverting code to last version... "

while true; do
    read -p "Delete saved[pickle] data? [yN] " yn
    case $yn in
        [Yy]* ) DELETEPICKLE=true; break;;
        [Nn]* ) DELETEPICKLE=false; break;;
        * ) DELETEPICKLE=false; break;;
    esac
done

echo "stopping $SERVICENAME service"
systemctl stop $SERVICENAME

if [ "$DELETEPICKLE" = true ] ; then
    echo "deleting $SERVICENAME.pickle file"
    rm $SERVICENAME.pickle
fi

echo "resetting code to prior version"
git reset --hard master@{1}

echo "starting $SERVICENAME service"
systemctl start $SERVICENAME

echo "viewing logs for $SERVICENAME service"
journalctl -u $SERVICENAME -f
