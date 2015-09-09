import yaml
import json
import os
import urllib2, urllib


####                       ####
#  get json list with param   #
####                       ####

def getAuthlib():
    uid = yaml.load(open('/opt/ubran/conf/hwinfo.conf').read())['product_uuid']
    print uid
    acsurl = yaml.load(open('/opt/ubran/conf/ran.conf').read())['acs_url']
    payload = {'hardware_id': uid, 'system_type': 'ub-ran'}
    encoded_args = urllib.urlencode(payload)
    url = 'http://172.16.0.165:8000/acserver/?' + encoded_args
    return urllib2.urlopen(url).read()
getAuthlib()


d = json.loads(getAuthlib())


####                       ####
#get anad save ssh key in file#
####                       ####
def addsshkey():
    print d['sshkey']
    if os.path.exists("/home/codsadmin/.ssh/"):
        print("folder exist")
        if os.path.exists("/home/codsadmin/.ssh/authorized_keys"):
            os.chmod(r"/home/codsadmin/.ssh/", 0700)
            f = open("/home/codsadmin/.ssh/authorized_keys", 'r')
            text = f.read()
            if d['sshkey'] in text:
                print 'Key already exist'
                f.close()
            else:
                f = open("/home/codsadmin/.ssh/authorized_keys", 'a')
                print 'Key append in keys file'
                f.write(d['sshkey'])
                f.close()
                os.chmod(r"/home/codsadmin/.ssh/authorized_keys", 0600)

        else:
            print ("file with keys created")
            os.chmod(r"/home/codsadmin/.ssh/", 0700)
            f = open("/home/codsadmin/.ssh/authorized_keys", 'w')
            f.write(d['sshkey'])
            f.close()
            os.chmod(r"/home/codsadmin/.ssh/authorized_keys", 0600)

    else:
        print(" folder and keys file will be created now")
        os.mkdir("/home/codsadmin/.ssh")
        os.chmod(r"/home/codsadmin/.ssh/", 0700)
        f = open("/home/codsadmin/.ssh/authorized_keys", 'w')
        f.write(d['sshkey'])
        f.close()
        os.chmod(r"/home/codsadmin/.ssh/authorized_keys", 0600)



#by use this
#remote$ [ -d ~/.ssh ] || (mkdir ~/.ssh; chmod 711 ~/.ssh) # create dir and add priv
#remote$ cat ~/id_rsa.pub >> ~/.ssh/authorized_keys        # add openkey
#remote$ chmod 600 ~/.ssh/authorized_keys                  # do right prive

addsshkey()

####                       ####
# change network param ub-ran #
####                       ####
#
def networkchange():

    mg = yaml.load(open('/opt/ubran/conf/ran.conf').read())['ran_interfaces']['mg']
    print mg
    os.chmod(r"/opt/ubran/bin/config/mg_config.sh", 0777)
    os.popen("/opt/ubran/bin/config/mg_config.sh " + mg + " " + d['network']['ipv4']['cidr_addr'] + " " + d['network']['ipv4']['gw'] + " " + d['network']['ipv4']['nameserver'])
    print "Ip setting changed"
networkchange()

# ####                       ####
# #  conntect to public api     #
# ####                       ####
# #d['apiurl']  return bad url  "apiurl": "https:///nms/acs/inventory/ub-ran"
#
#
# def setupAuth():
#     # auth_handler = urllib2.HTTPBasicAuthHandler()
#     # print d['authinfo']['username'], d['authinfo']['password'], d['authinfo']['realm'], d['apiurl']
#     # auth_handler.add_password(realm=d['authinfo']['realm'],
#     #     uri=d['apiurl'],
#     #     user=d['authinfo']['username'],
#     #     passwd=d['authinfo']['password'])
#     # print auth_handler
#     # opener = urllib2.build_opener(auth_handler)
#     #
#     # urllib2.install_opener(opener)
#
#     values = {'realm' : d['authinfo']['realm'],
#           'user' : d['authinfo']['username'],
#           'passwd' : d['authinfo']['password']}
#     print values
#     data = urllib.urlencode(values)
#     print data
#     req = urllib2.Request(d['apiurl'], data)
#     print req
#     response = urllib2.urlopen(req)
#     the_page = response.read()
#     print the_page
#
# setupAuth()

def getAuthlib():
    uid = yaml.load(open('/opt/ubran/conf/hwinfo.conf').read())['product_uuid']
    print uid
    acsurl = yaml.load(open('/opt/ubran/conf/ran.conf').read())['acs_url']
    payload = {'hardware_id': uid, 'system_type': 'ub-ran'}
    encoded_args = urllib.urlencode(payload)
    url = 'http://172.16.0.165:8000/acserver/?' + encoded_args
    return urllib2.urlopen(url).read()
getAuthlib()



def setupAuth():
    auth_handler = urllib2.HTTPBasicAuthHandler()

    auth_handler.add_password(realm=d['authinfo']['realm'],
        uri=d['apiurl'],
        user=d['authinfo']['username'],
        passwd=d['authinfo']['password'])
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
setupAuth()

def registerRAN():

    s =d['network']['ipv4']['cidr_addr'].split('/')[0].split('(')[0]
    print s
    params = {
        'management_ip' : s,
        'reconfigure'   : 'no',
        'password'      : d['authinfo']['password'],
        'username'      : d['authinfo']['username']
    }
    print params
    encoded_params = urllib.urlencode(params.items())
    print encoded_params
    try:
        req = urllib2.urlopen(d['apiurl'], encoded_params)
        print req.read()
    except urllib2.HTTPError as e:
        try:
            print e.read()
        except AttributeError:
            print e
            raise

registerRAN()