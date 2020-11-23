# PLSC: syncing and modifying two LDAPs in python

Originally inspired on LSC (LDAP Synchronization Connector), plsc synchronizes
two LDAPs. Earlier versions of plsc required adapting the python code itself.
Which works well, but doing this multiple times is perhaps not the most
efficient way of doing things. Therefore a new approach is taken. Instead of
modifying the python code, the input configuration for plsc is extended to
contain a description of what needs to be done. As a consequence the current
version has deviated for the earlier versions considerably

## Requirements

In order to run the plsc script, you'll need python 3.6 or above. Python 3.8
has been used through the development. Although not strictly necessary,
`pipenv` has been used as well. If you `docker-compose` provides with an easy
way to setup a local LDAP if you wish to use one.

## Installing plsc

Copy all the files from the repo and run `pipenv install` to install the
dependencies of the `plsc` script.

## Configuration file

The configuration file consists out of two blocks: `ldap` and `sync`. The
first block is for specifying necessary info for connecting to both the source
LDAP and the destination LDAP. The `sync` block describes the source ldap tree
and what needs to be synced.

### Configuration: ldap

The `ldap` section contains two entries: `src` and `dst`. Both hold the same
key values pairs. The former describes the source LDAP, while the latter the
destination LDAP.

|key|comment|
|-|-|
|`name`|a string containing the name given to the LDAP|
|`uri`|the URI of the LDAP. This includes the protocol, thus `ldaps://` or `ldap://` for example|
|`basedn`|the basedn of the LDAP|
|`binddn`|the DN that is allowed to read access|
|`passwd`|the password for the binddn|

#### Example

```yaml
ldap:
  src:
    name: "Source LDAP"
    uri: ldaps://ldap.example.com
    basedn: dc=a,adc=project,dc=example,dc=com
    binddn: cn=admin,dc=a,adc=project,dc=example,dc=com
    passwd: SecretOne
  dst:
    name: "Destination LDAP"
    uri: ldaps://ldap.example.org
    basedn: dc=z,adc=project,dc=example,dc=org
    binddn: cn=admin,dc=z,adc=project,dc=example,dc=org
    passwd: SecreTwot
```

### Configuration: sync

The `sync` section of the configuration specifies what needs to be synced
from the source LDAP and possibly how. The first thing you need to do is to
tell what to do. That is done with `copy_rdn` and it tells that you want to
copy a relative DN. For example, if you want to copy the `ou=People` that
sits directly under your basedn, you specify the rdn as part of `copy_rdn`
command. Thus:

```yaml
sync:
  copy_rdn:
   - rdn: "ou=People"
```

This would copy the `ou=People` only! If there are entries for `ou=People`,
they are not copied. If you want to do that you have to tell the sync script
just that. In other words, you have to tell to copy those entries as well. Thus:

```yaml
sync:
  copy_rdn:
    - rdn: "ou=People"
    copy_rdn:
      - rdn: "uid=somebody"
```

Although one could specify each uid, this approach does not scale. Therefore
instead of `rdn: "uid=somebody"` you should use: `rnd: "uid=*"`. This simply
itterates over all the uids of the People entry.

The final version of this becomes:

```yaml
sync:
  copy_rdn:
    - rdn: "ou=People"
    copy_rdn:
      - rdn: "uid=*"
```

And it copies the `ou=People` and all its `uid`s that are defined beneath it.

## Running plsc

`plsc` needs a configuration file and is started by: `pipenv run ./plsc
config.yml`

## Ansible code

The folder `ansible` contains roles and configuration files to automate the
deployment of the LDAP server plus the synchronization scrip and the cron job
that periodically performs the synchronization.

The Ansible roles also include Molecule-based tests.
