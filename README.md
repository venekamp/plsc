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

### Configuration: sync

## Running plsc

`plsc` needs a configuration file and is started by: `pipenv run ./plsc
config.yml`
