#!/usr/bin/env bash

XOS_URL=127.0.0.1
XOS_PORT=9101
XOS_USERNAME=xosadmin@opencord.org
XOS_PWD=ORR13pBZ8yrAZ42QiKhc

echo Sending file $2 to url $XOS_URL:$XOS_PORT/xosapi/v1/$1

curl -H "xos-username: $XOS_USERNAME" -H "xos-password: $XOS_PWD" -X POST --data-binary @$2 http://$XOS_URL:$XOS_PORT/xosapi/v1/$1
