# Installing VOLTHA

The following describes how to install VOLTHA (configured
with the EdgeCore OLT device) into R-CORD.

> Note: VOLTHA is not officially included in the release, but it can
> be configured manually, as described below.

## Prerequisites

The starting point is a physical CORD POD with the `rcord` profile, at which
point the manual fabric configuration steps outlined below can be performed.
Make sure your fabric has Internet access (i.e., `vRouter` has been configured).

The ONOS cluster controlling the fabric is located on the CORD head node.
We will deploy VOLTHA and a separate single-instance ONOS cluster for running
the OLT control apps on one of the CORD compute nodes. It doesn’t matter
which compute node is used at this stage, given that we are communicating
with the OLT out-of-band over the management network.

In R-CORD, each PON is identified by a subscriber VLAN tag, and each customer
on a PON is identified by a customer VLAN tag. You will need to decide on an
`s-tag` for the OLT and a `c-tag` for each subscriber that you want to provision.

You will also need to take note of the OpenFlow port numbers of the fabric switch
port where the OLT is connected, as well as the fabric switch port where your
compute node is connected. These port numbers are needed for fabric configuration
later on.

> Note: Currently there is a restriction that the OLT and the node hosting the vSG
> serving the customers on that OLT need to be attached to the same fabric leaf.
> In a small 1-node/1-switch setup this will obviously be the case, but if running
> on a larger setup it is necessary to be aware of the fact that vSG placement is
> constrained.

## Bring Up OLT Device

Install the OLT in your POD. Connect the 1G copper Ethernet port to the
management switch, and connect the top left NNI uplink to one of your
fabric leaf switches.

In CORD 5.0, the EdgeCore ASFvOLT16 OLT is able to PXE boot and have its
OS image automatically installed. Once the OLT is connected to the management
network, start the OLT in ONIE boot mode and the CORD automation will will take
it from there.

You can see the progress of this process in `cord prov list`. The default
username is `root` and default password is `onl`.

### Install ONL, BAL, and VOLTHA Software

Once the OS is ready, there is a set of software that needs to be installed on
the device. Unfortunately, as of the CORD 5.0 release, ONF is unable to
distribute this software, due to licensing issues with the Broadcom SDK.
If you have a relationship with Broadcom, then you can obtain this software
yourself and proceed with the rest of this guide. If not, you will have to wait
until we have clearance to distribute this software.

Assuming you have the software, then simply copy it over to the OLT and install it:

```
scp bal.deb root@<olt_mgmt_ip>:
ssh root@<olt_mgmt_ip>                #password: onl
dpkg -i bal.deb
reboot
```

### Configure NNI Speed

Depending on the switch that the OLT is connected to, you might need to
change the NNI speed. The NNI port on the OLT will default to running at 100G.
If it is connected to a switch that can support 100G then nothing further needs
to be done. If, however, it is connected to a switch that can only support 40G,
then you need to downgrade the speed of the NNI port on the OLT.

On the OLT box itself, edit the file `/broadcom/qax.soc`. Find the lines with
`port …` and add the following line underneath:

```
port ce128 sp=40000
```

Then reboot your OLT.

## Bring Up a vSG Instance

Browse to the XOS UI in a web browser:

```
http://<head_node_ip>/xos
```

Log in with your admin credentials.

On the menu on the left hand side, click on `Volt`, then on `vOLT Tenants`,
and then click the button on the right labelled `Add`. Fill out the form with
values for the new vSG that you want to create.

* C tag: the c-tag for this subscriber
* Creator id: Select ‘1’
* Master serviceinstance id: can leave blank
* Name: can leave blank
* Owner id: Select ‘volt’
* S tag: the s-tag for the OLT PON that the subscriber is attached to
* Service specific attribute: can leave blank
* Service specific id: put the c-tag number in here as well

Now click `Save` and a vSG will be created in the background on a compute node.
This will take a few minutes to fully come up. Again, make sure your fabric has
access to the internet when you do this, because the vSG needs to reach out to the
internet in order to fully come up.

## Configure Fabric ONOS

Once an OLT has been connected to the fabric, the fabric needs some configuration
to forward the data traffic from the OLT to the right compute node running the vSGs.
All vSGs serving customers on a particular PON will be located on the same compute node.

Recall that the fabric controller ONOS is located on the HEAD node The steps in
this section are done on the CORD head node.

The file `/opt/cord_profile/fabric-network-cfg.json` should contain the base
fabric network configuration that you created earlier. In this step we will edit this
file to add some additional configuration to add a tagged VLAN on two fabric switch
ports: the port facing the OLT, and the port facing the compute node where
the vSGs will be hosted.

