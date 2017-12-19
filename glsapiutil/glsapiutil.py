import urllib2
import re
import sys
import xml.dom.minidom

from xml.dom.minidom import parseString
from optparse import OptionParser
from xml.sax.saxutils import escape

DEBUG = 0

class glsapiutil2:

	## Housekeeping methods

	def __init__( self ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.hostname = ""
		self.auth_handler = None
		self.version = "v2"
		self.uri = ""
		self.base_uri = ""
		self.pythonVersion = sys.version.split( " " )[0]

	def setHostname( self, hostname ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.hostname = hostname

	def setVersion( self, version ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.version = version

	def setURI( self, uri ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.uri = uri

	def getBaseURI( self ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		return self.base_uri

	def getHostname( self ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		return self.hostname

	def setup( self, user, password ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		if len(self.uri) > 0:
			tokens = self.uri.split( "/" )
			self.hostname = "/".join(tokens[0:3])
			self.version = tokens[4]
			self.base_uri = "/".join(tokens[0:5]) + "/"
		else:
			self.base_uri = self.hostname + '/api/' + self.version + '/'

		## setup up API plumbing
		password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_manager.add_password( None, self.base_uri, user, password )
		self.auth_handler = urllib2.HTTPBasicAuthHandler( password_manager )
		opener = urllib2.build_opener( self.auth_handler )
		urllib2.install_opener( opener )

	## REST Methods

	def GET( self, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		responseText = ""
		thisXML = ""

		try:
			thisXML = urllib2.urlopen( url ).read()
		except urllib2.HTTPError, e:
			responseText = e.msg
		except urllib2.URLError, e:
			if e.strerror is not None:
				responseText = e.strerror
			elif e.reason is not None:
				responseText = str( e.reason )
			else:
				responseText = e.message
		except:
			responseText = str(sys.exc_type) + str(sys.exc_value)

		if len(responseText) > 0:
			print( "Error trying to access " + url )
			print( responseText )

		return thisXML

	def PUT( self, xmlObject, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		opener = urllib2.build_opener(self.auth_handler)

		req = urllib2.Request(url)
		req.add_data( xmlObject )
		req.get_method = lambda: 'PUT'
		req.add_header('Accept', 'application/xml')
		req.add_header('Content-Type', 'application/xml')
		req.add_header('User-Agent', 'Python-urllib2/%s' % self.pythonVersion )

		try:
			response = opener.open( req )
			responseText = response.read()
		except urllib2.HTTPError, e:
			responseText = e.msg
		except urllib2.URLError, e:
			if e.strerror is not None:
				responseText = e.strerror
			elif e.reason is not None:
				responseText = str( e.reason )
			else:
				responseText = e.message
		except:
			responseText = str(sys.exc_type) + " " + str(sys.exc_value)

		return responseText

	def POST( self, xmlObject, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		opener = urllib2.build_opener(self.auth_handler)

		req = urllib2.Request(url)
		req.add_data( xmlObject )
		req.get_method = lambda: 'POST'
		req.add_header('Accept', 'application/xml')
		req.add_header('Content-Type', 'application/xml')
		req.add_header('User-Agent', 'Python-urllib2/%s' % self.pythonVersion )

		try:
			response = opener.open( req )
			responseText = response.read()
		except urllib2.HTTPError, e:
			responseText = e.read()
		except urllib2.URLError, e:
			if e.strerror is not None:
				responseText = e.strerror
			elif e.reason is not None:
				responseText = str( e.reason )
			else:
				responseText = e.message
		except:
			responseText = str(sys.exc_type) + " " + str(sys.exc_value)

		return responseText

	## API Helper methods

	@staticmethod
	def getUDF( DOM, udfname ):

		response = ""

		elements = DOM.getElementsByTagName( "udf:field" )
		for udf in elements:
			temp = udf.getAttribute( "name" )
			if temp == udfname:
				response = udf.firstChild.data
				break

		return response

	@staticmethod
	def setUDF( DOM, udfname, udfvalue ):

		if DEBUG > 2: print( DOM.toprettyxml() )

		## are we dealing with batch, or non-batch DOMs?
		if DOM.parentNode is None:
			isBatch = False
		else:
			isBatch = True

		newDOM = xml.dom.minidom.getDOMImplementation()
		newDoc = newDOM.createDocument( None, None, None )

		## if the node already exists, delete it
		elements = DOM.getElementsByTagName( "udf:field" )
		for element in elements:
			if element.getAttribute( "name" ) == udfname:
				try:
					if isBatch:
						DOM.removeChild( element )
					else:
						DOM.childNodes[0].removeChild( element )
				except xml.dom.NotFoundErr, e:
					if DEBUG > 0: print( "Unable to Remove existing UDF node" )

				break

		# now add the new UDF node
		txt = newDoc.createTextNode( str( udfvalue ) )
		newNode = newDoc.createElement( "udf:field" )
		newNode.setAttribute( "name", udfname )
		newNode.appendChild( txt )

		if isBatch:
			DOM.appendChild( newNode )
		else:
			DOM.childNodes[0].appendChild( newNode )

		return DOM

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
			print message

	def getArtifacts( self, LUIDs ):

		"""
		This function will be passed a list of artifacts LUIDS, and return those artifacts represented as XML
		The artifacts will be collected in a single batch transaction, and the function will return the XML
		for the entire transactional list
		"""

		response = self.__getBatchObjects( LUIDs, "artifact" )
		if response is None:
			return ""
		else:
			return response

	def getContainers( self, LUIDs ):

		"""
		This function will be passed a list of container LUIDS, and return those containers represented as XML
		The containers will be collected in a single batch transaction, and the function will return the XML
		for the entire transactional list
		"""

		response = self.__getBatchObjects( LUIDs, "container" )
		if response is None:
			return ""
		else:
			return response

	def getSamples( self, LUIDs ):

		"""
		This function will be passed a list of sample LUIDS, and return those sample represented as XML
		The samples will be collected in a single batch transaction, and the function will return the XML
		for the entire transactional list
		"""

		response = self.__getBatchObjects( LUIDs, "sample" )
		if response is None:
			return ""
		else:
			return response

	def getFiles( self, LUIDs ):

		"""
		This function will be passed a list of file LUIDS, and return those sample represented as XML
		The samples will be collected in a single batch transaction, and the function will return the XML
		for the entire transactional list
		"""

		response = self.__getBatchObjects( LUIDs, "file" )
		if response is None:
			return ""
		else:
			return response

	def __getBatchObjects( self, LUIDs, objectType ):

		if objectType == "artifact":
			batchNoun = "artifacts"
			nodeNoun = "art:artifact"
		elif objectType == "sample":
			batchNoun = "samples"
			nodeNoun = "smp:sample"
		elif objectType == "container":
			batchNoun = "containers"
			nodeNoun = "con:container"
		elif objectType == "file":
			batchNoun = "files"
			nodeNoun = "file:file"
		else:
			return None

		lXML = []
		lXML.append( '<ri:links xmlns:ri="http://genologics.com/ri">' )
		for limsid in set(LUIDs):
			lXML.append( '<link uri="%s%s/%s"/>' % ( self.getBaseURI(), batchNoun, limsid ) )
		lXML.append( '</ri:links>' )
		lXML = ''.join( lXML )

		mXML = self.POST( lXML, "%s%s/batch/retrieve" % ( self.getBaseURI(), batchNoun ) )

		## did we get back anything useful?
		try:
			mDOM = parseString( mXML )
			nodes = mDOM.getElementsByTagName( nodeNoun )
			if len(nodes) > 0:
				response = mXML
			else:
				response = ""
		except:
			response = ""

		return response


        def deleteObject( self, xmlObject, url):
            
                opener = urllib2.build_opener(self.auth_handler)
            
                req = urllib2.Request(url)
                req.add_data( xmlObject )
                req.get_method = lambda: 'DELETE'
                req.add_header('Accept', 'application/xml')
                req.add_header('Content-Type', 'application/xml')
                req.add_header('User-Agent', 'Python-urllib2/2.4')
            
                responseText = "EMPTY"
            
                try:
                    response = opener.open( req )
                    responseText = response.read()
                except urllib2.HTTPError, e:
                    responseText = e.read()
                except:
                    responseText = str(sys.exc_type) + " " + str(sys.exc_value)
            
                return responseText


class glsapiutil:

	## Housekeeping methods

	def __init__( self ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.hostname = ""
		self.auth_handler = ""
		self.version = "v1"

	def setHostname( self, hostname ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.hostname = hostname

	def setVersion( self, version ):
		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )
		self.version = version

	def setup( self, user, password ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		## setup up API plumbing
		password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_manager.add_password( None, self.hostname + '/api/' + self.version, user, password )
		self.auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
		opener = urllib2.build_opener(self.auth_handler)
		urllib2.install_opener(opener)

	## REST methods


        def deleteObject( self, xmlObject, url):
            
                opener = urllib2.build_opener(self.auth_handler)
            
                req = urllib2.Request(url)
                req.add_data( xmlObject )
                req.get_method = lambda: 'DELETE'
                req.add_header('Accept', 'application/xml')
                req.add_header('Content-Type', 'application/xml')
                req.add_header('User-Agent', 'Python-urllib2/2.4')
            
                responseText = "EMPTY"
            
                try:
                    response = opener.open( req )
                    responseText = response.read()
                except urllib2.HTTPError, e:
                    responseText = e.read()
                except:
                    responseText = str(sys.exc_type) + " " + str(sys.exc_value)
            
                return responseText

	def createObject( self, xmlObject, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		opener = urllib2.build_opener(self.auth_handler)

		req = urllib2.Request(url)
		req.add_data( xmlObject )
		req.get_method = lambda: 'POST'
		req.add_header('Accept', 'application/xml')
		req.add_header('Content-Type', 'application/xml')
		req.add_header('User-Agent', 'Python-urllib2/2.6')

		try:
			response = opener.open( req )
			responseText = response.read()
		except urllib2.HTTPError, e:
			responseText = e.read()
		except:
			responseText = str(sys.exc_type) + " " + str(sys.exc_value)

		return responseText

	def updateObject( self, xmlObject, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		opener = urllib2.build_opener(self.auth_handler)

		req = urllib2.Request(url)
		req.add_data( xmlObject )
		req.get_method = lambda: 'PUT'
		req.add_header('Accept', 'application/xml')
		req.add_header('Content-Type', 'application/xml')
		req.add_header('User-Agent', 'Python-urllib2/2.6')

		try:
			response = opener.open( req )
			responseText = response.read()
		except urllib2.HTTPError, e:
			responseText = e.read()
		except:
			responseText = str(sys.exc_type) + " " + str(sys.exc_value)

		return responseText

	def getResourceByURI( self, url ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		responseText = ""
		xml = ""

		try:
			xml = urllib2.urlopen( url ).read()
		except urllib2.HTTPError, e:
			responseText = e.msg
		except urllib2.URLError, e:
			if e.strerror is not None:
				responseText = e.strerror
			elif e.reason is not None:
				responseText = str( e.reason )
			else:
				responseText = e.message
		except:
			responseText = str(sys.exc_type) + str(sys.exc_value)

		if len(responseText) > 0:
			print( "Error trying to access " + url )
			print( responseText )

		return xml

	def getBatchResourceByURI( self, url, links ):

		if DEBUG > 0: print( "%s:%s called" % ( self.__module__, sys._getframe().f_code.co_name ) )

		opener = urllib2.build_opener(self.auth_handler)

		req = urllib2.Request(url)
		req.add_data( links )
		req.get_method = lambda: 'POST'
		req.add_header('Accept', 'application/xml')
		req.add_header('Content-Type', 'application/xml')
		req.add_header('User-Agent', 'Python-urllib2/2.6')

		try:
			response = opener.open( req )
			responseText = response.read()
		except urllib2.HTTPError, e:
			responseText = e.read()
		except:
			responseText = str(sys.exc_type) + " " + str(sys.exc_value)

		return responseText

	## Helper methods

	@staticmethod
	def getUDF( DOM, udfname ):

		response = ""

		elements = DOM.getElementsByTagName( "udf:field" )
		for udf in elements:
			temp = udf.getAttribute( "name" )
			if temp == udfname:
				response = udf.firstChild.data
				break

		return response

	@staticmethod
	def setUDF( DOM, udfname, udfvalue ):

		if DEBUG > 2: print( DOM.toprettyxml() )

		## are we dealing with batch, or non-batch DOMs?
		if DOM.parentNode is None:
			isBatch = False
		else:
			isBatch = True

		newDOM = xml.dom.minidom.getDOMImplementation()
		newDoc = newDOM.createDocument( None, None, None )

		## if the node already exists, delete it
		elements = DOM.getElementsByTagName( "udf:field" )
		for element in elements:
			if element.getAttribute( "name" ) == udfname:
				try:
					if isBatch:
						DOM.removeChild( element )
					else:
						DOM.childNodes[0].removeChild( element )
				except xml.dom.NotFoundErr, e:
					if DEBUG > 0: print( "Unable to Remove existing UDF node" )

				break

		# now add the new UDF node
		txt = newDoc.createTextNode( str( udfvalue ) )
		newNode = newDoc.createElement( "udf:field" )
		newNode.setAttribute( "name", udfname )
		newNode.appendChild( txt )

		if isBatch:
			DOM.appendChild( newNode )
		else:
			DOM.childNodes[0].appendChild( newNode )

		return DOM

	def getParentProcessURIs( self, pURI ):

		response = []

		pXML = self.getResourceByURI( pURI )
		pDOM = parseString( pXML )
		elements = pDOM.getElementsByTagName( "input" )
		for element in elements:
			ppNode = element.getElementsByTagName( "parent-process" )
			ppURI = ppNode[0].getAttribute( "uri" )

			if ppURI not in response:
				response.append( ppURI )

		return response

	def getDaughterProcessURIs( self, pURI ):

		response = []
		outputs = []

		pXML = self.getResourceByURI( pURI )
		pDOM = parseString( pXML )
		elements = pDOM.getElementsByTagName( "output" )
		for element in elements:
			limsid = element.getAttribute( "limsid" )
			if limsid not in outputs:
				outputs.append( limsid )

		## now get the processes run on each output limsid
		for limsid in outputs:
			uri = self.hostname + "/api/" + self.version + "/processes?inputartifactlimsid=" + limsid
			pXML = self.getResourceByURI( uri )
			pDOM = parseString( pXML )
			elements = pDOM.getElementsByTagName( "process" )
			for element in elements:
				dURI = element.getAttribute( "uri" )
				if dURI not in response:
					response.append( dURI )

		return response

	def reportScriptStatus( self, uri, status, message ):

		newuri = uri + "/programstatus"
		message = escape( message )

		thisXML = self.getResourceByURI( newuri )
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
			self.updateObject( thisDOM.toxml(), newuri )
		except:
			print message

	@staticmethod
	def removeState( xml ):

		return re.sub( "(.*)(\?state=[0-9]*)(.*)", "\\1" + "\\3", xml )

	@staticmethod
	def getInnerXml( xml, tag ):
		tagname = '<' + tag + '.*?>'
		inXml = re.sub( tagname, '', xml )

		tagname = '</' + tag + '>'
		inXml = inXml.replace( tagname, '' )

		return inXml

################################################
## THESE CLASSES RELY UPON THE glsapiutil2 CLASS
################################################

class stepOutput:

	def __init__(self):
		self.__inputLUID = ""
		self.__LUID = ""
		self.__type = ""
		self.__isShared = False
		self.__props = {}
		pass

	def setInputLUID(self, value): self.__inputLUID = value
	def getInputLUID(self): return self.__inputLUID

	def setOutputLUID(self, value): self.__LUID = value
	def getOutputLUID(self): return self.__LUID

	def setOutputType(self, value): self.__type = value
	def getOutputType(self): return self.__type

	def setIsShared(self, value): self.__isShared = value
	def getIsShared(self): return self.__isShared

	def setProperty(self, propName, propValue): self.__props[ propName ] = propValue
	def getProperty(self, propName):
		if propName in self.__props.keys():
			return self.__props[ propName ]
		else:
			return ""

	def toString(self):
		txt = "Input:" + self.__inputLUID
		txt += " Output:" + self.__LUID
		txt += " Type:" + self.__type
		txt += " Shared:" + str(self.__isShared)

		for k in self.__props.keys():
			txt += " " + k + ":" + str(self.__props[ k ])

		return txt

class IOMapper:

	def __init__( self ):
		self.__stepURI = ""
		self.__IOMaps = []
		self.__detailsDOM = None
		self.__APIHandler = None

	def setStepURI( self, value ): self.__stepURI = value
	def setAPIHandler(self, object ): self.__APIHandler = object

	def getIOMaps( self, outputType="", shared=False ):
		if len(self.__stepURI) > 0:
			## do we already have a populated DOM? If not, fetch the XML we require
			if self.__detailsDOM is None:
				detailsURI = self.__stepURI + "/details"
				detailsXML = self.__APIHandler.GET( detailsURI )
				self.__detailsDOM = parseString( detailsXML )

				IOMaps = self.__detailsDOM.getElementsByTagName( "input-output-map" )
				for IOMap in IOMaps:
					tmp = stepOutput()
					nodes = IOMap.getElementsByTagName( "input" )
					iLUID = nodes[0].getAttribute( "limsid" )
					tmp.setInputLUID( iLUID )
					nodes = IOMap.getElementsByTagName( "output" )
					## does the step even produce outputs? Maybe not
					if len(nodes) > 0:
						tmp.setOutputLUID( nodes[0].getAttribute( "limsid" ) )
						tmp.setOutputType( nodes[0].getAttribute( "type" ) )
						## set the output-generation-type
						ogType = nodes[0].getAttribute( "output-generation-type" )
						if ogType == "PerInput" or ogType == "PerReagent":
							tmp.setIsShared( False )
						else:
							tmp.setIsShared( True )

					## do we want this as part of our collection?
					if shared is True:
						if len(outputType) == 0:
							self.__IOMaps.append( tmp )
						elif outputType == tmp.getOutputType():
							self.__IOMaps.append( tmp )
					elif shared is False and tmp.getIsShared() is False:
						if len(outputType) == 0:
							self.__IOMaps.append( tmp )
						elif outputType == tmp.getOutputType():
							self.__IOMaps.append( tmp )

		return self.__IOMaps

class stepHelper:

	def __init__( self ):
		self.__stepURI = ""
		self.IOMaps = None
		self.__APIHandler = None
		self.__placementsDOM = None
		self.__processDOM = None
		self.__poolingDOM = None
		self.__reagentsDOM = None
		pass

	def setStepURI( self, value ): self.__stepURI = value
	def setAPIHandler(self, object ): self.__APIHandler = object

	def getIOMaps( self, outputType="", shared=False ):
		if self.IOMaps is None:
			self.IOMaps = IOMapper()
			self.IOMaps.setStepURI( self.__stepURI )
			self.IOMaps.setAPIHandler( self.__APIHandler )
		IOMaps = self.IOMaps.getIOMaps( outputType, shared )

		return IOMaps

	def getUniqueInputLUIDs( self, shared=False ):
		iLUIDS = []
		for IOMap in self.getIOMaps( shared=shared ):
			iLUID = IOMap.getInputLUID()
			if iLUID not in iLUIDS:
				iLUIDS.append( iLUID )
		return iLUIDS

	def getSelectedContainers( self ):

		scLUIDs = []

		if len(self.__stepURI) > 0 and self.__placementsDOM is None:
			placementsURI = self.__stepURI + "/placements"
			placementsXML = self.__APIHandler.GET( placementsURI )
			self.__placementsDOM = parseString( placementsXML )

		nodes = self.__placementsDOM.getElementsByTagName( "selected-containers" )
		scNodes = nodes[0].getElementsByTagName( "container")
		for sc in scNodes:
			scURI = sc.getAttribute( "uri")
			scLUID = scURI.split( "/" )[-1]

			scLUIDs.append( scLUID )

		return scLUIDs

	def getProcessDOM( self ):

		if self.__processDOM is None:
			pURI = self.__stepURI.replace( "steps", "processes" )
			detailsXML = self.__APIHandler.GET( pURI )
			self.__processDOM = parseString( detailsXML )

		return self.__processDOM

	def getPoolingDOM( self ):

		if self.__poolingDOM is None:
			pURI = self.__stepURI + "/pools"
			pXML = self.__APIHandler.GET( pURI )
			self.__poolingDOM = parseString( pXML )

		return self.__poolingDOM

	def getPlacementsDOM( self ):

		if len(self.__stepURI) > 0 and self.__placementsDOM is None:
			placementsURI = self.__stepURI + "/placements"
			placementsXML = self.__APIHandler.GET( placementsURI )
			self.__placementsDOM = parseString( placementsXML )

		return self.__placementsDOM

	def getReagentsDOM( self ):

		if len(self.__stepURI) > 0 and self.__reagentsDOM is None:
			thisURI = self.__stepURI + "/reagents"
			thisXML = self.__APIHandler.GET( thisURI )
			self.__placementsDOM = parseString( thisXML )

		return self.__placementsDOM

	def getStepConfiguration( self ):

		response = ""

		if len( self.__stepURI ) > 0:
			stepXML = self.__APIHandler.GET( self.__stepURI )
			stepDOM = parseString( stepXML )
			nodes = stepDOM.getElementsByTagName( "configuration" )
			if len(nodes) > 0:
				response = nodes[0].toxml()

		return response

################################################
## Test Code
################################################

def main():

	global api
	global options

	parser = OptionParser()
	parser.add_option( "-u", "--username", action = "store", dest = "username", type = "string", help = "username of the current user" )
	parser.add_option( "-p", "--password", action = "store", dest = "password", type = "string", help = "password of the current user" )
	parser.add_option( "-s", "--stepURI", action = "store", dest = "stepURI", type = "string", help = "the URI of the step that launched this script" )

	(options, otherArgs) = parser.parse_args()

	api = glsapiutil2()
	api.setURI( options.stepURI )
	api.setup( options.username, options.password )

	## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
	## so let's get this show on the road!
	pXML = api.GET( api.getBaseURI() + "projects" )
	pDOM = parseString( pXML )
	pURI = pDOM.getElementsByTagName( "project" )[0].getAttribute( "uri" )
	pXML = api.GET( pURI )
	pDOM = parseString( pXML )
	pName = pDOM.getElementsByTagName( "name" )[0].firstChild.data
	pName = pName.split( " " )[0] + " updated by Script"
	pDOM.getElementsByTagName( "name" )[0].firstChild.data = pName
	api.PUT( pDOM.toxml(), pURI )

if __name__ == "__main__":
	main()
