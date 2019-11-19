#!/usr/bin/env python

# Written by Harry Kodden <harry.kodden@surfnet.nl>

import sys
import re
import os, yaml, json
import uuid
import json
import requests

def equal(a, b):
    return (a.lower() == b.lower())

def base_email(a):
    return "{}@{}".format(a.rsplit('@')[0].rsplit('+')[0], a.rsplit('@')[1])

def equal_email(a, b):
    return equal(base_email(a), base_email(b))

def valid_email(email):
    if not email:
       print("No email address found !")
       return False

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
       print("Email address: {} is not valid !".format(email))
       return False

    return True

class JumpCloud(object):

    url = None
    key = None
    grp = None

    persons = {}
    groups = {}
    foreign_uid = {}

    def __init__(self, url, key, grp=None):
      self.url = url
      self.key = key
      self.grp = grp

      for record in self.api('/api/systemusers')['results']:
        self.persons[record['id']] = { 'checked': False, 'record': record }

      for record in self.api('/api/v2/usergroups'):
        self.groups[record['id']]  = { 'name': record['name'], 'members': {} }

      for u in self.persons.keys():
        for g in self.api('/api/v2/users/{}/memberof'.format(u)):
            self.groups[g['id']]['members'][u] = False

    def __str__(self):
        return "Persons: {}\nGroups: {}".format(self.persons, self.groups)

    def api(self, request, method='GET', data=None):

      print("API: {} {} ...".format(method, request))

      try:
        headers = {
          'Accept' : 'application/json',
          'x-api-key': self.key
        }

        if data:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data)
            print(data)

        r = requests.request(method, url="{}{}".format(self.url, request), headers=headers, data=data)

        if r.status_code in [200, 201, 204]:
           try:
              return json.loads(r.text)
           except:
              return r.text
        else:
           print("API: {} {} returns: {} {}".format(method, request, r.status_code, r.text))

      except Exception as e:
        print("API Exception: {}".format(str(e)))

      return None


    def username(self, firstname, lastname):
        n = 0

        suggestion = "{}.{}".format(firstname, lastname).lower().replace(' ','')

        while True:
          if suggestion.startswith("."):
             suggestion = suggestion[1:]

          collision = False
          for uid in self.persons.keys():
            if equal(self.persons[uid]['record']['username'], suggestion):
               collision = True
               break

          if not collision:
             return suggestion

          n = n+1
          suggestion = "{}.{}.{}".format(firstname, lastname, n).lower().replace(' ','')


    def lookup_person(self, email):
      for uid in self.persons.keys():
        if equal_email(self.persons[uid]['record']['email'], email):
          return uid

      return None


    def lookup_group(self, name):
      print("Lookup: {}".format(name))
      for gid in self.groups.keys():
        if equal(self.groups[gid]['name'], name):
          return gid

      return None


    def person(self, **kwargs):
      src_uid = kwargs.get('uid')[0]
      firstname = kwargs.get('givenName', [''])[0]
      lastname = kwargs.get('sn', [''])[0]
      email = kwargs.get('mail', [''])[0]

      ssh_keys = []
      for k in kwargs.get('sshPublicKey', []):
        try:
          _, public_key, name = k.strip().split(' ')
          ssh_keys.append({ 'public_key': public_key, 'name': name })
        except:
          pass

      if not valid_email(email):
        print("User: {} {} is not registered as JumpCloud user, since he is not having a valid email address".format(firstname, lastname))
        return

      uid = self.lookup_person(email)

      self.foreign_uid[src_uid] = uid

      if uid:
        if not equal(firstname, self.persons[uid]['record']['firstname']) or not equal(lastname, self.persons[uid]['record']['lastname']):
           print("Updating person: {} {}".format(firstname, lastname))

           self.api('/api/systemusers/{}'.format(uid), method='PUT', data = {
              'firstname': firstname,
              'lastname': lastname
           })

        self.persons[uid]['checked'] = True
      else:
        for i in range(0,5):
          print("Adding person: {} {}".format(firstname, lastname))

          record = self.api('/api/systemusers', method='POST', data = {
            'username': self.username(firstname, lastname),
            'email': email,
            'firstname': firstname,
            'lastname': lastname
          })

          if record:
            uid = record.get('_id', None)

          if uid:
            break;

          email = "{}+{}@{}".format(
            email.split('@')[0].split('+')[0], i+1, email.split('@')[1]
          )

        if not uid:
          raise Exception("Cannot add user: {}".format(email))

        self.persons[uid] = { 'checked': True, 'record': record }


      # Check our src keys, add the one that do not yet exist...
      for src_key in ssh_keys:
        exists = False

        for dst_key in self.persons[uid]['record']['ssh_keys']:
          if equal(src_key['public_key'], dst_key['public_key']):
            exists = True
            break

        if not exists:
          print("Adding SSH key {}".format(src_key['name']))
          self.api('/api/systemusers/{}/sshkeys'.format(uid), method='POST', data = {
           'public_key': src_key['public_key'],
           'name': src_key['name']
          })

      # Check the existing keys, delete the ones that are no longer valid...
      for dst_key in self.persons[uid]['record']['ssh_keys']:
        valid = False

        for src_key in ssh_keys:
          if equal(src_key['public_key'], dst_key['public_key']):
            valid = True
            break

        if not valid:
          print("Delete SHS key {}".format(dst_key['name']))
          self.api('/api/systemusers/{}/sshkeys/{}'.format(uid, dst_key['id']), method='DELETE')

    def group(self, name, members):

      if self.grp and not equal(self.grp, name):
          print("Skipping group: {} , because we only look for {}".format(name, self.grp))
          return

      gid = self.lookup_group(name)

      if not gid:
        print("Group {} does not yet exist".format(name))

        record = self.api('/api/v2/usergroups', method='POST', data = {
            'name': name
          }
        )

        gid = record['id']
        self.groups[gid] = {'name': name, 'members': {}}

      for memberUid in members:
        uid = self.foreign_uid[memberUid]

        if not uid:
          print("member: {} is not registered as JumpCloud group member, since he is not a valid JumpCloud person".format(memberUid))
          continue

        if uid not in self.groups[gid]['members']:
          print("Adding {} to group {}".format(uid, gid))

          self.api('/api/v2/usergroups/{}/members'.format(gid), method='POST', data = {
              "op": "add", "type": "user", "id": uid
            }
          )

        self.groups[gid]['members'][uid] = True

    def cleanup(self):
      print("Cleaning....")

      #Cleanup groups...
      for gid in self.groups.keys():

        for uid in list(self.groups[gid]['members'].keys()):

          if not self.groups[gid]['members'][uid]:
            print("Removing {} from group {}".format(uid, gid))

            self.api('/api/v2/usergroups/{}/members'.format(gid), method='POST', data = {
                "op": "remove", "type": "user", "id": uid
              }
            )

            del self.groups[gid]['members'][uid]

        if len(self.groups[gid]['members'].keys()) == 0:
          print("Delete group {}".format(gid))

          self.api("/api/v2/usergroups/{}".format(gid), method='DELETE')

      # Remove persons no longer valid...
      for uid in self.persons.keys():
        print("Validating: {}".format(uid))

        if not self.persons[uid]['checked']:
          print("Delete person {}".format(uid))
          self.api("/api/systemusers/{}".format(uid), method='DELETE')
