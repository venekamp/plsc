FROM ubuntu:18.04

WORKDIR /opt/ldap-sync

COPY requirements.txt /opt/ldap-sync/

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3 python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev && \
    pip3 install --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY connection.py \
     jumpcloud.py \
     plsc \
     util.py \
     rsc-config.yml \
     /opt/ldap-sync/

RUN chmod u+x plsc

CMD ["/opt/ldap-sync/plsc", "/opt/ldap-sync/rsc-config.yml"]
