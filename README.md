# PLSC, a Python implemention of LSC

This project is a Python implementation aiming for LDAP to LDAP synchronization. We are inspired by the LSC project (https://lsc-project.org/doku.php)

## Install

For local development we advice to make use of docker. The installation commands are specified below.

## Sample Synchronisation configuration

This is an example of what we need to specify source and destination.

Prepare e **.env** file that contains values for the following attributes:

```
SRC_LDAP_HOST=ldaps://...
SRC_LDAP_BASE=...
SRC_LDAP_PASS=...

DST_LDAP_DOMAIN=example.org
DST_LDAP_BASE=dc=example,dc=org
DST_LDAP_PASS=changethispassword

API_URL=https://console.jumpcloud.com
API_KEY=< your JumpCloud API key >
```

### Local development

Install both **docker** and **docker-compose**

Start local LDAP by:

```
docker-compose up -d ldap
```

Optionally start LDAPphpAdmin:

```
$ docker-compose up -d ldapadmin
```

Run synchronisation script by:
```
$ docker-compose up app
```
