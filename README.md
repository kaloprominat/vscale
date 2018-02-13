vscale python api & cli
=====

Requirements:

* python2.7

python3 not tested yet


## Installation

```
pip install git+https://github.com/kaloprominat/vscale.git
```


## Using python api

```
>>> import vscale
>>> vs = vscale.Client(api_token='<your_api_token>')
>>> vs.account()
{u'info': {u'surname': u'<surename>', u'name': u'<name>', u'locale': u'ru', u'country': u'\u0420
\u043e\u0441\u0441\u0438\u044f', u'email': u'<email>', u'middlename': u'<middlename>', u'
state': u'1', u'actdate': u'2017-10-10 21:00:32.594687', u'mobile': u'<mobile>', u'face_id': u'1', u'is_blocked': False, u'id': u'<id>'}, u'status': u'ok'}
>>>
```

## Using CLI

```
export VSCALE_API_TOKEN="<your_api_token>"

vsctl -h
usage: vsctl [-h]
             {account,scalets,backups,locations,images,rplans,sshkeys,billing}
             ...

positional arguments:
  {account,scalets,backups,locations,images,rplans,sshkeys,billing}
                        available resources

optional arguments:
  -h, --help            show this help message and exit
```

### Getting list of scalets

```
vsctl scalets ls
test1: 206988
 --------------------------------------------------------------------------------------------------------------
| Attribute      | Value                                                                                     |
 --------------------------------------------------------------------------------------------------------------
| status         | started                                                                                   |
| hostname       | cs206988                                                                                  |
| locked         | True                                                                                      |
| name           | test1                                                                                     |
| made_from      | ubuntu_16.04_64_001_docker                                                                |
| public_address | {u'netmask': u'255.255.255.0', u'gateway': u'<gw>', u'address': u'<addr>'}                |
| private_address| {}                                                                                        |
| deleted        | None                                                                                      |
| created        | 13.02.2018 08:58:57                                                                       |
| keys           | [{u'id': 14546, u'name': u'mykey'}]                                                       |
| location       | msk0                                                                                      |
| active         | True                                                                                      |
| ctid           | 206988                                                                                    |
| rplan          | small                                                                                     |
| tags           | []                                                                                        |
 --------------------------------------------------------------------------------------------------------------

```

### Creating scalet with default ssh key and connecting to it via ssh

```
vsctl scalets create -n test1 -t ubuntu_16.04_64_001_docker -p small -l msk0 --ssh

test1: 206988
 -------------------------------------------------------
| Attribute      | Value                              |
 -------------------------------------------------------
| status         | defined                            |
| hostname       | cs206988                           |
| locked         | True                               |
| name           | test1                              |
| made_from      | ubuntu_16.04_64_001_docker         |
| public_address | {}                                 |
| created        | 13.02.2018 08:58:57                |
| deleted        | None                               |
| private_address| {}                                 |
| keys           | [{u'id': 14546, u'name': u'mykey'}]|
| location       | msk0                               |
| active         | False                              |
| ctid           | 206988                             |
| rplan          | small                              |
| tags           | []                                 |
 -------------------------------------------------------

Warning: Permanently added '82.202.246.244' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 16.04.3 LTS (GNU/Linux 4.4.0-112-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

root@cs206988:~#
```

### Rebuilding scalet and wait until process is over

```
vsctl scalets rebuild test1 -b

test1: 206988
 --------------------------------------------------------------------------------------------------------------
| Attribute      | Value                                                                                     |
 --------------------------------------------------------------------------------------------------------------
| status         | started                                                                                   |
| hostname       | cs206988                                                                                  |
| locked         | True                                                                                      |
| name           | test1                                                                                     |
| made_from      | ubuntu_16.04_64_001_docker                                                                |
| public_address | {u'netmask': u'255.255.255.0', u'gateway': u'<gw>', u'address': u'<addr>'}                |
| created        | 13.02.2018 08:58:57                                                                       |
| deleted        | None                                                                                      |
| private_address| {}                                                                                        |
| keys           | [{u'id': 14546, u'name': u'mykey'}]                                                       |
| location       | msk0                                                                                      |
| active         | True                                                                                      |
| ctid           | 206988                                                                                    |
| rplan          | small                                                                                     |
| tags           | []                                                                                        |
 --------------------------------------------------------------------------------------------------------------
```

