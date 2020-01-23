# -*- coding: utf-8 -*-
"""
RDFa 1.1 validator. HTML source template for the output

@summary: RDFa validator, html template
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@var html_page: the XHTML code as a template for the output
"""

"""
$Id: html.py,v 1.4 2011-11-15 11:56:43 ivan Exp $ $Date: 2011-11-15 11:56:43 $
"""

html_page = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
	<title>RDFa 1.1 Validator results</title>
	<link rel="icon" type="image/png" href="/2001/sw/favicon-sw.png" />
	<link rel="meta" type="application/rdf+xml" title="FOAF" href="http://www.ivan-herman.net/foaf.rdf" />
	<meta name="Author" content="Ivan Herman, Semantic Web Activity Lead, W3C" />
	<link rel="copyright" href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231" title="CC Copyrights" />
	<link rel="stylesheet" type="text/css" href="/StyleSheets/base.css"/>
	<link rel="stylesheet" type="text/css" href="/2001/sw/swstyle.css"/>
	<link rel="stylesheet" type="text/css" href="/2001/sw/swstyleExtras.css"/>
	<link rel="stylesheet" type="text/css" href="/2007/08/pyrdfa/style/pyrdfa.css"/>
   <style type="text/css">
        #Turtle {
            padding: 0.5em;
            border: thin inset;
            background-color: rgb(255, 255, 204);
        }
        div#Message p:first-child {
            font-weight: bold;
            font-size: 120%%;
            font-style: italic
        }
		div#Message {
			background-color: inherit
		}
        p.Error span:first-child { color: red}
        p.Warning span:first-child { color: blue}
        p.Info span:first-child { color: green}
		address { font-size:90%% }
        body {
            font-size : 100%%
        }
     </style>
  </head>
  <body prefix="doap: http://usefulinc.com/ns/doap#">
		<p class="banner"><a href="/2001/sw/" ><img src="/Icons/SW/sw-horz-w3c.png" width="241" height="48" alt="W3C SW Logo"/></a></p>
        <h1 id="title" class="title"><img src="/Icons/SW/Buttons/sw-rdfa-orange.png" alt="RDFa technology button"/>&nbsp;&nbsp;RDFa Validation results </h1>
         
      <h2>Validator messages</h2>

      <div id="Message">
      </div>

      <h2>Generated RDF content in Turtle format</h2>
      <div id="Turtle">
<pre id="output">
</pre>
        </div>
      
        <hr />
        <address>
		    <a href="http://www.w3.org/People/Ivan/">Ivan Herman</a> (<a href="mailto:ivan@w3.org">ivan@w3.org</a>)
			<br />
			%s
		</address>
  </body>
</html>
"""
