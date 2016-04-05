#!/usr/bin/env python3
# Convert a spreadsheet containing goals, transactions, high level
# requirements, information requirements, and business rules, according to
# the e-Document engineering methodology, to RDF satisfying the MDR vocabulary.
#
# Copyright 2014 European Union
# Author: Vianney le Clément de Saint-Marcq (PwC EU Services)
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

import argparse
import sys
import re
import xlrd
import rdflib
import hashlib

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, XSD
VOCAB = rdflib.Namespace("http://data.europa.eu/esco/de#")
SKOSXL = rdflib.Namespace("http://www.w3.org/2008/05/skos-xl#")
SKOSTHES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")
ESCOMODEL = rdflib.Namespace("http://data.europa.eu/esco/model#")

# Strings indicating that labels at the top of the file

level1_id="BA-Systematik Ebene 1"
level1_label="Bezeichnung"

level2_id="BA-Systematik Ebene 2"
level2_label="Bezeichnung1"

level3_id="BA-Systematik Ebene 3"
level3_label="Bezeichnung2"

level4_id="BA-Systematik Ebene 4"
level4_label="Bezeichnung3"

level5_id="BA-Systematik Ebene 5"
level5_label="Bezeichnung4"

endpos_label="Endposition (8-Steller)"   # level 6
jobname_label="Berufsposition (Bezeichnung)"

x2="berufskundl. Typ"
x3="Berufskundliche Hautpgruppe"
x4="Bezeichnung5"
x5="Berufskundliche Grobgruppe"
x6="Bezeichnung6"
x7="BKGR"
x8="Bezeichnung7"
skill_label="Qualifikationsniveau 1=Anlern-/Hilfsniveau 2=Ausbildungsniveau 3=Weiterbildungsniveau 4=Hochschulniveau"
drq_level_label="DQR-Niveau"
isco_label="ISCO 08-Zuordnung"
trainings_label="Korrespondierende Tatigkeit/Ausbildung"
competencies_label="Kompetenzen"
activities_label="Ausubungsformen (Tatigkeit-Tatigkeit)"

