import ldap
import ldap.modlist

import common


class LDAPinvalidCredentials(Exception):
    """Invalid credentials for given LDAP"""
    def __init__(self, ldap_name):
        self.ldap_name = ldap_name


def ldap_encode(entry):
    r = {}
    for k, v in entry.items():
        rv = []
        for ev in v:
            rv.append(ev.encode())
        r[k] = rv
    return r


def ldap_decode(entry):
    r = {}
    for k, v in entry.items():
        rv = []
        for ev in v:
            rv.append(ev.decode())
        r[k] = rv
    return r


class LDAPConnection(object):

    # LDAP connection, private
    __c = None

    # BaseDN, public
    basedn = None

    def __init__(self, config, dry_run, verbose_level, *kargs):
        ldap_config = config
        for i in kargs:
            ldap_config = ldap_config[i]

        self.ldap_name = common.get_value_from_config(config, *kargs, 'name')
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
        ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)

        if dry_run:
            print('Switching to dry_run mode. No modification will be made.')

        self.basedn = common.get_value_from_config(config, *kargs, 'basedn')
        self.dry_run = dry_run
        self.verbose_level = verbose_level

        uri = common.get_value_from_config(config, *kargs, 'uri')
        binddn = common.get_value_from_config(config, *kargs, 'binddn')
        passwd = common.get_value_from_config(config, *kargs, 'passwd')

        self.__c = ldap.initialize(uri)

        try:
            if binddn == 'external':
                self.__c.sasl_external_bind_s()
            else:
                self.__c.simple_bind_s(binddn, passwd)
        except Exception as e:
            raise LDAPinvalidCredentials(self.ldap_name)


    def __search(self, basedn, fltr='(ObjectClass=*)', attrs=[], scope=ldap.SCOPE_SUBTREE):
        if not basedn:
            basedn = self.basedn
        return self.__c.search_s(basedn, scope, fltr, attrs)

    def find(self, basedn, fltr='(ObjectClass=*)', attrs=[], scope=ldap.SCOPE_SUBTREE):
        dns = {}
        try:
            r = self.__search(basedn, fltr, attrs, scope)
            for dn, entry in r:
                dns[dn] = ldap_decode(entry)
        except Exception as e:
            print("find: {}".format(e))
        return dns

    def rfind(self, basedn, fltr='(ObjectClass=*)', attrs=[], scope=ldap.SCOPE_SUBTREE):
        if basedn:
            b = "{},{}".format(basedn, self.basedn)
        else:
            b = self.basedn
        return self.find(b, fltr, attrs, scope)

    def add(self, dn, entry):
        addlist = ldap.modlist.addModlist(ldap_encode(entry))

        if not self.dry_run:
            try:
                self.__c.add_s(dn, addlist)
            except Exception as e:
                #pass
                print("{}\n  {}".format(dn, e))
        else:
            if self.verbose_level > 0:
                print('\033[38;5;208mLDAP add:')
                self.PrettyPrint(addlist)


        return addlist

    def modify(self, dn, old_entry, new_entry):
        modlist = ldap.modlist.modifyModlist(
            ldap_encode(old_entry), ldap_encode(new_entry))

        if not self.dry_run:
            try:
                self.__c.modify_s(dn, modlist)
            except Exception as e:
                #pass
                print("{}\n  {}".format(dn, e))
        else:
            if self.verbose_level > 0:
                print('LDAP modify:')
                self.PrettyPrint(modlist)

        return modlist


    def add_or_modify(self, dn, entry):
        try:
            r = self.__c.search_s(dn, ldap.SCOPE_BASE, '(objectClass=*)', [])
            old_entry = ldap_decode(r[0][1])
            self.modify(dn, old_entry, entry)
        except ldap.NO_SUCH_OBJECT:
            self.add(dn, entry)


    def delete(self, dn):
        if self.dry_run:
            print(f'LDAP delete DN: {dn}')
            return

        try:
            self.__c.delete_s(dn)
        except Exception as e:
            #pass
            print("{}\n  {}".format(dn, e))

    def get_sequence(self, dn):
        seq = 1000
        r = self.__c.search_s(dn, ldap.SCOPE_BASE)
        for dn, old_entry in r:
            old_entry = ldap_decode(old_entry)
            new_entry = old_entry.copy()
            seq = int(new_entry['serialNumber'][0]) + 1
            new_entry['serialNumber'] = [str(seq)]
            self.modify(dn, old_entry, new_entry)
        return seq


    def PrettyPrint(self, msg):
        for m in msg:
            attribute_name, attribute_values = m
            print(f'  \033[33;1m{attribute_name}: ', end='')
            for value in attribute_values:
                v = value.decode('utf-8')
                print(f'\033[0m\033[36;3m{v.rstrip()}', end='')
                if value != attribute_values[-1]:
                    print(', ', end='')
            print('\033[0m')
