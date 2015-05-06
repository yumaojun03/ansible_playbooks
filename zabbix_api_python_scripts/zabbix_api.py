#!/usr/bin/env python
# coding: utf-8

# coding=utf-8
__author__ = 'chuanxiu'


import json
import urllib2
import argparse


class zabbix(object):
    ''' call zabbix api '''

    def __init__(self,user,passwd,url):
        self.zabbix_user = user
        self.zabbix_pass = passwd
        self.url = url
        self.header = {"Content-Type" : "application/json"}

    def auth(self):
        ''' auth'''
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.zabbix_user,
                    "password": self.zabbix_pass
                },
                "id": 0,
            }
        )

        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])

        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "Auth Failed,Please Check You Name And Password: %s" %(str(e))
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']

    def logout(self,authid):
        '''logout'''
        data = json.dumps(
            {
                "jsonrpc" : "2.0",
                "method" : "user.logout",
                "params" : [],
                "id" : 0,
                "auth" : authid
            }
        )

        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])

        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "Logout Failed: %s" %(str(e))
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']

    def user_lang_update(self, authid, userid, lang):
        ''' get user id form user group'''
        data = json.dumps(
            {
                "jsonrpc" : "2.0",
                "method" : "user.update",
                "params" : {
                    "userid" : userid,
                    "lang" : lang
                },
                "auth" : authid,
                "id" : 7,
            }
        )
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "get user infomation failed: %s" % ( str(e) )
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']

    def get_log_userid(self, authid, ):
        ''' update user lang to chinese'''
        data = json.dumps(
            {
                "jsonrpc" : "2.0",
                "method" : "user.get",
                "params" : {
                    "output" : ["surname", "alias", "userid"],
                },
                "auth" : authid,
                "id" : 7,
            }
        )
        request = urllib2.Request(self.url,data)
        for key in  self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "Update user failed: %s" % (str(e))
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']

    def get_media_type_id(self, authid, ):
        ''' update user lang to chinese'''
        data = json.dumps(
            {
                "jsonrpc" : "2.0",
                "method" : "mediatype.get",
                "params" : {
                    "output" : ["mediatypeid", "description"]
                },
                "auth" : authid,
                "id" : 8,
            }
        )
        request = urllib2.Request(self.url,data)
        for key in  self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "Update user failed: %s" % (str(e))
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']

    def update_media_email(self, authid, emailtypeid, smtp_server, smtp_helo, smtp_email ):
        ''' update user lang to chinese'''
        data = json.dumps(
            {
                "jsonrpc" : "2.0",
                "method" : "mediatype.update",
                "params" : {
                     "mediatypeid" : emailtypeid,
                     "smtp_server" : smtp_server,
                     "smtp_helo" : smtp_helo,
                     "smtp_email" : smtp_email,
                     "status" : 0
                },
                "auth" : authid,
                "id" : 8,
            }
        )
        request = urllib2.Request(self.url,data)
        for key in  self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception,e:
            print "Update user failed: %s" % (str(e))
        else:
            response = json.loads(result.read())
            result.close()
        return response['result']


def update_lang(user, password, url, username, lang):
    zbx = zabbix(user, password, url)
    authid = zbx.auth()
    print "Auth Successful. The Auth ID IS: %s" %(authid)

    for i in  zbx.get_log_userid(authid):
        if i['alias'] == username:
            userid = i['userid']
    print "the %s userid is: %s." % ( username, userid)
    response = zbx.user_lang_update(authid, userid, lang)
    if response['userids']:
        print "success!"
    else:
        print "Failed!"

    print "Logout : %s" %(zbx.logout(authid))

def update_email(user, password, url, smtp_server, smtp_helo, smtp_email):
    zbx = zabbix(user, password, url)
    authid = zbx.auth()
    print "Auth Successful. The Auth ID IS: %s" %(authid)    

    for i in zbx.get_media_type_id(authid):
        if i["description"] == "Email":
            emailtypeid = i["mediatypeid"]
    print "the Email typeid is: %s." % ( emailtypeid )    
    response = zbx.update_media_email(authid, emailtypeid, smtp_server, smtp_helo,smtp_email)
    if response['mediatypeids']:
        print "success!"
    else:
        print "Failed!"

    print "Logout : %s" %(zbx.logout(authid))

    
    
    
def Main():
    paser = argparse.ArgumentParser()
    paser.add_argument('--user')
    paser.add_argument('--password')
    paser.add_argument('--url')
    paser.add_argument('--smtp_server')
    paser.add_argument('--smtp_helo')
    paser.add_argument('--smtp_email')

    args = paser.parse_args()
    user = args.user
    password = args.password
    url = args.url
    smtp_server = args.smtp_server
    smtp_helo = args.smtp_helo
    smtp_email = args.smtp_email
    
    update_lang(user, password, url, 'Admin', 'zh_CN')
    update_email(user, password, url, smtp_server, smtp_helo, smtp_email)
    

Main()
