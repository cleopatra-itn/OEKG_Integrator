import requests
import urllib.parse
import numpy as np
import math
from jsonmerge import merge

from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
    PROF, PROV, RDF, RDFS, SH, SKOS, SOSA, SSN, TIME, \
    VOID, XMLNS, XSD

SO = Namespace('http://schema.org/')
OEKG_R = Namespace(u'http://oekg.l3s.uni-hannover.de/resource/')
OEKG_S = Namespace('http://oekg.l3s.uni-hannover.de/schema/')
SEM = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')

url = "http://smldapi.l3s.uni-hannover.de/" # This needs to be changed
graph = "example"

def insert_example_triples():

    # reset graph
    clear_graph(graph)

    # Joe Biden in Wikidata: https://www.wikidata.org/wiki/Q6279
    biden_wikidata_id = "Q6279"

    # Second inauguration of Obama in Wikidata: https://www.wikidata.org/wiki/Q3526570
    obama_inauguration_wikidata_id = "Q3526570"

    # Query the OEKG API to get its IDs of the Wikidata entities
    oekg_ids = getOEKGIdsByWikidataIds(biden_wikidata_id, obama_inauguration_wikidata_id)
    print(oekg_ids)

    # create a set of triples describing two news articles with titles and main entities
    g = Graph()

    # bind prefixes. Only used when you create triples in the .ttl format. But for the upload, we use .nt!
    g.bind("oekg-r", OEKG_R)
    g.bind("oekg-s", OEKG_S)
    g.bind("so", SO)

    # add triples of first news article
    g.add((OEKG_R.article1, RDF.type, SO.Article))
    g.add((OEKG_R.article1, SO.mainEntity, URIRef(OEKG_R)+oekg_ids[biden_wikidata_id]))
    g.add((OEKG_R.article1, SO.headline, Literal('Bidens wins election.', 'en')))

    # add triples of second news article
    g.add((OEKG_R.article2, RDF.type, SO.Article))
    g.add((OEKG_R.article2, SO.mainEntity, URIRef(OEKG_R)+oekg_ids[obama_inauguration_wikidata_id]))
    g.add((OEKG_R.article2, SO.headline, Literal("Obama inaugurated the second time.", "en")))

    # Write triples into a file "example_articles.nt". Use the .nt format for uploading the graph.
    # For testing, you can use "turtle" as well.
    filename = "example_articles.nt"
    file = open(filename, "w")
    file.write(g.serialize(format='nt').decode("utf-8"))
    file.close()

    # Upload the file into to the OEKG, using the example graph
    uploadFileToOEKG(graph, filename)

def uploadFileToOEKG(graph, file_name):
    print("uploadFileToOEKG: " + url + "upload/"+graph)
    files = {'upload_file': open(file_name, 'rb')}
    r = requests.post(url + "upload/"+graph, files=files)#, data=data)
    print(r.text)


def getOEKGIdByWikidataId(wikidata_id):
    # Get OEKG ID of an entity via its Wikidata ID
    return requests.get(url + "api/wikidataId/" + wikidata_id).json()


def getOEKGIdsByWikidataIds(*wikidata_ids):
    # Get OEKG IDs of a set of entity via its Wikidata ID
    ids = {}
    for ids_sublist in np.array_split(wikidata_ids, math.ceil(len(wikidata_ids) / 5000)):
        res = requests.post(url + "api/wikidataIds", data= ";".join(ids_sublist)).json()
        ids = merge(ids, res)
    return ids


def getOEKGIdByWikipediaId(language, wikipedia_id):
    # Get OEKG ID of an entity via its Wikipedia ID
    return requests.get(url + "api/wikipediaId/" + language + "/" + wikipedia_id).json()


def getOEKGIdsByWikipediaIds(language, *wikipedia_ids):
    # Get OEKG IDs for a set of Wikidata IDs
    ids = {}
    for ids_sublist in np.array_split(wikipedia_ids, math.ceil(len(wikipedia_ids) / 5000)):
        res = requests.post(url + "api/wikidataIds/",data=";".join(ids_sublist)).json()
        ids = merge(ids, res)
    return ids


def clear_graph(graph_to_be_cleared):
    # Remove all triples uploaded within the given graph.
    print("Clear graph " + graph_to_be_cleared+".")
    r = requests.get(url + "clear/"+graph_to_be_cleared)
    print(r.text)


def query_oekg(query):
    result1 = requests.get(url + "sparql?query=" + urllib.parse.quote_plus(query) + "&format=json")
    print("RES: "+str(result1.json()))

if __name__ == '__main__':
    insert_example_triples()

    # Run an example query
    query = ("SELECT ?mainEntity ?title WHERE { "
              "?article so:mainEntity ?mainEntity .  "
              "?mainEntity owl:sameAs dbr:Joe_Biden . "
              "?article so:headline ?title . }")
    query_oekg(query)
