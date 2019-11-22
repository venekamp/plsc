FROM ubuntu:18.04

WORKDIR /opt/ldap-sync

COPY connection.py \
     jumpcloud.py \
     plsc \
     requirements.txt \
     util.py \
     /opt/ldap-sync/

RUN apt update && \
    apt install -y python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev && \
    pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["/opt/ldap-sync/plsc", "/opt/ldap-sync/rsc-confg.yml"]
