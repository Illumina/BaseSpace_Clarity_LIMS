#!/usr/bin/env python

import glsapiutil
import platform

api = None

HOSTNAME = platform.node()
VERSION = 'v2'
BASE_URI = HOSTNAME + '/api/' + VERSION + '/'

def setupGlobalsFromURI( uri ):

    global HOSTNAME
    global VERSION
    global BASE_URI

    tokens = uri.split( "/" )
    HOSTNAME = "/".join(tokens[0:3])
    VERSION = tokens[4]
    BASE_URI = "/".join(tokens[0:5]) + "/" 


def main():

    global api

    sample_uri = "https://demosystem/api/v2/steps/24-000000"
    username = 'apiuser'
    password = 'password'
    
    setupGlobalsFromURI( sample_uri )

    api = glsapiutil.glsapiutil2()
    api.setHostname( HOSTNAME )
    api.setVersion( VERSION )
    api.setup( username, password )

    return


if __name__ == '__main__':

    main()
