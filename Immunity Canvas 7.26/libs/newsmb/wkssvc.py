#!/usr/bin/env python
##ImmunityHeader v1
###############################################################################
## File       :  wkssvc.py
## Description:
##            :
## Created_On :  Mon Aug  3 CEST 2015
## Created_By :  X.
##
## (c) Copyright 2010, Immunity, Inc. all rights reserved.
###############################################################################

# The API is not 100% written but is currently working quite well.
# Implemented from Wireshark && [MS-WKST].pdf

# Confirmed working on:
#    Windows 2003
#    Windows 2008 R2
#    Windows 7
#    Windows 2012

import sys
import logging
from struct import pack, unpack

if '.' not in sys.path:
    sys.path.append('.')

from libs.newsmb.libdcerpc import DCERPC, DCERPCString, DCERPCSid
from libs.newsmb.libdcerpc import RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_INTEGRITY
from libs.newsmb.Struct import Struct

###
# Constants
###

# The RPC methods

WKSSVC_COM_GET_INFO = 0
WKSSVC_COM_SET_INFO = 1
WKSSVC_COM_ENUM_USERS = 2
WKSSVC_COM_USER_GET_INFO = 3
WKSSVC_COM_USER_SET_INFO = 4

# Required by the _WKSTA_USER_ENUM_UNION

WKSTA_USER_INFO_0 = 0
WKSTA_USER_INFO_1 = 1

###
# WKSSVC Objects.
# No exception handling for these objects.
###

class ResumeHandle(Struct):
    st = [
        ['RefId', '<L', 0x2006],
        ['Pointer', '<L', 0],
    ]

    def __init__(self, data=None, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)

    def pack(self):
        data = Struct.pack(self)
        return data

class WkstaUserInfoLevel0(Struct):
    st = [
        ['RefID', '<L', 0x2005 ],
        ['MaxCount', '<L', 0 ],
        ['UsernameArray', '0s', '' ]
    ]

    def __init__(self, data=None, UsernameArray=[]):
        Struct.__init__(self, data)
        self.usernames = []

        if data is not None:
            Struct.__init__(self, data)
            pos = self.calcsize()
            for i in xrange(self['MaxCount']):
                refptr = unpack('<L', data[pos:pos+4])[0]
                pos += 4
            for i in xrange(self['MaxCount']):
                s = DCERPCString(data=data[pos:])
                self.usernames.append(s.get_string().decode('UTF-16LE').encode('ascii')[:-1])
                pos += len(s.pack())
            self['UsernameArray'] = ''.join(UsernameArray)
        else:
            self.usernames = UsernameArray
            self['MaxCount'] = len(self.usernames)
            self['UsernameArray'] = ''.join(UsernameArray)

    def pack(self):

        data =Struct.pack(self)
        for i in xrange(self['MaxCount']):
            data += pack('<L', 0x20010+i*4)
        if self['MaxCount']:
            data += ''.join(self.usernames)
        return data

    def get_usernames(self):
        return self.usernames

class WkstaUserInfoLevel0Array(Struct):
    st = [
        ['Ctr', '<L', 0 ],
        ['RefPtr', '<L', 0x2004 ],
        ['EntriesRead', '<L', 0 ],
        ['UserInfo', '0s', '' ],
    ]

    def __init__(self, data=None, EntriesRead=0):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
            pos = self.calcsize()
            self['UserInfo'] = WkstaUserInfoLevel0(data=data[pos:])
            ### TODO
        else:
            self['EntriesRead'] = 0 # Let's avoid EntriesRead for now.
            self['UserInfo'] = WkstaUserInfoLevel0()

    def pack(self, pack_header=1, pack_string=0, force_null_byte=1):

        data  = pack('<L', self['Ctr'])
        data += pack('<L', self['RefPtr'])
        data += pack('<L', self['EntriesRead'])
        data += self['UserInfo'].pack()
        return data

    def get_usernames(self):
        return self['UserInfo'].get_usernames()

class WkstaUserInfo(Struct):
    st = [
        ['Level', '<L', 0 ],
        ['UserInfo', '0s', '' ],
    ]

    def __init__(self, data=None, Level=WKSTA_USER_INFO_0, EntriesRead=0):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
            self['UserInfo'] = WkstaUserInfoLevel0Array(data=data[4:])
        else:
            self['Level'] = Level
            self['UserInfo'] = WkstaUserInfoLevel0Array(EntriesRead=EntriesRead)

    def pack(self, pack_header=1, pack_string=0, force_null_byte=1):

        data = pack('<L', self['Level'])
        data += self['UserInfo'].pack()
        return data

    def get_usernames(self):
        return self['UserInfo'].get_usernames()


