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
* a working `vagrant`[^2] setup, based on *VirtualBox* or *libvirt* as simulation back ends.
* `molecule` and `molecule-vagrant` PIP packages
* optionally, `pipenv` to automatically create a Python virtual environment including the PIP packages above

### Preparing testing virtual environment
The repository includes the file  `ansible/Pipfile` that will create a Python virtual environment with the required PIP dependencies.
```
cd plsc/ansible
pipenv install
```

### Running the Molecule tests
```
cd plsc/ansible
pipenv shell
cd roles/ldap-server
molecule test
```


[^1] https://molecule.readthedocs.io/en/latest/
[^2] https://www.vagrantup.com/
