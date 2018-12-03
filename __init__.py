# -*- coding: utf-8 -*-
"""
RDFa 1.1 validator. Is simply a small shell around the RDFa 1.1 distiller, catching the
error and warning triples and displaying them as part of an HTML page in a more human readable fashion. It is meant
to run as a back end to a CGI script.

The code's behaviour is:

 - generate the default and the processor graphs via the distiller
 - take the HTML code template in L{html_page}
 - expand the DOM tree of that template by (a) generate a list of errors and warnings in HTML and (b) add the generated code
 - serialize the HTML page as an output to the CGI call

@summary: RDFa validator
@requires: Python version 2.5 or up
@requires: U{RDFLib<http://rdflib.net>}; version 3.X is preferred, it has a more readable output serialization.
@requires: U{pyRdfa<http://www.w3.org/2007/08/pyrdfa/>}, version 3.X (i.e., corresponding to RDFa 1.1)
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: __init__.py,v 1.8 2013-03-18 12:28:28 ivan Exp $ $Date: 2013-03-18 12:28:28 $
"""

__version__ = "1.0"
__author__  = 'Ivan Herman'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231'

import sys
PY3 = (sys.version_info[0] >= 3)

if PY3 :
	from io import StringIO
else :
	from StringIO import StringIO

from datetime import date

import rdflib
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import RDF  as ns_rdf
	from rdflib	import RDFS as ns_rdfs
else :
	from rdflib.RDFS	import RDFSNS as ns_rdfs
	from rdflib.RDF		import RDFNS  as ns_rdf

from pyRdfa 			import pyRdfa
from pyRdfa.options		import Options
from pyRdfa.host 		import MediaTypes

try :
	from pyRdfaExtras import MyGraph as Graph
except :
	if rdflib.__version__ >= "3.0.0" :
		from rdflib	import Graph
	else :
		from rdflib.Graph import Graph

import xml.dom.minidom

from rdfavalidator.html	   import html_page
from rdfavalidator.errors  import Errors

class Validator :
	"""
	Shell around the distiller and the error message management.
	@ivar default_graph: default graph for the results
	@ivar processor_graph: processor graph (ie, errors and warnings)
	@ivar uri: file like object or URI of the source
	@ivar base: base value for the generated RDF output
	@ivar media_type: media type of the source
	@ivar vocab_expansion: whether vocabulary expansion should occur or not
	@ivar rdfa_lite: whether RDFa 1.1 Lite should be checked
	@ivar hturtle: whether the embedded turtle should be included in the output
	@ivar domtree: the Document Node of the final domtree where the final HTML code should be added
	@ivar message: the Element Node in the final DOM Tree where the error/warning messages should be added
	@ivar code: the Element Node in the final DOM Tree where the generated code should be added
	@ivar errors: separate class instance to generate the error code
	@type errors: L{Errors}
	"""
	def __init__(self, uri, base, media_type, vocab_expansion = False, rdfa_lite = False, embedded_rdf = False) :
		"""
		@param uri: the URI for the content to be analyzed
		@type uri: file-like object (e.g., when content goes through an HTTP Post) or a string
		@param base: the base URI for the generated RDF
		@type base: string
		@param media_type: Media Type, see the media type management of pyRdfa. If "", the distiller will try to find the media type out.
		@type media_type: pyRdfa.host.MediaTypes value
		"""
		# Create the graphs into which the content is put
		self.default_graph   = Graph()
		self.processor_graph = Graph()
		self.uri 			 = uri
		self.base			 = base
		self.media_type		 = media_type
		self.embedded_rdf	 = embedded_rdf
		self.rdfa_lite		 = rdfa_lite
		self.vocab_expansion = vocab_expansion
		
		# Get the DOM tree that will be the scaffold for the output
		self.domtree = xml.dom.minidom.parse(StringIO(html_page % date.today().isoformat()))
		# find the warning/error content
		for div in self.domtree.getElementsByTagName("div") :
			if div.hasAttribute("id") and div.getAttribute("id") == "Message" :
				self.message = div
				break
		# find the turtle output content
		for pre in self.domtree.getElementsByTagName("pre") :
			if pre.hasAttribute("id") and pre.getAttribute("id") == "output" :
				self.code = pre
				break
		
		self.errors = Errors(self)
	# end __init__
	
	def parse(self) :
		"""
		Parse the RDFa input and store the processor and default graphs. The final media type is also updated.
		"""
		transformers = []
		if self.rdfa_lite :
			from pyRdfa.transform.lite import lite_prune
			transformers.append(lite_prune)		
		
		options = Options(output_default_graph = True, output_processor_graph = True,
						  transformers    = transformers,
						  vocab_expansion = self.vocab_expansion,
						  embedded_rdf    = self.embedded_rdf,
						  add_informational_messages = True)
		processor = pyRdfa(options = options, base = self.base, media_type = self.media_type)
		processor.graph_from_source(self.uri, graph = self.default_graph, pgraph = self.processor_graph, rdfOutput = True)	
		# Extracting some parameters for the error messages
		self.processor 	= processor
		
	def complete_DOM(self) :
		"""
		Add the generated graph, in turtle encoding, as well as the error messages, to the final DOM tree
		"""
		# Add the RDF code in the DOM tree
		outp = self.default_graph.serialize(format="turtle")
		try :
			# This will fail on Python 3!
			u = unicode(outp.decode('utf-8'))
		except :
			u = outp

		dstr = self.domtree.createTextNode(u)
		self.code.appendChild(dstr)
		# Settle the error message
		self.errors.interpret()
				
	def run(self) :
		"""
		Run the two steps of validation, and return the serialized version of the DOM Tree, ready to be displayed
		"""
		self.parse()
		self.complete_DOM()
		return self.domtree.toxml(encoding="utf-8")

