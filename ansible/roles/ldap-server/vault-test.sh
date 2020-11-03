#!/bin/bash

ANSIBLE_VAULT_PASSWORD_FILE=~/.vault.txt molecule converge 

# molecule test -- --vault-id @"$HOME"/.vault.txt
