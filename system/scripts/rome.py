# Generic functions
import rdflib
import hashlib
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, XSD

SKOSXL = rdflib.Namespace("http://www.w3.org/2008/05/skos-xl#")
SKOSTHES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")
ESCOMODEL = rdflib.Namespace("http://data.europa.eu/esco/model#")

ROME = URIRef("http://data.europa.eu/esco/ConceptScheme/rome")

def add_value_integer(self,item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,self.rdfinteger(value)))           

def add_value_text(self,item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,self.text(value)))

def add_value_label(self,item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,self.text(self.sanitise_label(value))))

def add_isco(self,item,uri,g):
    value = item[isco_label.lower()]
    if value != "" :
        code=value.split()[1]
        isco_ref = URIRef("http://data.europa.eu/esco/isco2008/Concept/C"+code)
        g.add((uri,ESCOMODEL.memberOfISCOGroup,isco_ref))

def uri(self, name):
    '''Return the URI of name.'''
    # note: put a lower() before the encode() will mean a case will 
    # be ignored in the original data sheet (or correct the data sheet).
    return self.ns.term(URIRef(hashlib.md5(name.encode()).hexdigest()))
        
def create_label(self,id,label,g):
    uri = self.uri_id("L"+''.join(str(id).split()))
    g.add((uri,RDF.type,SKOSXL.Label))
    g.add((uri,RDF.type,SKOSTHES.PreferredTerm))
    g.add((uri,RDF.type,ESCOMODEL.Label)) 
    g.add((uri,SKOSXL.literalForm,self.text(self.sanitise_label(label))))
    return uri

