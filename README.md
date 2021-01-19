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

### Automatic creation of entities and attributes

The SRAM LDAP contains information about identities of users and the groups
they belong to. However, this is not sufficient when it comes to logging in
user at the SP. First of al the user entry should be extented with for example
the `posixAccount` object class. This is necessary so that the underlying Linux
system is able to determine the uid of the user, its login name, etc.

The `posixAccount` information is deliberately missing from SRAM. The same hold
true for necessary group info, such as gid. In addtion if you would like to
configure you local LDAP to have unique groups for each user, you'll find SRAM
is not supplying that information either. Again, this has all to do with the
design descission SRAM made.

If you require a working LDAP on the Linux level, i.e. you need LDAP to provide
uids, gids and such, the `plsc` script can help you there as well. It is able to
create attributes and new entries while it synchronizes. What is important here
is that `plsc` must be able to remember past generated values. There is no guarantee
that the script will generate the same values on each run. In order to give this
guarentee, generated values must be stored. For this the following
configuration section should be used:

```yaml
storage:
  file:
    path: generated-values.json
```

It simply tells that storage must be used and that the name of the file is
`generated-values.json`. In case of uids and gids, or rather integer sequence,
you can specify a minumum and maximum values. This means that `plsc` starts a
the minumun value and progresses towards the maximum each time a new value is
requested. You also specify this in the `storage` section like so:

```yaml
storage:
  sequences:
    - name: uidNumber
      minimum: 2000
      maximum: 3000
    - name: gidNumber
      minimum: 3000
      maximum: 4000
  database:
    username: plsc
    password: test1234
    table: delena
  file:
    path: generated-values.json
```

In order to use the sequences, and the automatic writing of generated values
to file, you can use the below configuration. What this configuration does is:

- copy the `ou=Groups`
- copy the `uid=People`
- for each entry in `ou=People`
  - drop unwanted attributes from SRAM
  - add missing object class `posixAccount`
  - create missing uid and gid from a sequence as defined in the `storage` section
  - specify the home directory of the user based on the generated uid
  - specify the login shell
  - create a new entry within `ou=Groups` for the unique group of the user
  - create a unique gid for the new group
  - add the user's `dn` to the newly create group, so that the user becomes a
    member of that group
  - add a description to the group

```yaml
sync:
  copy_rdn:
    - rdn: "ou=Groups"
      copy_rdn:
        - rdn: "cn=*"
          replace_basedn: "member"
          add_attributes:
            - attribute: gidNumber
              source: sequence
              name: gidNumber
    - rdn: "ou=People"
      copy_rdn:
        - rdn: "uid=*"
          drop_attribute:
            - objectClass:
              - eduPerson
              - voPerson
            - voPersonExternalAffiliation
            - eduPersonScopedAffiliation
            - voPersonExternalID
            - eduPersonUniqueId
          add_attributes:
            - attribute: objectClass
              source: literal
              value:
                - posixAccount
            - attribute: uidNumber
              source: sequence
              name: uidNumber
            - attribute: gidNumber
              source: attribute
              value: "{{ uidNumber }}"
            - attribute: homeDirectory
              source: attribute
              value: "/home/{{ uid }}"
            - attribute: loginShell
              source: literal
              value: "/bin/bash"
            - entry: "cn={{ uid }},ou=Groups,{{ basedn }}"
              add_attributes:
                - attribute: objectClass
                  source: literal
                  value:
                    - extensibleObject
                    - groupOfMembers
                - attribute: gidNumber
                  source: attribute
                  value: "{{ uidNumber }}"
                - attribute: member
                  source: attribute
                  value: "uid={{ uid }},ou=People,{{ basedn }}"
                - attribute: description
                  source: attribute
                  value: "This '{{ uid }}' group was created automatically."
```

## Running plsc

`plsc` needs a configuration file and is started by: `pipenv run ./plsc
config.yml`

## Ansible code

The folder `ansible` contains roles and configuration files to automate the
deployment of the LDAP server plus the synchronization scrip and the cron job
that periodically performs the synchronization.

The Ansible roles also include Molecule-based tests.
