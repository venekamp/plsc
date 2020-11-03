# Intro

This Ansible code setup and synchronize a LDAP server based on `docker-compose`. It performs:
* configuration of the system: docker, docker-compose, ...
* installation of synchronization and configuration of scripts (`plsc`)


## LDAP server deployment
The deployment of the LDAP server relies in several configuration files detailed below.

### Ansible vault
The Ansible code contains several secrets encrypted using Ansible Vault. Configure the file `ansible.cfg`, key `vault_password_file` to indicate where the Vault password is stored in your system.

### Ansible inventory
The Ansible inventory (`hosts`) lists the hosts to be managed by the Ansible code and roles. The default file points to `localhost`. Edit the content of `hosts` to point to any other remote machine where the LDAP server will be deployed.

### Deployment
Just run:
```
ansible-playbook site.yml
```

## Testing Ansible code with Molecule
The Ansible roles include Molecule[^1] configuration files for automatic testing. This testing code is based on Vagrant as simulation driver. The testing environment has the following dependencies:
* a working `vagrant`[^2] setup based on *libvirt* as simulation back end.
* `molecule`, `molecule-libvirt` and `molecule-vagrant` PIP packages
* package `libvirt-dev` (Debian/Ubuntu) or `libvirt-devel` (CentOS)
* optionally, `pipenv` to automatically create a Python virtual environment including the PIP packages above

### GitLab deploy token
The Ansible code relies on a GitLab deploy token registered in the [plsc repository](https://git.ia.surfsara.nl/spider-clones/sram-poc/plsc/-/settings/repository) to gain access to the repo and been able to fetch the code. This deploy token is encrypted using Ansible Vault. The Vault password is shared in the SURF Footlocker server.


### Preparing testing virtual environment
The repository includes the file  `ansible/Pipfile` that will create a Python virtual environment with the required PIP dependencies.
```
cd plsc/ansible
pipenv install
```

### Running the Molecule tests
We have to pass somehow the Ansible Vault password to Molecule to successfully test our role.
```
cd plsc/ansible
pipenv shell
cd roles/ldap-server
ANSIBLE_VAULT_PASSWORD_FILE=/path/to/vault-pass.txt molecule test
```


[^1] https://molecule.readthedocs.io/en/latest/
[^2] https://www.vagrantup.com/
