#!/usr/bin/env python3

# This is version 3 of the glsapiutil library
# to work with the Illumina BaseSpace ClarityLIMS API

# It is now backwards compatible with Python 2.6

from __future__ import absolute_import, division, print_function, unicode_literals

__version__ = '3.0a'

import sys
_py_version_ = sys.version_info
import re
import xml.dom.minidom
import logging


if _py_version_ >= (3,0):
    import urllib.request as py_sys_urllib # partially supersedes Python 2's urllib2
    from urllib.error import HTTPError, URLError
else:
    import urllib2 as py_sys_urllib
    from urllib2 import HTTPError, URLError

from xml.dom.minidom import parseString
from xml.sax.saxutils import escape

DEBUG = 0

class glsapiutil3:
   
    # constructor, takes in a debug value as optional argument
    # if debug is specified then a logger is set up

    def __init__ ( self, debug = 0 ):
        global DEBUG
        DEBUG = debug

        # set up the logger
        if DEBUG > 0:
            root = logging.getLogger() # return the root logger
            root.setLevel( logging.DEBUG )
            
            ch = logging.StreamHandler( sys.stderr ) # write to stderr by default
            ch.setLevel( logging.DEBUG )
            
            logfmtr = logging.Formatter('{0} %(levelname)-2s: %(asctime)s @> %(message)s'.format(self.__module__))
            ch.setFormatter( logfmtr )

            root.addHandler( ch )

        logging.debug( '%s called' % ( sys._getframe().f_code.co_name ) )

        # some internal variables we will need
        self.hostname = ''
        self.auth_handler = ''
        self.version = 'v2'
        self._base_uri = []

    # sets the hostname
    # if a sourceURI is provided in setup()
    # the hostname will be overwritten by what is set here
    def setHostname( self, hostname ):

        logging.debug( 'Setting hostname to "%s"' % (hostname) )
        self.hostname = hostname

    # set the API version
    # this function will not usually need to be called
    # unless we are explicitly setting the version to something
    # other than the default 'v2'
    def setVersion( self, version ):
        
        logging.debug( 'Setting API version to "%s"' % (version) )
        self.version = version

    # get the base URI
    # always call this function instead of accessing
    # self._base_uri directly, as this function will give
    # you a nice string instead of tokens
    def getBaseURI( self ):
        base_uri = '/'.join( self._base_uri )
        base_uri = '{0}/'.format( base_uri )
        
        logging.warn( 'Current Base URI is "%s". If you have called setVersion() or setHostname() after calling setup(), please call setup() again' % ( base_uri ) )

        return base_uri
    
    # set up the API connection with a username and password
    # if a step URI or some other source URI is provided
    # the function will introspect and use the hostname
    # and version from it, overwriting any previous values
    # that are set by setHostname() or setVersion()
    def setup( self, username, password, sourceURI = '' ):

        logging.debug( 'Setting API credentials' )

        if len(sourceURI) > 0: # if we are given a source URI to work with, let's set up with those
            tokens = sourceURI.split('/')
            self.hostname = '/'.join( tokens[0:3] )
            self.version = tokens[4]
            
            logging.debug('You have specified a URI from which I will figure out the hostname. Thanks!')

        if len( self.hostname ) <= 0:
            logging.error( 'Hostname not specified! Please call setHostname() first or specify a sourceURI to setup()' )
            raise ValueError( 'Hostname not specified.' )

        # set the base URI that we will use forever more
        # doing it this way means we can change the hostname or version
        # after calling setup(). The caveat is that setup() needs to be called again
        self._base_uri = [ self.hostname, 'api', self.version ]

        logging.debug( 'Setting base URI to "%s". If this looks different from your normal hostname, don\'t panic!' % ( self.getBaseURI() ) )

        # set up the API authentication and plumbing
        # using the current Base URI
        password_manager = py_sys_urllib.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password( None, self.getBaseURI(), username, password )
        self.auth_handler = py_sys_urllib.HTTPBasicAuthHandler( password_manager )
        opener = py_sys_urllib.build_opener( self.auth_handler )
        py_sys_urllib.install_opener( opener )
    
        logging.debug( 'API object created successfully.' )


    ## FUNCTIONS TO ACCESS REST ENDPOINTS

    def GET( self, uri ):
        
        # default HTTP Request is a GET
        return self._createStandardHTTPRequest( uri )

    # POST wrapper function
    def POST( self, xmlObject, uri ):

        return self._createStandardHTTPRequest( 'POST', uri, xmlObject )
    
    # PUT wrapper function
    def PUT( self, xmlObject, uri ):

        return self._createStandardHTTPRequest( 'PUT', uri, xmlObject )

    # DELETE wrapper function
    def DELETE( self, xmlObject, uri ):

        return self._createStandardHTTPRequest( 'DELETE', uri, xmlObject )



    ## Useful helper functions
    def reportScriptStatus( self, uri, status, message ):

        newuri = uri + "/programstatus"
        message = escape( message )

        thisXML = self.GET( newuri )
        thisDOM = parseString( thisXML )

        sNodes = thisDOM.getElementsByTagName( "status" )
        
        if len( sNodes ) > 0:
            sNodes[0].firstChild.data = status
        
        mNodes = thisDOM.getElementsByTagName( "message" )
        
        if len( mNodes ) > 0:
            mNodes[0].firstChild.data = message
        
        elif len( mNodes ) == 0:
            newDOM = xml.dom.minidom.getDOMImplementation()
            newDoc = newDOM.createDocument( None, None, None )

            # now add the new message node
            txt = newDoc.createTextNode( str( message ) ) 
            newNode = newDoc.createElement( "message" )
            newNode.appendChild( txt )

            thisDOM.childNodes[0].appendChild( newNode )

        try:
            self.PUT( thisDOM.toxml(), newuri )
        
        except:
            logging.error( message )  
    

    ## internal functions
    
    # create a HTTP request for POSTs and PUTs
    # with the standard API and sends the message.
    # returns the message received from the server
    def _createStandardHTTPRequest( self, uri, http_method_type = 'GET', xmlObject = None ):

        logging.debug( 'Creating a request of type %s' % (http_method_type, ) )
        
        opener = py_sys_urllib.build_opener( self.auth_handler )

        req = py_sys_urllib.Request( uri )

        if xmlObject is not None:
            req.add_data( xmlObject )
        
        req.get_method = lambda: http_method_type
        req.add_header( 'Accept', 'application/xml' )
        req.add_header( 'Content-Type', 'application/xml' )
        req.add_header( 'User-Agent', 'Python-urllib-glsapiutil/3.5' ) # custom user agent

        responseText = ''

        try:

            response = opener.open( req )
            responseText = response.read()

        except HTTPError as e:
            responseText = e.read()

        except URLError as e:
            if e.strerror is not None:
                responseText = e.strerror

            elif e.reason is not None:
                responseText = e.reason
            else:
                responseText = e.message


        except:
            responseText = '%s %s' % ( str(sys.exc_type), str(sys.exc_value) )

        return responseText
