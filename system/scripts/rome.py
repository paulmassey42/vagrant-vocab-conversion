# Generic functions
import rdflib
import hashlib
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, XSD

SKOSXL = rdflib.Namespace("http://www.w3.org/2008/05/skos-xl#")
SKOSTHES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")
ESCOMODEL = rdflib.Namespace("http://data.europa.eu/esco/model#")

ROME = URIRef("http://data.europa.eu/esco/ConceptScheme/rome")

def text(text):
    '''Return an RDF Literal with the text.'''
    return Literal(text, lang="fr")

def rdfinteger(strin):
    '''Return an RDF Literal with the text.'''
    return Literal(int(strin),datatype=XSD.integer)
        
def add_value_integer(item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,rdfinteger(value)))           

def add_value_text(item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,text(value)))

def add_value_label(item,label,predicate,uri,g):
    value = item[label.lower()]
    if value != "" :
        g.add((uri,predicate,text(sanitise_label(value))))

def add_isco(self,item,isco_label,uri,g):
    value = item[isco_label.lower()]
    if value != "" :
        code=value.split()[1]
        isco_ref = URIRef("http://data.europa.eu/esco/isco2008/Concept/C"+code)
        g.add((uri,ESCOMODEL.memberOfISCOGroup,isco_ref))

def add_isco_raw(self,item,isco_label,uri,g):
    code = str(int(item[isco_label.lower()]))
    if code != "" :
        isco_ref = URIRef("http://data.europa.eu/esco/isco2008/Concept/C"+code)
        g.add((uri,ESCOMODEL.memberOfISCOGroup,isco_ref))
        
def uri(self, name):
    '''Return the URI of name.'''
    # note: put a lower() before the encode() will mean a case will 
    # be ignored in the original data sheet (or correct the data sheet).
    return self.ns.term(URIRef(hashlib.md5(name.encode()).hexdigest()))
        
def create_label(self,id,label,g):
    uri = uri_id(self,"L"+''.join(str(id).split()))
    g.add((uri,RDF.type,SKOSXL.Label))
    g.add((uri,RDF.type,SKOSTHES.PreferredTerm))
    g.add((uri,RDF.type,ESCOMODEL.Label)) 
    g.add((uri,SKOSXL.literalForm,text(sanitise_label(label))))
    return uri

def sanitise_label(text):
    '''Return a sanitised label - new newlines, tabs, '|' or ',' characters'''
    str0 = text.replace("\n"," ").replace("\r"," ").replace("\t"," ")
    str1 = str0.replace("|"," ").replace(","," ")
    return str1;

def uri_id(self, id):
    '''Return the URI of the id.'''
    return self.ns.term(''.join(str(id).split()))

def split(self, values):
    '''Split a comma-separated list of values.'''
    return re.split(r"\s*,\s*", values)

