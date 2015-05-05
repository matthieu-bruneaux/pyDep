### * Description

# This module provides function to retrieve and process data from public
# databases such as GenBank and Ensembl.

### * Setup

### ** Import

from Bio import Entrez
import xml.etree.ElementTree as ET

### * Functions

### ** gbSearch(term, retmax)
def gbSearch(term, retmax) :
    """Perform a Entrez.esearch on db="nuccore", using history.
    TAKES
    term: string, the GenBank search tem
    retmax: int, the maximum number of returned ids
    RETURNS
    A dictionary with the ids, their count and the history information"""
    logging.debug("Start a search with query: " + term)
    handle = Entrez.esearch(db = "nuccore", term = term, retmax =retmax,
                            usehistory = "y")
    results = Entrez.read(handle)
    handle.close()
    output = dict()
    output["idList"] = results["IdList"]
    output["count"] = int(results["Count"])
    output["webEnv"] = results["WebEnv"]
    output["queryKey"] = results["QueryKey"]
    logging.debug("Found %i entries while retmax was %i" % (output["count"], retmax))
    return(output)

### ** getDocSum(search)
def getDocSum(search, retmax) :
    """Fetch the documents summaries for the entries from an Entrez.esearch.
    TAKES
    search: output from gbSearch() (at minimum a dict with "webEnv" and 
      "queryKey")
    retmax: int, the maximum number of document summaries to get
    RETURNS
    A string containing the summaries in an XML format"""
    logging.debug("Start fetching %i docsums while retmax is %i" %
                  (search["count"],retmax))
    handle = Entrez.efetch(db = "nuccore", rettype = "docsum", retmode = "xml",
                           retstart = 0, retmax = retmax,
                           webenv = search["webEnv"],
                           query_key = search["queryKey"])
    data = handle.read()
    handle.close()
    logging.debug("End of fetching")
    return(data)

### ** getDocSum(search)
def getGenBank(search, retmax) :
    """Fetch the GenBank records for the entries from an Entrez.esearch.
    TAKES
    search: output from gbSearch() (at minimum a dict with "webEnv" and 
      "queryKey")
    retmax: int, the maximum number of document summaries to get
    RETURNS
    A string containing the summaries in an XML format"""
    logging.debug("Start fetching %i GenBank records while retmax is %i" %
                  (search["count"],retmax))
    handle = Entrez.efetch(db = "nuccore", rettype = "gb", retmode = "xml",
                           retstart = 0, retmax = retmax,
                           webenv = search["webEnv"],
                           query_key = search["queryKey"])
    data = handle.read()
    handle.close()
    logging.debug("End of fetching")
    return(data)

### ** parseDocSumXML(xmlFile)

def parseDocSumXML(xmlFile) :
    """Parse the documents summaries contained in an xml files into a list of
    dictionaries.
    TAKES
    xmlFile: name or path to the file (string)
    RETURNS
    A list of dictionaries containing the entries
    """
    logging.debug("Start the parsing of the XML file with ElementTree")
    tree = ET.parse(xmlFile)
    logging.debug("Parsing with ElementTree complete")
    root = tree.getroot()
    docsums = []
    logging.debug("Going through the XML tree to extract the docsum information")
    for child in root :
        entry = dict()
        nKeys = 0
        for i in child :
            if i.tag == "Item" :
                if i.text == None :
                    i.text = "None"
                entry[i.attrib["Name"]] = i.text
                nKeys += 1
        assert nKeys == 12
        docsums.append(entry)
    logging.debug("Docsum extraction complete")
    return(docsums)

### ** saveDocSums(tableFile)

def saveDocSums(docsums, tableFile) :
    """Save the documents summaries into a tabular format.
    TAKES
    docsums: a list of dictionaries, output from parseDocSumXML()
    tableFile: name of the output file (string)
    RETURNS
    None
    """
    logging.debug("Start writing the docsums table file")
    with open(tableFile, "w") as fo :
        headers = docsums[0].keys()
        fo.write("\t".join(headers) + "\n")
        for i in docsums :
            fo.write("\t".join([i[h] for h in headers]) + "\n")
