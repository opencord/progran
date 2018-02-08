# Programmable RAN Slicing (ProgRAN)

The Progan service, available in M-CORD 5.0 (`mcord-cavium` profile), is intended to manage RAN Slicing in M-CORD
taking advantage of the Progran ONOS application designed and built by Netsia.

## How to setup RAN Slicing

As first you'll need to contact Netsia to obtain access to the ONOS Docker image containing
the `progran` application.

Once you have the image you can deploy it on the `head-node` using this `docker-compose.yml` file:

```yaml
version: '2'

services:
   progran:
      image: <onos-progran-image-name>
      ports:
       - "221:22"
       - "6655:6653"
       - "8103:8101"
       - "8183:8181"
       - "9878:9876"
       - "4010:4010"
```

The steps to bring it up are:
- copy this content in a file called `docker-compose.yml` in the home directory of your user
- from that same directory execute `docker-compose -p progran up -d`
- access the ONOS cli in that container with `ssh -p 8103 karaf@0.0.0.0`
- activate the progran application with `app activate org.onosprojet.progran`

Once the application is up and running, you need to tell XOS how to reach it,
to do that follow this steps:
- open the XOS UI and navigate to `Progran > Progran Service`
- select the first entry and update the `onos_address` to `onos-fabric`
- save the model

The Progran service should be now up and running, you can check that the synchronizer
is not printing any error with:
```bash
docker logs -f mcordcavium_xos_progran_synchronizer_1
```

## How to create your first slice

From the XOS UI navigate to `Progran > Handovers` and create your handover configuration, 
then navigate to `Progran > ProgranServiceInstances` and create your first slice.

> NOTE that the `progran` synchronizer will read the state from the ONOS Application, 
> so you can also use the ONOS `progran` cli if you are more familiar with it.   

