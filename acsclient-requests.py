import yaml
import os
from pwd import getpwnam
from collections import namedtuple
import requests
import json

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

hwconf = yaml.load(open('/opt/ubran/conf/hwinfo.conf'))
ranconf = yaml.load(open('/opt/ubran/conf/ran.conf'))
uid = hwconf['product_uuid']
acsurl = ranconf['acs_url']
mg = ranconf['ran_interfaces']['mg']
mg_admin = ranconf['mg_admin']
mg_conf = '/opt/ubran/bin/config/mg_config.sh'
dirpath = getpwnam(mg_admin).pw_dir + r"/.ssh/"
keystorage ='/opt/ubran/bin/certs/'

def getAuthlib():
        payload = {'hardware_id': uid, 'system_type': 'ub-ran'}
        r = requests.get(acsurl, params=payload, cert=(keystorage +'client.crt', keystorage +'client.key'), verify=keystorage +'ca.crt')

        try:
            jsondict = r.json()
        except ValueError:
            print "not json"
        return jsondict

def setNetworkchange():
        os.chmod(mg_conf, 0777)
        os.popen("%s %s %s %s %s" % (mg_conf, mg, x.ip4_part.cidr_addr, x.ip4_part.gw, x.ip4_part.nameserver))

def registerRAN():
    s = x.ip4_part.cidr_addr.split('/')[0].split('(')[0]
    params = {
        'management_ip' : s,
        'reconfigure'   : 'no',
        'username'      : mg_admin
    }
    r = requests.post(x.apiurl, json=params, auth=(x.auth_part.username, x.auth_part.password), verify=False)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print "You get an HTTPError:", e.message + ", maybe device already registed"



class ACSReply(object):

    AuthInfo = namedtuple('AuthInfo', 'username realm password type')
    IpV4 = namedtuple('IpV4', 'gw cidr_addr nameserver')

    def __init__(self, jsondict):
        self.parse_dict(jsondict)

    def parse_dict(self, jsondict):
        auth_part = jsondict['authinfo']
        self.auth_part = self.AuthInfo(auth_part['username'], auth_part['realm'], auth_part['password'], auth_part['type'])

        ip4_part = jsondict['network']['ipv4']
        self.ip4_part = self.IpV4(ip4_part['gw'], ip4_part['cidr_addr'], ip4_part['nameserver'])

        self.sshkey = jsondict['sshkey']

        self.apiurl = jsondict['apiurl']


class ACSSshKeystore(object):

    def __init__(self, dirpath, mg_admin):
        self.dirpath = dirpath
        self.mg_admin = mg_admin

    def create_dir(self):
        os.mkdir(self.dirpath)
        os.chmod(self.dirpath, 0700)

    def perm_key(self):
        os.chmod(self.dirpath + "authorized_keys", 0600)
        os.chown(self.dirpath + "authorized_keys", getpwnam(self.mg_admin).pw_uid, getpwnam(self.mg_admin).pw_gid)
        os.chown(self.dirpath, getpwnam(self.mg_admin).pw_uid, getpwnam(self.mg_admin).pw_gid)

    def add_key(self, sshkey):
        if not os.path.exists(self.dirpath):
            self.create_dir()
        os.chmod(self.dirpath, 0700)
        with open(self.dirpath + "authorized_keys", 'a+') as f:
                f.seek(0)
                text = f.read()
                self.perm_key()
                if sshkey in text:
                    return
                f.write(sshkey+"\n")


if __name__ == "__main__":
    x = ACSReply(getAuthlib())
    keystore = ACSSshKeystore(dirpath, mg_admin)
    keystore.add_key(x.sshkey)
    setNetworkchange()
    registerRAN()
