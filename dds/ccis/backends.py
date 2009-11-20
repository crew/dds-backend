# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.contrib.auth.models import User, check_password
from django.conf import settings
import ldap


class LDAPBackend(object):
    """LDAPBACKEND_HOST and LDAPBACKEND_DN both need to be defined in the
    settings file to use the LDAPBackend. Currently,
        
        LDAPBACKEND_HOST = 'ldap://cluster.ldap.ccs.neu.edu/'
        LDAPBACKEND_DN   = 'uid=%s,ou=people,dc=ccs,dc=neu,dc=edu'
    
    """

    def authenticate(self, username=None, password=None):
        """Tries to authenticate the username with the given password."""
        if self.filter_out(username):
            return None

        try:
            ldap_conn = ldap.initialize(settings.LDAPBACKEND_HOST)
            q = settings.LDAPBACKEND_DN % username
            (result_type, result_data) = ldap_conn.simple_bind_s(q, password)
            if result_type == ldap.RES_BIND:
                user = self.get_user(username)
                if user is None:
                    user = User(username=username, password='')
                    try:
                        self.set_user_metadata(user, ldap_conn)
                    except:
                        user = User(username=username, password='')
                    user.set_unusable_password()
                    user.save()
                return user
        except ldap.LDAPError, e:
            pass
        return None

    def get_user(self, username):
        try:
            return User.objects.get(username__exact=username)
        except User.DoesNotExist:
            return None

    def set_user_metadata(self, user, ldap_conn):
        """Just a stub."""
        pass

    def filter_out(self, username):
        """Just a stub. Return True to filter out a username."""
        return False


class CCISLDAPBackend(LDAPBackend):
    """An LDAPBackend for CCIS"""
    FILTER = (
        'account', 'postfix', 'rt', 'nandan', 'puppet', 'hobbit', 'zimbra',
        'gkwiki', 'cgiadmin', 'cricket', 'radiusd', 'munctron', 'webapps',
        'syscgi', 'cstyliaold', 'cgiwww', 'vimuser', 'ragroup', 'iadmin',
        'openldap', 'rancid', 'mailman', 'mysql', 'www', 'slipgate',
        'request', 'samba', 'aosd2004', 'sysblog', 'acp4is', 'infopark',
        'bigbro', 'exim', 'openfire', 'clamav', 'minerva', 'jpold',
        'cvsanon', 'iplanet', 'zabbix', 'bigsis', 'forum', 'nagios', 'ftp',
        'netsaint', 'cacti', 'mcsmtpd', 'alexsrvr', 'netreg', 'proto',
        'doxwiki', 'condor',
    )
    LDAP_BASE = 'dc=ccs,dc=neu,dc=edu'

    def set_user_metadata(self, user, ldap_conn):
        result = ldap_conn.search_s('ou=people,%s' % self.LDAP_BASE,
                                    ldap.SCOPE_ONELEVEL,
                                    '(uid=%s)' % user.username)

        if len(result):
            (dn, info) = result[0]
            user.email = info['mail'][0]
            name = info['displayName'][0].split(' ')
            user.first_name = name[0]
            user.last_name = name[-1]

    def filter_out(self, username):
        return username in self.FILTER
