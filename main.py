import requests
import urllib.parse
import numpy as np
import math
from jsonmerge import merge

from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
    PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
    VOID, XMLNS, XSD

url = "http://localhost:4567/" # This needs to be changed
graph = "example"


def insert_example_triples():
    # Joe Biden in Wikidata: https://www.wikidata.org/wiki/Q6279
    biden_wikidata_id = "Q6279"

    # Second inauguration of Obama in Wikidata: https://www.wikidata.org/wiki/Q3526570
    obama_inauguration_wikidata_id = "Q3526570"

    # Query the OEKG API to get its IDs of the Wikidata entities
    oekg_ids = getOEKGIdsByWikidataIds(biden_wikidata_id, obama_inauguration_wikidata_id)

    # create a new namespace for OEKG
    OEKG_R = Namespace("http://eventkg.l3s.uni-hannover.de/resource/")

    # create a set of triples describing two news articles with titles and main entities
    g = Graph()

    # create proper prefixes "oekg-r" and "so" for namespaces
    g.bind("oekg-r", OEKG_R)
    g.bind("so", SDO)

    # add triples of first news article
    g.add((OEKG_R.article1, RDF.type, SDO.Article))
    g.add((OEKG_R.article1, SDO.mainEntity, URIRef(oekg_ids[biden_wikidata_id], OEKG_R)))
    g.add((OEKG_R.article1, SDO.headline, Literal('Bidens wins election.', 'en')))

    # add triples of second news article
    g.add((OEKG_R.article2, RDF.type, SDO.Article))
    g.add((OEKG_R.article2, SDO.mainEntity, URIRef(oekg_ids[obama_inauguration_wikidata_id], OEKG_R)))
    g.add((OEKG_R.article2, SDO.headline, Literal("Obama inaugurated the second time.", "en")))

    # Write triples into a file "example_articles.ttl".
    file = open("example_articles.ttl", "w")
    file.write(g.serialize(format='turtle').decode("utf-8"))
    file.close()

    # Upload the file into to the OEKG, using the example graph
    uploadFileToOEKG(graph, "example_articles.ttl")

    clear_graph(graph)


def uploadFileToOEKG(graph, file_name):
    files = {'upload_file': open(file_name, 'rb')}
    r = requests.post(url + "upload/"+graph, files=files)
    print(r.text)


def getOEKGIdByWikidataId(wikidata_id):
    # Get OEKG ID of an entity via its Wikidata ID
    return requests.get(url + "api/wikidataId/" + wikidata_id).json()


def getOEKGIdsByWikidataIds(*wikidata_ids):
    # Get OEKG IDs of a set of entity via its Wikidata ID
    ids = {}
    for ids_sublist in np.array_split(wikidata_ids, math.ceil(len(wikidata_ids) / 1)):
        res = requests.get(url + "api/wikidataIds/" + ";".join(ids_sublist)).json()
        ids = merge(ids, res)
    return ids


def getOEKGIdByWikipediaId(language, wikipedia_id):
    # Get OEKG ID of an entity via its Wikipedia ID
    return requests.get(url + "api/wikipediaId/" + language + "/" + wikipedia_id).json()


def getOEKGIdsByWikipediaIds(language, *wikipedia_ids):
    # Get OEKG IDs for a set of Wikidata IDs
    ids = {}
    for ids_sublist in np.array_split(wikipedia_ids, math.ceil(len(wikipedia_ids) / 1)):
        res = requests.get(url + "api/wikidataIds/" + ";".join(ids_sublist)).json()
        ids = merge(ids, res)
    return ids


def clear_graph(graph_to_be_cleared):
    # Remove all triples uploaded within the given graph.
    r = requests.get(url + "clear/"+graph_to_be_cleared)
    print(r.text)


def query_oekg():
    query1 = ("SELECT ?title WHERE { "
              "?article so:mainEntity ?mainEntity .  "
              "?mainEntity owl:sameAs dbr:Joe_Biden . "
              "?article dcterms:title ?title . }")
    result1 = requests.get(url + "query/" + urllib.parse.quote_plus(query1))
    print(result1)


if __name__ == '__main__':
    insert_example_triples()
    query_oekg()