###
# Handlers
# No exception handling for these objects.
###

# Opnum 2

'''
unsigned long NetrWkstaUserEnum(
 [in, string, unique] WKSSVC_IDENTIFY_HANDLE ServerName,
 [in, out] LPWKSTA_USER_ENUM_STRUCT UserInfo,
 [in] unsigned long PreferredMaximumLength,
 [out] unsigned long* TotalEntries,
 [in, out, unique] unsigned long* ResumeHandle
);
'''

class NetrWkstaUserEnumRequest(Struct):
    st = [
        ['ServerName', '0s', ''],
        ['UserInfo', '0s', ''],
        ['PrefMaxLen', '<L', 60000],
        ['ResumeHandle', '0s', ''],
    ]

    def __init__(self, data=None, ServerName='', is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
            ### TODO
        else:
            if len(ServerName):
                self['ServerName'] = ServerName.encode('UTF-16LE')
            self['UserInfo'] = WkstaUserInfo()
            self['ResumeHandle'] = ResumeHandle()

    def pack(self):

        if len(self['ServerName']):
            data = pack('<L', 0x20004)
            data += DCERPCString(string = self['ServerName']).pack()
        else:
            data = pack('<L', 0) # Null Ptr

        data += self['UserInfo'].pack()
        data += pack('<L', self['PrefMaxLen'])
        data += self['ResumeHandle'].pack()
        return data


class NetrWkstaUserEnumResponse(Struct):
    st = [
        ['UserInfo', '0s', ''],
        ['EntriesRead', '<L', 0],
        ['ResumeHandle', '0s', ''],
    ]

    def __init__(self, data=None, UserInfo=None, EntriesRead=0, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
            pos = 0
            self['UserInfo'] = WkstaUserInfo(data=data[pos:])
            pos += len(self['UserInfo'].pack())
            self['EntriesRead'] = unpack('<L', data[pos:pos+4])[0]
            pos += 4
            self['ResumeHandle'] = ResumeHandle(data=data[pos:]).pack()
        else:
            self['UserInfo'] = WkstaUserInfo()
            self['EntriesRead'] = EntriesRead
            self['ResumeHandle'] = ResumeHandle()

    def pack(self):
        data = ''
        return data

    def get_usernames(self):
        return self['UserInfo'].get_usernames()

    def get_nbr_entries(self):
        return self['EntriesRead']


#######################################################################
#####
##### Exception classes
#####
#######################################################################

class WKSSVCException(Exception):
    """
    Base class for all WKSSVC-specific exceptions.
    """
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return '[ WKSSVC_ERROR: %s ]' % (self.message)

class WKSSVCException2(Exception):
    """
    Improved version of the base class to track errors.
    """
    def __init__(self, message='', status=None):
        self.message = message
        self.status = status

    def __str__(self):
        if not self.status:
            return '[ WKSSVC_ERROR: %s ]' % (self.message)
        else:
            return '[ WKSSVC_ERROR: %s (0x%x) ]' % (self.message, self.status)

class WKSSVCUserEnumException(WKSSVCException2):
    """
    Raised when open fails.
    """
    pass

class WKSSVCUserEnumAccessDeniedException(WKSSVCUserEnumException):
    """
    Raised when credentials are incorrect / or not enough.
    """
    def __init__(self):
        self.message = 'NetrWkstaUserEnumResponse() failed: Access Denied.'
        self.status = 5

#######################################################################
#####
##### Main classes: WKSSVC, WKSSVCClient (WKSSVCServer will not be implemented)
##### API will raise specific exceptions when errors are caught.
#######################################################################

class WKSSVC():
    def __init__(self, host, port):
        self.host              = host
        self.port              = port
        self.is_unicode        = True
        self.policy_handle     = None
        self.uuid              = (u'6bffd098-a112-3610-9833-46c3f87e345a', u'1.0')

class WKSSVCClient(WKSSVC):

    def __init__(self, host, port=445):
        WKSSVC.__init__(self, host, port)
        self.username = None
        self.password = None
        self.domain = None
        self.kerberos_db = None
        self.use_krb5 = False

    def set_credentials(self, username=None, password=None, domain=None, kerberos_db=None, use_krb5=False):
        if username:
            self.username = username
        if password:
            self.password = password
        if domain:
            self.domain = domain
        if kerberos_db:
            self.kerberos_db = kerberos_db
            self.use_krb5 = True
        else:
            if use_krb5:
                self.use_krb5 = use_krb5

    def __bind_krb5(self, connector):

        try:
            self.dce = DCERPC(connector,
                              getsock=None,
                              username=self.username,
                              password=self.password,
                              domain=self.domain,
                              kerberos_db=self.kerberos_db,
                              use_krb5=True)

            return self.dce.bind(self.uuid[0], self.uuid[1], RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_INTEGRITY)
        except Exception as e:
            return 0

    def __bind_ntlm(self, connector):

        try:
            self.dce = DCERPC(connector,
                              getsock=None,
                              username=self.username,
                              password=self.password,
                              domain=self.domain)

            return self.dce.bind(self.uuid[0], self.uuid[1], RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_INTEGRITY)
        except Exception as e:
            return 0

    def __bind(self, connector):

        if self.use_krb5:
            ret = self.__bind_krb5(connector)
            if not ret:
                return self.__bind_ntlm(connector)
        else:
            ret = self.__bind_ntlm(connector)
            if not ret:
                return self.__bind_krb5(connector)
        return 1


    def bind(self):
        """
        Perform a binding with the server.
        0 is returned on failure.
        """

        connectionlist = []
        connectionlist.append(u'ncacn_np:%s[\\browser]' % self.host)
        connectionlist.append(u'ncacn_np:%s[\\wkssvc]' % self.host)
        connectionlist.append(u'ncacn_ip_tcp:%s[%d]' % (self.host,self.port))
        connectionlist.append(u'ncacn_tcp:%s[%d]' % (self.host,self.port))

        for connector in connectionlist:
            ret = self.__bind(connector)
            if ret:
                return 1

        return 0


    def get_reply(self):
        return self.dce.reassembled_data

    def enum_users(self):
        """
        Fetches the list of connected users on the system
        WKSSVCUserEnumException is raised on failure
        """

        try:
            data = NetrWkstaUserEnumRequest(ServerName='').pack()
        except Exception as e:
            raise WKSSVCUserEnumException('enum_users() failed to build the request.')

        self.dce.call(WKSSVC_COM_ENUM_USERS, data, response=True)
        if len(self.get_reply()) < 4:
            raise WKSSVCUserEnumException('NetrWkstaUserEnum() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]
        if status == 0:
            try:
                resp = NetrWkstaUserEnumResponse(self.get_reply())
                return resp.get_usernames()
            except Exception as e:
                raise WKSSVCUserEnumException('NetrWkstaUserEnum() failed: Parsing error in the answer.')
        if status == 5:
            raise WKSSVCUserEnumAccessDeniedException()
        else:
            raise WKSSVCUserEnumException('NetrWkstaUserEnumResponse() failed.', status=status)


#######################################################################
#####
##### A couple of useful functions for other parts of CANVAS
#####
#######################################################################

def wkssvc_enum_user(target_ip, username=None, password=None, domain=None, kerberos_db=None):
    try:
        wsvc = WKSSVCClient(target_ip)
        wsvc.set_credentials(username, password, domain, kerberos_db)
        if not wsvc.bind():
            return -1, None
        names = wsvc.enum_users()
        return 0, names
    except WKSSVCUserEnumAccessDeniedException as e:
        return -e.status, None
    except Exception as e:
        return -1, None

#######################################################################
#####
##### Well, the main :D
#####
#######################################################################

TARGET_IP = '10.0.0.1'
USERNAME = 'administrator'
PASSWORD = 'foobar123!'
DOMAIN = 'immu5.lab'

def call_every_op():

    wsvc = WKSSVCClient(TARGET_IP)
    wsvc.set_credentials(USERNAME, PASSWORD, DOMAIN)

    if not wsvc.bind():
        print "[-] bind() failed."
        sys.exit(0)

    for op in xrange(256):
        wsvc.dce.call(op, "A"*200, response=True)

def main():

    names = wkssvc_enum_user(TARGET_IP, USERNAME, PASSWORD, DOMAIN)
    print names

if __name__ == "__main__":
    main()
