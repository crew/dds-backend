from django.contrib.auth.models import User
import ldap
import logging


LDAP_HOST = 'ldap://cluster.ldap.ccs.neu.edu'
LDAP_DN ='uid=%s,ou=people,dc=ccs,dc=neu,dc=edu'


def ldap_match(username, password):
    try:
        logging.info('Connecting to CCIS LDAP')
        conn = ldap.initialize(LDAP_HOST)
        logging.info('Trying to bind %s' % username)
        result = conn.simple_bind_s(LDAP_DN % username, password)
        logging.info('Result = %s' % str(result))
        if result[0] == ldap.RES_BIND:
            return True
    except ldap.LDAPError, e:
        logging.info(str(e))
        return False


class CCISAuthBackend(object):
    def authenticate(self, username=None, password=None):
        if not username or not password:
            return None
        try:
            user = User.objects.get(username=username)
            if ldap_match(username, password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        return User.objects.get(id=user_id)
