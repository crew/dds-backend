from django.contrib.auth.models import User
import ldap
import logging


LDAP_HOST = 'ldap://cluster.ldap.ccs.neu.edu'
LDAP_DN ='uid=%s,ou=people,dc=ccs,dc=neu,dc=edu'
LDAP_TLS = True


def ldap_match(username, password):
    try:
        logging.info('Connecting to CCIS LDAP')
        conn = ldap.initialize(LDAP_HOST)
        if LDAP_TLS:
            # Start TLS (synchronously)
            conn.start_tls_s()
        logging.info('Trying to bind %s' % username)
        result = conn.simple_bind_s(LDAP_DN % username, password)
        logging.info('Result = %s' % str(result))
        if result[0] == ldap.RES_BIND:
            return True
    except ldap.LDAPError as e:
        logging.info(str(e))
        return False


class CCISAuthBackend(object):
    def authenticate(self, username=None, password=None):
        if not username or not password:
            return
        if not ldap_match(username, password):
            return
        try:
            # XXX Access is limited by the existence of the User object
            # in the database.
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        return User.objects.get(id=user_id)
