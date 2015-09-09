import yaml
import json
import os
import urllib2, urllib
from pwd import getpwnam
from collections import namedtuple

hwconf = yaml.load(open('/opt/ubran/conf/hwinfo.conf'))
ranconf = yaml.load(open('/opt/ubran/conf/ran.conf'))
uid = hwconf['product_uuid']
acsurl = ranconf['acs_url']
mg = ranconf['ran_interfaces']['mg']
mg_admin = ranconf['mg_admin']
mg_conf = '/opt/ubran/bin/config/mg_config.sh'
dirpath = getpwnam(mg_admin).pw_dir + r"/.ssh/"


def getAuthlib():
        payload = {'hardware_id': uid, 'system_type': 'ub-ran'}
        encoded_args = urllib.urlencode(payload)
        url = acsurl +'?' + encoded_args
        url = 'http://172.16.0.165:8000/acserver/?hardware_id=42BF3C8A-DFF8-AD07-88FB-5C168CA00991&system_type=ub-ran'
        jsonreply =urllib2.urlopen(url).read()
        jsondict = json.loads(jsonreply)
        return jsondict

def setNetworkchange():
        os.chmod(mg_conf, 0777)
        os.popen("%s %s %s %s %s" % (mg_conf, mg, x.ip4_part.cidr_addr, x.ip4_part.gw, x.ip4_part.nameserver))

def setupAuth():
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm=x.auth_part.realm,
        uri=x.apiurl,
        user=x.auth_part.username,
        passwd=x.auth_part.password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

def registerRAN():
    s = x.ip4_part.cidr_addr.split('/')[0].split('(')[0]
    params = {
        'management_ip' : s,
        'reconfigure'   : 'no',
        'username'      : mg_admin
    }

    encoded_params = urllib.urlencode(params.items())

    try:
        urllib2.urlopen(x.apiurl, encoded_params)

    except urllib2.HTTPError as e:
        try:
            print e.read()
        except AttributeError:
            print e
            raise

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
                else:
                    f.write(sshkey+"\n")


if __name__ == "__main__":

    x = ACSReply(getAuthlib())
    keystore = ACSSshKeystore(dirpath, mg_admin)
    keystore.add_key(x.sshkey)
    setNetworkchange()
    setupAuth()
    registerRAN()
s