def validateURI(uri, form={}) :
	"""The standard processing of an RDFa uri options in a form, ie, as an entry point from a CGI call. For compatibility
	reasons with the RDFa 1.1 distiller (the same CGI entry point is used for both) the form's content may include a number
	of entries that this function ignores.

	The call accepts the following extra form option (eg, HTTP GET options):
	
	 - C{host_language=[xhtml,html,xml]} : the host language. Used when files are uploaded or text is added verbatim, otherwise the HTTP return header shoudl be used

	@param uri: URI to access. Note that the "text:" and "uploaded:" values are treated separately; the former is for textual intput (in which case a StringIO is used to get the data) and the latter is for uploaded file, where the form gives access to the file directly.
	@param form: extra call options (from the CGI call) to set up the local options
	@type form: cgi FieldStorage instance
	@return: serialized HTML content
	@rtype: string
	"""
	def _get_option(param, compare_value, default) :
		retval = default
		if param in list(form.keys()) :
			val = form.getfirst(param).lower()
			return val == compare_value

	if uri == "uploaded:" :
		input	= form["uploaded"].file
		base	= ""
	elif uri == "text:" :
		input	= StringIO(form.getfirst("text"))
		base	= ""
	else :
		input	= uri
		base	= uri
		
	if "rdfa_version" in list(form.keys()) :
		rdfa_version = form.getfirst("rdfa-version")
	else :
		rdfa_version = None
	
	# working through the possible options
	# Host language: HTML, XHTML, or XML
	# Note that these options should be used for the upload and inline version only in case of a form
	# for real uris the returned content type should be used
	if "host_language" in list(form.keys()) :
		if form.getfirst("host_language").lower() == "xhtml" :
			media_type = MediaTypes.xhtml
		elif form.getfirst("host_language").lower() == "html" :
			media_type = MediaTypes.html
		elif form.getfirst("host_language").lower() == "svg" :
			media_type = MediaTypes.svg
		elif form.getfirst("host_language").lower() == "atom" :
			media_type = MediaTypes.atom
		else :
			media_type = MediaTypes.xml
	else :
		media_type = ""

	rdfa_lite 		   = _get_option( "rdfa_lite", "true", True)		
	embedded_rdf   	   = _get_option( "embedded_rdf", "true", True)
	vocab_expansion    = _get_option( "vocab_expansion", "true", False)
	
	validator = Validator(input, base, media_type, vocab_expansion = vocab_expansion, rdfa_lite = rdfa_lite, embedded_rdf = embedded_rdf)
	
	try :
		return validator.run()
	except :
		# This branch should occur only if an exception is really raised, ie, if it is not turned
		# into a graph value.
		(type,value,traceback) = sys.exc_info()
		import traceback, cgi
		print( "<html>" )
		print( "<head>" )
		print( "<title>Error in RDFa validation processing</title>" )
		print( "</head><body>" )
		print( "<h1>Error in RDFa validation processing</h1>" )
		print( "<pre>" )
		traceback.print_exc(file=sys.stdout)
		print( "</pre>" )
		print( "<pre>%s</pre>" % value )
		print( "<h1>Validator request details</h1>" )
		print( "<dl>" )
		if uri == "text:" and "text" in form and form["text"].value != None and len(form["text"].value.strip()) != 0 :
			print( "<dt>Text input:</dt><dd>%s</dd>" % cgi.escape(form["text"].value).replace('\n','<br/>') )
		elif uri == "uploaded:" :
			print( "<dt>Uploaded file</dt>" )
		else :
			print( "<dt>URI received:</dt><dd><code>'%s'</code></dd>" % cgi.escape(uri) )
		if "host_language" in form.keys() :
			print( "<dt>Media Type:</dt><dd>%s</dd>" % media_type )
		print( "</dl>" )
		print( "</body>" )
		print( "</html>" )


#############################
# For testing purposes
if __name__ == '__main__':
	sys.path.insert(0,"/Users/ivan/Library/Python")
	validator = Validator("test.html","", MediaTypes.html)
	print( validator.run() )

	