Create a new section in the `ports` section for the port facing your OLT.
For example:

```
...
“ports” {
    …
    },
    "of:0000cc37ab6180ca/9": {
        "interfaces": [
            {
                "vlan-tagged" : [ 300 ]
            }
        ]
    }
}
```

The port facing your compute node will already have an interface config from
the earlier provisioning of the fabric. We now need to add a new interface config
under the same existing port config for the data traffic from the OLT:

```
...
"of:0000cc37ab6180ca/5": {
    "interfaces": [
        {
            "ips": [ "10.6.1.254/24" ],
                "vlan-untagged" : 1
            },
            {
                "vlan-tagged" : [ 300 ]
            }
        ]
    }
...
```

Run the following command on the head node to refresh the config in
ONOS:

```
$ curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: `cat /opt/credentials/xosadmin@opencord.org`" -X POST --data-binary @/opt/cord_profile/fabric-service.yaml http://localhost:9102/xos-tosca/run
```

Now it is best to log in to the fabric ONOS and verify that the config was
received properly:

```
$ ssh karaf@localhost -p 8101      #password=karaf
```

Run the `interfaces` command and verify that your new `vlanTagged`
interfaces are there:

```
onos> interfaces
...
(unamed): port=of:0000cc37ab6180ca/5 vlanTagged=[300]
(unamed): port=of:0000cc37ab6180ca/9 vlanTagged=[300]
…
```

It’s also best to restart the segment routing app to make sure it picks up the
new config:

```
onos> app deactivate org.onosproject.segmentrouting
onos> app activate org.onosproject.segmentrouting
```

## Run VOLTHA and ONOS

VOLTHA comes with a Docker stack file that runs a full single-node ensemble
of VOLTHA. This means we will run a single copy of all the VOLTHA containers,
plus a single copy of all the infrastructure services that VOLTHA needs to run
(e.g., consul, kafka, zookeeper, fluentd, etc). The stack file will also run an ONOS
instance that we will use to control the logical OpenFlow device that VOLTHA
exposes.

### Prepare ONOS Configuration

Before we run VOLTHA, we’ll need to prepare our ONOS configuration. This is
because the stack file will bring up ONOS at the same time as it brings up
VOLTHA, and ONOS needs to be configured at system startup.

Create a config file that looks like this in `~/network-cfg.json`

```
{
  "devices": {
    "of:0001000000000001": {
      "basic": {
        "driver": "pmc-olt"
      },
      "accessDevice": {
        "uplink": "129",
        "vlan": "300"
      }
    }
  }
}
```

### Prepare the Node for Swarm

Prepare the node as a single-node docker swarm (substitute the dataplane IP
address of the node on which you are running VOLTHA):

```
$ docker swarm init --advertise-addr 10.6.1.2
```

### Run a Released Version of VOLTHA

Download the VOLTHA run script:

```
$ curl https://raw.githubusercontent.com/opencord/voltha/voltha-1.2/scripts/run-voltha.sh > run-voltha.sh
$ chmod +x run-voltha.sh
```

Then you can start voltha like this:

```
$ ONOS_CONFIG=~/network-cfg.json REPOSITORY=voltha/ TAG=1.2.1 ./run-voltha.sh start
```

Now we have started a single-node VOLTHA stack. You can use the following
command to see the various containers that are runnning as part of the stack:

```
$ docker stack ps voltha
```

## Provision the OLT + ONU

Access VOLTHA's CLI with:

```
$ ssh voltha@localhost -p 5022
```

Run the health command and verify you get this output:

```
(voltha) health
{
    "state": "HEALTHY"
}
```

Now we can provision our OLT:

```
(voltha) preprovision_olt -t asfvolt16_olt -H <olt_mgmt_ip>:59991
success (device id = 0001f6f4595fdc93)

(voltha) enable 0001f6f4595fdc93
enabling 0001f6f4595fdc93
waiting for device to be enabled...
waiting for device to be enabled...
waiting for device to be enabled...
```

This will start to provision the device and will take approximately two
minutes. During this time you should see logs scrolling by in the
`bal_core_dist` and `voltha_bal_driver` apps on the OLT. The "waiting for
device to be enabled" message will stop once the device has finished being
provisioned.

Next, add the OLT configuration. The following is a series of
commands that need to be entered into the VOLTHA CLI in order to configure
an OLT and ONU. Pay attention to the device ID in the channel termination command,
(`0001bb590711de28`) as this will need to be changed to match your OLT's device ID.

