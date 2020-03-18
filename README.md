# PLSC, a Python implemention of LSC

This project is a Python implementation aiming for LDAP to LDAP synchronization. We are inspired by the LSC project (https://lsc-project.org/doku.php)

## Install

For local development we advice to make use of docker. The installation commands are specified below.

## Sample Synchronisation configuration

This is an example of what we need to specify source and destination.

Prepare e **.env** file that contains values for the following attributes:

```
ENV_SRC_LDAP_HOST=ldaps://...
ENV_SRC_LDAP_BASE=...
ENV_SRC_LDAP_PASS=...

ENV_DST_LDAP_DOMAIN=example.org
ENV_DST_LDAP_BASE=dc=example,dc=org
ENV_DST_LDAP_PASS=changethispassword

ENV_API_URL=https://console.jumpcloud.com
ENV_API_KEY=< your JumpCloud API key >
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