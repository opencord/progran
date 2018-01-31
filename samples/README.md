# Samples

This directory contains sample data to create Progran related models.

## Example setup

Create an IMSI:

```bash
bash progran-curl.sh mcord/mcordsubscriberinstances imsi.json
```

Create an enodeb:

```bash
bash progran-curl.sh progran/enodebs enodeb.json
```

Create an handover:

```bash
bash progran-curl.sh progran/handovers handover.json
```

Create a Profile: note that you'll need to replace `enodeb_id` and `handover_id` with existing values

```bash
bash progran-curl.sh progran/progranserviceinstances profile.json
```

curl -U xosadmin@opencord.org:bash -X PUT --data-binary @profile.json http://127.0.0.1:9101/xosapi/v1/progran/progranserviceinstances/4