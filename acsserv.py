import yaml
import json
import os
import urllib2, urllib
from pwd import getpwnam
from collections import namedtuple
from collections import namedtuple


class ACSReply():

    dirpath = "51"
    dirpath1 ="1"
    def __init__(self):
        self.one()


    def one(self):
        a=1
        b=11
        if a == b :
            self.tre()
        else:
            print "10"

    def two(self):
        self.val = "3"
    def tre(self):
        self.val = "5"


if __name__ == "__main__":
    y = ACSReply()


#
# x=namedtuple('authinfo', 'username type password realm')
#
#
# namedtuple('ipv4', 'gw addr nameserver')
#
#
#
# bob = x(name='Bdob', age=30, gender='male')
# print bob