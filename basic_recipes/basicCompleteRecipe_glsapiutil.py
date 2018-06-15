#!/usr/bin/env python
import glsapiutil
import platform
import argparse
import logging
from xml.dom.minidom import parseString

api = None
args = None

# seed default values
HOSTNAME = platform.node()
VERSION = 'v2'
BASE_URI = HOSTNAME + '/api/' + VERSION + '/'

# command line argument setup using argparse
def setupArguments():

    aParser = argparse.ArgumentParser("Assigns reaction conditions to samples based on sample UDFs.")
    
    aParser.add_argument('-u', action='store', dest='username', required=True)
    aParser.add_argument('-p', action='store', dest='password', required=True)
    aParser.add_argument('-s', action='store', dest='stepURI', required=True)
    
    # log file 
    aParser.add_argument( '-g', action='store', dest='logfileName' )
    
    return aParser.parse_args()

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
    global args

    args = setupArguments()

    setupGlobalsFromURI( args.stepURI )

    # set up the logger
    logging.basicConfig( filename = args.logfileName, level = logging.DEBUG, format = '%(asctime)s %(message)s' )

    api = glsapiutil.glsapiutil2()
    api.setHostname( HOSTNAME )
    api.setVersion( VERSION )
    api.setup( args.username, args.password )

    logging.debug( "API initialised" )

    return


if __name__ == '__main__':

    main()

