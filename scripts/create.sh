#!/bin/bash

if [ $# -ne 1 ] 
then
    echo "usage: $0 [common_name]"
    exit 1
fi

COMMON_NAME=$1

echo "Generating VPN config for $COMMON_NAME..."

# generate client-config
CLIENT_ID=$((`ls -1 /etc/openvpn/ccd/ | wc -l` + 1))

if [ $CLIENT_ID -ge 110 ]
then
    CLIENT_ID=$(($CLIENT_ID + 1))
fi
IP="10.114.107.$CLIENT_ID"
echo "ifconfig-push $IP 255.255.255.255" > /etc/openvpn/ccd/$COMMON_NAME

echo "client-config saved, ip: $IP"

# generate key
cd ~/ca
source vars > /dev/null
(echo -en "\n\n\n\n\n\n\n\n"; sleep 3; echo -en "\n"; sleep 1; echo -en "\n"; sleep 3; echo -en "yes"; echo -en "\n"; sleep 1; echo -en "yes"; echo -en "\n") | ./build-key $COMMON_NAME > /dev/null 2&>/dev/null

echo "key generated"

# generate ovpn
~/conf/make.sh $COMMON_NAME

echo "VPN config saved"

