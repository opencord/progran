# Progran App


## Add Profile
`curl --user onos:rocks -v -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data '{"Name":"mme2","DlSchedType":"RR","UlSchedType":"RR","DlAllocRBRate":0,"UlAllocRBRate":0,"CellIndividualOffset":1,"AdmControl":0,"MMECfg":{"IPAddr":"10.10.2.7","Port":36412},"DlWifiRate":0,"Handover":{"A3Hysteresis":1,"A3TriggerQuantity":0,"A3offset":0,"A5Hysteresis":1,"A5Thresh1Rsrp":80,"A5Thresh1Rsrq":20,"A5Thresh2Rsrp":90,"A5Thresh2Rsrq":20,"A5TriggerQuantity":0},"Start":"","End":"","Status":1}' http://onos-fabric:8183/onos/progran/profile`


## Add imsi to profile
`curl --user onos:rocks -H "Content-Type: application/json" -X POST -d '{"profile":"slice1", "imsi": "1111111"}'  http://onos-fabric:8183/onos/progran/mwc/connect`

## Update profile
`curl --user onos:rocks -H "Content-Type: application/json" -X POST -d '{"profile":"slice2", "ul": "20","dl":"20"}'  http://onos-fabric:8183/onos/progran/mwc/profile`

## Update Profile
`curl --user onos:rocks -v -H "Accept: application/json" -H "Content-Type: application/json" -X GET --data ' http://onos-fabric:8183/onos/progran/mwc/list`



post
/mwc/profile
/mwc/connect

get
/mwc/list


curl --user onos:rocks -H "Content-Type: application/json" -X POST -d '{"profile":"slice1", "imsi": "12345678"}'  http://10.1.8.65:8181/onos/progran/mwc/connect


curl  -sSL --user onos:rocks  -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data '{"IMSI":"001010000000343"}' http://10.1.8.65:8181/onos/progran/imsi
