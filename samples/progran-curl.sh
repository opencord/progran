#!/usr/bin/env bash

# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

XOS_URL=127.0.0.1
XOS_PORT=9101
XOS_USERNAME=xosadmin@opencord.org
XOS_PWD=ORR13pBZ8yrAZ42QiKhc

echo Sending file $2 to url $XOS_URL:$XOS_PORT/xosapi/v1/$1

curl -H "xos-username: $XOS_USERNAME" -H "xos-password: $XOS_PWD" -X POST --data-binary @$2 http://$XOS_URL:$XOS_PORT/xosapi/v1/$1