```
(voltha) xpon
(voltha-xpon ) channel_group create -n "Manhattan" -d "Channel Group for Manhattan" -a up -p 100 -s 000000 -r raman_none
(voltha-xpon ) channel_partition create -n "WTC" -d "Channel Partition for World Trade Center in Manhattan" -a up -r 20 -o 0 -f false -m false -u serial_number -c "Manhattan"
(voltha-xpon ) channel_pair create -n "PON port" -d "Channel Pair for Freedom Tower in WTC" -a up -r (voltha-xpon ) down_10_up_10 -t channelpair -g "Manhattan" -p "WTC" -i 0 -o class_a
(voltha-xpon ) traffic_descriptor_profile create -n "TDP 1" -f 100000 -a 500000 -m 1000000 -p 1 -w 1 -e additional_bw_eligibility_indicator_none
(voltha-xpon ) channel_termination create -i 0001bb590711de28 -n "PON port" -d "Channel Termination for Freedom Tower" -a up -r "PON port" -c "AT&T WTC OLT"
```
Then for every ONU that you want to bring up, run the following commands in the VOLTHA CLI.
The value of the ONU serial number (`BRCM12345678`) needs to be changed to match your
ONU's serial number.

```
(voltha-xpon ) vont_ani create -n "ATT Golden User" -d "ATT Golden User in Freedom Tower" -a up -p "WTC" -s "BRCM12345678" -r "PON port" -o 1

# Wait for 5 sec for ONT to come up
(voltha-xpon ) ont_ani create -n "ATT Golden User" -d "ATT Golden User in Freedom Tower" -a up -u true -m false
(voltha-xpon ) tcont create -n "TCont 1" -r "ATT Golden User" -t "TDP 1"

# Wait for 5 sec for scheduler configuration to finish.
(voltha-xpon ) v_enet create -n "Enet UNI 1" -d "Ethernet port - 1" -a up -r "ATT Golden User"
(voltha-xpon ) gem_port create -n "Gemport 1" -r "Enet UNI 1" -c 2 -a true -t "TCont 1"
```

At this point the ONU should have been provisioned and ready to have its
subscriber VLANs programmed by ONOS.

## Provision a Subscriber in ONOS

Now we need to provision a subscriber in ONOS. ONOS will then send flow rules
to forward the subscriber’s traffic to the VOLTHA logical device, and VOLTHA will
take these flow rules and configure the PON accordingly.

On the node where VOLTHA is running, you can access the ONOS CLI using:

```
$ ssh karaf@localhost -p 8101           #password=karaf
```

In the previous step we already provisioned VOLTHA with an OLT, so it should
have automatically connected to this new ONOS instance. Running `devices`
and `ports` should show one OLT device with two ports, an NNI port and a UNI
port.

```
onos> devices
id=of:0001000000000001, available=true, local-status=connected 34m43s ago, role=MASTER, type=SWITCH, mfr=cord project, hw=n/a, sw=logical device for Edgecore ASFvOLT16 OLT, serial=10.6.0.199:59991, driver=pmc-olt, channelId=172.25.0.1:55015, locType=geo, managementAddress=172.25.0.1, name=of:0001000000000001, protocol=OF_13
onos> ports
id=of:0001000000000001, available=true, local-status=connected 34m45s ago, role=MASTER, type=SWITCH, mfr=cord project, hw=n/a, sw=logical device for Edgecore ASFvOLT16 OLT, serial=10.6.0.199:59991, driver=pmc-olt, channelId=172.25.0.1:55015, locType=geo, managementAddress=172.25.0.1, name=of:0001000000000001, protocol=OF_13
  port=21, state=enabled, type=fiber, speed=0 , portName=Enet UNI 1, portMac=00:00:00:01:00:15
  port=129, state=enabled, type=fiber, speed=0 , portName=nni, portMac=00:00:00:00:00:81
```

If this is all correct, then the final step is to use the ONOS CLI to provision subscriber VLANs on the PON:

```
onos> add-subscriber-access <olt_dpid> <uni_port> <c_vlan>
e.g., add-subscriber-access of:0001000000000001 21 400
```

If all is going well, traffic should be able to flow through the PON, to the vSG
and out to the Internet. If you place a client behind the ONU it should be able to
DHCP and get an address from the vSG, then reach the Internet using the vSG
as its default gateway.

## Troubleshooting

If you ever need to reset the system, then you can stop VOLTHA like this:

```
$ ./run-voltha.sh stop
```

Then reboot the OLT to ensure that it is in a fresh state to be reprovisioned.