class VocabMappingGermany:

    '''The German Spreadsheet Cass handles a spreadsheet. '''

    def __init__(self, filename, namespace):
        '''Initialize the spreadsheet.

        Arguments:
        filename -- the path to the xls/xlsx file
        namespace -- the namespace of the resulting graph
        '''
        self.workbook = xlrd.open_workbook(filename)
        self.ns = rdflib.Namespace(namespace)

    # Utility methods

    def column_name(self, name, prefix):
        '''Return the normalized column name name.'''
        name = re.sub("^"+prefix.lower()+r"\s+", "", name.strip().lower())
        name = re.sub(r"^reference\s+to\s+", "", name)
        name = re.sub(r"\s+", " ", name)
        return name

    def read_sheet(self, name, prefix):
        '''Read the sheet named name and yield the rows as dictionaries indexed
        by the column name.'''
        sheet = self.workbook.sheet_by_name(name)
        header = [self.column_name(sheet.cell(0, i).value, prefix)
                  for i in range(sheet.ncols)]
        for i in range(1, sheet.nrows):
            yield {name:sheet.cell(i, j).value
                   for j, name in enumerate(header)}

    def uri(self, name):
        '''Return the URI of name.'''
        # note: put a lower() before the encode() will mean a case will 
        # be ignored in the original data sheet (or correct the data sheet).
        return self.ns.term(URIRef(hashlib.md5(name.encode()).hexdigest()))

    def uri_id(self, id):
        '''Return the URI of the id.'''
        return self.ns.term(''.join(id.split()))

    def text(self, text):
        '''Return an RDF Literal with the text.'''
        return Literal(text, lang="de")

    def integer(self, text):
        '''Return an RDF Literal with the text.'''
        return Literal(text, datatype=XSD.integer)
        
    def sanitise_label(self, text):
        '''Return a sanitised label - new newlines, tabs, '|' or ',' characters'''
        str0 = text.replace("\n"," ").replace("\r"," ").replace("\t"," ")
        str1 = str0.replace("|"," ").replace(","," ")
        return str1;
    
    def split(self, values):
        '''Split a comma-separated list of values.'''
        return re.split(r"\s*,\s*", values)

    # Main methods

    def convert(self):
        '''Return the RDF Graph corresponding to the spreadsheet.'''
        g = rdflib.Graph()
        g.bind("skos", str(SKOS))
        self.convert_rows(g)
        return g

    def convert_rows(self, g):
        '''Add the contents of the 'Tabelle1' sheet to the graph g.'''
        for item in self.read_sheet("Tabelle1", ""):
            identifier1 = item[level1_id.lower()]
            # check row is not empty
            if identifier1 != "" :
                self.convert_row(item,g)

    def cv_common(self,item,g,uri):
        g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        pubid = item["public identifier (uri)"]
        if pubid != "":
            g.add((uri, DCTERMS.identifier, URIRef(pubid)))

    def create_label(self,id,label,g):
        uri = self.uri_id("L"+id)
        g.add((uri,RDF.type,SKOSXL.Label))
        g.add((uri,RDF.type,SKOSTHES.PreferredTerm))
        g.add((uri,RDF.type,ESCOMODEL.Label)) 
        g.add((uri,SKOSXL.literalForm,self.text(self.sanitise_label(label))))
        return uri

    def add_trainings(self,item,uri,g):
        trainings = item[trainings_label.lower()]
        if trainings != "" :
            for training in trainings.splitlines():
                g.add((uri,VOCAB.training,self.text(self.sanitise_label(training))))

    def add_skilllevel(self,item,uri,g):
        skilllevel = item[skill_label.lower()]
        g.add((uri,VOCAB.skilllevel,self.integer(self.sanitise_label(skilllevel))))
        
    def add_drq_level(self,item,uri,g):
        drq_level = item[drq_level_label.lower()]
        if drq_level != "" :        
            g.add((uri,VOCAB.drq_level,self.text(self.sanitise_label(drq_level))))
        
    def add_isco_level(self,item,uri,g):
        val = item[isco_label.lower()]
        if val != "" :        
            g.add((uri,VOCAB.isco,self.text(self.sanitise_label(val))))
        
    def add_activities(self,item,uri,g):
        activities = item[activities_label.lower()]
        if activities != "" :
            for activity in activities.splitlines():
                g.add((uri,VOCAB.activity,self.text(self.sanitise_label(activity))))

    def add_competencies(self,item,uri,g):
        competencies = item[competencies_label.lower()]
        if competencies != "" :
            for competency in competencies.splitlines():
                g.add((uri,VOCAB.competency,self.text(self.sanitise_label(competency))))
    
    def add_extras(self,item,uri,g):
        self.add_isco_level(item,uri,g)
        self.add_drq_level(item,uri,g)
        self.add_skilllevel(item,uri,g)        
        self.add_competencies(item,uri,g)
        self.add_activities(item,uri,g)
        self.add_trainings(item,uri,g)        

    def convert_row(self,item,g):
        identifier1 = item[level1_id.lower()]
        label1 = item[level1_label.lower()]
        label1_ref=self.create_label(identifier1,label1,g)
        uri1=self.uri_id(identifier1)
        g.add((uri1,RDF.type,SKOS.Concept))
        g.add((uri1,RDF.type,ESCOMODEL.SimpleConcept))                        
        g.add((uri1,SKOS.prefLabel,label1_ref))
        
        identifier2 = item[level2_id.lower()]
        label2 = item[level2_label.lower()]
        label2_ref=self.create_label(identifier2,label2,g)
        uri2=self.uri_id(identifier2)
        g.add((uri2,RDF.type,SKOS.Concept))
        g.add((uri2,RDF.type,ESCOMODEL.SimpleConcept))                        
        g.add((uri2,SKOS.prefLabel,label2_ref))
        
        identifier3 = item[level3_id.lower()]
        label3 = item[level3_label.lower()]
        label3_ref=self.create_label(identifier3,label3,g)
        uri3=self.uri_id(identifier3)
        g.add((uri3,RDF.type,SKOS.Concept))
        g.add((uri3,RDF.type,ESCOMODEL.SimpleConcept))                
        g.add((uri3,SKOS.prefLabel,label3_ref))

        identifier4 = item[level4_id.lower()]
        label4 = item[level4_label.lower()]
        label4_ref=self.create_label(identifier4,label4,g)
        uri4=self.uri_id(identifier4)
        g.add((uri4,RDF.type,SKOS.Concept))
        g.add((uri4,RDF.type,ESCOMODEL.SimpleConcept))                
        g.add((uri4,SKOS.prefLabel,label4_ref))

        identifier5 = item[level5_id.lower()]
        label5 = item[level5_label.lower()]
        label5_ref=self.create_label(identifier5,label5,g)
        uri5=self.uri_id(identifier5)
        g.add((uri5,RDF.type,SKOS.Concept))
        g.add((uri5,RDF.type,ESCOMODEL.SimpleConcept))                
        g.add((uri5,SKOS.prefLabel,label5_ref))

        # This is the bottom level
        endpos = item[endpos_label.lower()]
        if endpos != "" :
            jobname = item[jobname_label.lower()]
            label6_ref=self.create_label(endpos,jobname,g)        
            uri6=self.uri_id(endpos)
            g.add((uri6,RDF.type,SKOS.Concept))
            g.add((uri6,RDF.type,ESCOMODEL.SimpleConcept))                
            g.add((uri6,SKOS.prefLabel,label6_ref))
            g.add((uri6,VOCAB.end_position_identifier,self.text(self.sanitise_label(jobname))))
            g.add((uri6,VOCAB.jobname,self.text(self.sanitise_label(jobname))))
            self.add_extras(item,uri6,g)
            g.add((uri5,SKOS.narrower,uri6))                
            g.add((uri6,SKOS.broader,uri5))                

        g.add((uri1,SKOS.narrower,uri2))
        g.add((uri2,SKOS.narrower,uri3))
        g.add((uri3,SKOS.narrower,uri4))
        g.add((uri4,SKOS.narrower,uri5))
        
        g.add((uri2,SKOS.broader,uri1))
        g.add((uri3,SKOS.broader,uri2))
        g.add((uri4,SKOS.broader,uri3))
        g.add((uri5,SKOS.broader,uri4))
        
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.description = "Convert the ."
    ap.add_argument("xlsfile", help="input XLS(X) file")
    ap.add_argument("-N", "--namespace",
                    default="http://data.europa.eu/esco/de/",
                    help="output namespace (default: %(default)s)")
    ap.add_argument("-f", "--format", default="turtle",
                    help="serialization format (default: %(default)s)")
    args = ap.parse_args()
    edoc = VocabMappingGermany(args.xlsfile, args.namespace)
    g = edoc.convert()
    print(g.serialize(format=args.format).decode())

