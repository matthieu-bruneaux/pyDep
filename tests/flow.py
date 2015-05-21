### * Setup

### ** Import

import os
import sys
sys.path.append("./")
import imp
import time

### * Functions

### ** loadFileContent(filename, comments = "#")

def loadFileContent(filename, comments = "#") :
    """Load the content of a file to a list of strings, removing the comments on
    the way.

    Args:
        filename (str): Filename
        comments (str): Lines starting with [blank] and this character are 
          considered comments and discarded

    Returns:
        list of str: A list containing each line, stripped of flanking blanks, 
          and without the lines considered as comments
    """
    o = []
    with open(filename, "r") as fi :
        for l in fi :
            line = l.strip()
            if line != "" and not line.startswith(comments):
                o.append(line)
    return o

### ** splitByOneSep(string, sep)

def splitByOneSep(string, sep) :
    """Split one string into a list of its elements separated with a separator.

    Args:
        string (str): Source string
        sep (str, one char): Separator

    Returns:
        list: A list of the elements of string separated by sep

    """
    splitStr = string.split(sep)
    o = []
    for s in splitStr :
        o += [s, sep]
    return o[:-1]

### ** splitTokens(source, sep = "={};")

def splitTokens(source, sep = "={};") :
    """Take a string or a list of strings and split them using the given
    separators.  If a list is given in input, the output is the sum of the
    resulting lists (i.e. a regular list, not a nested list).

    Args:
        source (str or list of str): Content to be split
        sep (str): Each character of this string will be used as a separator 
          between tokens

    Returns:
        list of str: If the input was a string, the list resulting from 
          splitting this string with each of the separators. If the input was
          a list, the list resulting from concatenating the lists resulting 
          from splitting each element of the list with the separators.

    """
    if type(source) == str :
        o = splitTokens([str], sep)
        return o
    else :
        o = []
        for element in source :
            splitElement = [element]
            for s in sep :
                result = []
                [[result.append(y) for y in splitByOneSep(x, s)] for x in splitElement]
                splitElement = result
            o += splitElement
        o = [x.strip() for x in o if x.strip() != ""]
        return o

### ** getStatements(tokenList)

def getStatements(tokenList, openDef = "{", closeDef = "}", assign = "=",
                  nextProp = ";") :
    """Extract separate statements from a list of tokens.

    Args:
        tokenList (list of str): A list of tokens (output from 
          :func:`splitTokens`)

    Returns:
        list of tuples: A list of tuples, each tuple containing one statement 
          and its type. Each statement is a list of tokens that can be 
          processed on its own, one after the other.

    """
    inNodeDef = False
    expectedNodeOpenDef = False
    inEdgeDef = False
    statementType = None
    statements = []
    currentStatement = []
    separators = [openDef, closeDef, assign, nextProp]
    for t in tokenList :
        if inNodeDef or inEdgeDef :
            if t == openDef :
                if not (inNodeDef and expectedNodeOpenDef) :
                    raise Exception
                else :
                    currentStatement.append(t)
                    expectedNodeOpenDef = False
            elif t == closeDef :
                currentStatement.append(t)
                statements.append((statementType, currentStatement))
                currentStatement = []
                inNodeDef = False
                inEdgeDef = False
                statementType = None
            else :
                currentStatement.append(t)
        else :
            if t not in separators :
                inNodeDef = True
                statementType = "nodeDef"
                expectedNodeOpenDef = True
                currentStatement.append(t)
            elif t == openDef :
                inEdgeDef = True
                statementType = "edgeDef"
                currentStatement.append(t)
            else :
                raise Exception
    if inNodeDef or inEdgeDef :
        raise Exception
    return statements

### ** processNodeDef(nodeDef)

def processNodeDef(nodeDef) :
    """Process a node definition (list of tokens) into a node dictionary.
    
    Args:
        nodeDef (list): List of tokens defining a node

    Returns:
        dict: A node dictionary

    """
    node = dict()
    node["nodeName"] = nodeDef[0]
    nodeAttr = ["type", "label", "uniqueId", "filename"]
    if len(nodeDef) == 3 :
        node["type"] = "default"
        return node
    nodeDef = nodeDef[2:-1]
    while len(nodeDef) > 0 :
        if len(nodeDef) == 1 :
            assert len(nodeAttr) > 0
            node[nodeAttr[0]] = nodeDef[0].strip("\"")
            nodeAttr = nodeAttr[1:]
            nodeDef = []
        elif len(nodeDef) == 2 :
            assert nodeDef[1] == ";"
            assert len(nodeAttr) > 0
            node[nodeAttr[0]] = nodeDef[0].strip("\"")
            nodeAttr = nodeAttr[1:]
            nodeDef = []
        elif nodeDef[1] == ";" :
            assert len(nodeAttr) > 0
            node[nodeAttr[0]] = nodeDef[0].strip("\"")
            nodeAttr = nodeAttr[1:]
            nodeDef = nodeDef[2:]
        elif nodeDef[1] == "=" :
            assert len(nodeDef) > 2
            node[nodeDef[0]] = nodeDef[2].strip("\"")
            nodeDef = nodeDef[3:]
            if len(nodeDef) > 0 and nodeDef[0] == ";" :
                nodeDef = nodeDef[1:]
        else :
            raise Exception
    return node

### ** processEdgeDef(edgeDef)

def processEdgeDef(edgeDef) :
    """Process an edge definition (list of tokens) into an edge dictionary.
    
    Args:
        edgeDef (list): List of tokens defining a node

    Returns:
        dict: An edge dictionary

    """
    edge = dict()
    edge["path"] = []
    if len(edgeDef) < 3 :
        return edge
    edgeDef = edgeDef[1:-1]
    while len(edgeDef) > 0 :
        if len(edgeDef) == 1 :
            if edgeDef[0] == ";" :
                return edge
            edge["path"].append(edgeDef[0])
            edgeDef = edgeDef[1:]
        elif len(edgeDef) == 2 :
            assert edgeDef[1] == ";"
            edge["path"].append(edgeDef[0])
            edgeDef = edgeDef[2:]
        elif len(edgeDef) > 2 :
            if edgeDef[1] == ";" :
                edge["path"].append(edgeDef[0])
                edgeDef = edgeDef[2:]
            elif edgeDef[1] == "=" :
                assert edgeDef[2] != "path"
                edge[edgeDef[0]] = edgeDef[2]
                edgeDef = edgeDef[3:]
            else :
                raise Exception
        else :
            raise Exception
    return edge


### ** processFileContent(filename)

def processFileContent(filename) :
    """Process a file into node and edge definitions.

    Args:
        filename (str): Filename

    Returns:
        dict: A dictionary with

        * clusterName

        * nodeDefs (list)

        * edgeDefs (list)

        * folder (workflow folder for touched files)

    """
    c = loadFileContent(filename)
    t = splitTokens(c)
    s = getStatements(t)
    o = dict()
    o["clusterName"] = os.path.basename(filename)
    o["nodeDefs"] = [processNodeDef(x[1]) for x in s if x[0] == "nodeDef"]
    o["edgeDefs"] = [processEdgeDef(x[1]) for x in s if x[0] == "edgeDef"]
    o["folder"] = os.path.dirname(filename)
    return o

### ** fillNodeAttributes(nodeDef, defaultAttributes)

defaultNodeAttributes = {
    "label" : "Node",
    "shape" : "box",
    "style" : "filled", # bold, filled, dotted
    "color" : "\"#000000\"", # shape color
    "fillcolor" : "\"#9fafaf\"" # fill color
}

def fillNodeAttributes(nodeDef, defaultAttributes) :
    """Fill the missing attributes of a node definition.

    Args:
        nodeDef (dict): Dictionary defining a node
        defaultAttributes (dict): Mapping between node attributes and default
          values

    Returns:
        dict: A copy of the original nodeDef with updated attributes if they 
          were missing

    """
    o = nodeDef.copy()
    for k in defaultAttributes.keys() :
        if k not in o.keys() :
            o[k] = defaultAttributes[k]
    return o

### ** applyNodeConf(nodeDef, conf)

def applyNodeConf(nodeDef, conf) :
    """Update a node definition with the node attributes from a configuration 
    namespace

    Args:
        nodeDef (dict): Dictionary defining a node
        conf (namespace): Configuration namespace

    Returns:
        dict: A copy of the original nodeDef with updated attributes if they 
          were present in the configuration namespace
    
    """
    o = nodeDef.copy()
    if hasattr(conf, "nodeColor") :
        n = conf.nodeColor
        for k in n.keys() :
            if not n[k].startswith("\"") or not n[k].endswith("\"") :
                n[k] = "\"" + n[k] + "\""
        if o["type"] in n.keys() :
            o["fillcolor"] = n[o["type"]]
        elif "default" in n.keys() :
            o["fillcolor"] = n["default"]
    return o

### ** fillEdgeAttributes(edgeDef, defaultAttributes)

defaultEdgeAttributes = {
    "label" : "",
    "labelfontcolor" : "blue",
    "decorate" : "false", # true, false
    "style" : "filled", # bold, dotted, filled
    "color" : "\"#0E0E0E\"",
    "penwidth" : "1.3"
}

def fillEdgeAttributes(edgeDef, defaultAttributes, folder = "./") :
    """Fill the missing attributes of an edge  definition.

    Args:
        edgeDef (dict): Dictionary defining a edge
        defaultAttributes (dict): Mapping between edge atrributes and default
          values
        folder (str): Path to the workflow folder (for touched files tracking)

    Returns:
        dict: A copy of the original edgeDef with updated attributes if they 
          were missing

    """
    o = edgeDef.copy()
    for k in defaultAttributes.keys() :
        if k not in o.keys() :
            o[k] = defaultAttributes[k]
    if "monitor" in o.keys() :
        try :
            modif = os.path.getmtime(os.path.join(folder,
                                                  o["monitor"].strip("\"")))
            label = time.strftime("%Y-%m-%d\\n%H:%m:%S", time.localtime(modif))
            o["label"] = label
            o["decorate"] = "true"
        except OSError :
            pass
    return o

### ** writeNodes(nodeDefs)

def writeNodes(nodeDefs) :
    """Produce a string containing the node description in dot language.

    Args:
        nodeDefs (list of dict): List of node definitions that have been filled
          with :func:`fillNodeAttributes`

    Returns:
        str: String ready to be written to a dot file

    """
    o = ""
    for node in nodeDefs :
        o += makeNameDotSafe(node["nodeName"]) + " ["
        o += "label = " + makeLabelDotSafe(node["label"]) + ",\n  "
        o += "color = " + node["color"] + ",\n  "
        o += "shape = " + node["shape"] + ",\n  "
        o += "fillcolor = " + node["fillcolor"] + ",\n  "
        o += "style = " + node["style"] + "];\n\n"
    return o

### ** writeEdges(edgeDefs)

def writeEdges(edgeDefs) :
    """Produce a string containing the edge description in dot language.

    Args:
        nodeDefs (list of dict): List of edge definitions that have been filled
          with :func:`fillEdgeAttributes`

    Returns:
        str: String ready to be written to a dot file

    """
    o = ""
    for edge in edgeDefs :
        o += " -> ".join([makeNameDotSafe(x) for x in edge["path"]]) + " ["
        o += "label = " + makeLabelDotSafe(edge["label"]) + ",\n  "
        o += "labelfontcolor = " + edge["labelfontcolor"] + ",\n  "
        o += "decorate = " + edge["decorate"] + ",\n  "
        o += "color = " + edge["color"] + ",\n  "
        o += "penwidth = " + edge["penwidth"] + ",\n  "
        o += "style = " + edge["style"] + "];\n\n"
    return o

### ** makeNameDotSafe(name)

def makeNameDotSafe(name) :
    name = name.replace("-", "_").replace("/", "__")
    name = name.replace(".", "___")
    return "n_" + name

### ** makeLabelDotSafe(label)

def makeLabelDotSafe(label) :
    if not label.startswith("\"") :
        assert not label.endswith("\"")
        return "\"" + label + "\""
    else :
        return label

### ** prepareNodes(unitFlow)

def prepareNodes(unitFlow, conf = None) :
    """Process the content of one workflow file to produce the node output.

    Args:
        unitFlow (dict): Output from :func:`processFileContent`
        conf (namespace): Optional, a configuration namespace
    
    Returns:
        str: String describing the nodes in dot language

    """
    nodes = [fillNodeAttributes(x, defaultNodeAttributes) for x in unitFlow["nodeDefs"]]
    if conf is not None :
        nodes = [applyNodeConf(x, conf) for x in nodes]
    return writeNodes(nodes)

### ** prepareEdges(unitFlow)

def prepareEdges(unitFlow) :
    """Process the content of one workflow file to produce the edge output.

    Args:
        unitFlow (dict): Output from :func:`processFileContent`

    Returns:
        str: String describing the edges in dot language

    """
    edges = [fillEdgeAttributes(x, defaultEdgeAttributes,
                                unitFlow["folder"]) for x in unitFlow["edgeDefs"]]
    return writeEdges(edges)
    


### ** loadConfFile(filename, defaultConfig)

defaultConfig = {
    "rootFolder" : "./", # root folder
    "workflowFile" : "workflow" # pattern for workflow file names
}

def loadConfFile(filename, defaultConfig) :
    """Load and process the contents of a configuration file.

    Args:
       filename (str): Path to the configuration file. If it ends with ".py", 
         the suffix will be automatically removed for import
       defaultConfig (dict): Default option values

    Returns:
        namespace: Namespace with the configuration options

    """
    # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    conf = imp.load_source("myConf", filename)
    # Set up default values if needed
    for k in defaultConfig :
        if not hasattr(conf, k) :
            setattr(conf, k, defaultConfig[k])
    # Get the list of all workflow files
    def l (arg, dirname, fnames) :
        for f in fnames :
            if f == conf.workflowFile :
                arg.append(os.path.join(dirname, f))
    conf.workflowFileList = []
    rootFolder = os.path.join(os.path.dirname(filename), conf.rootFolder)
    os.path.walk(rootFolder, l, conf.workflowFileList)
    return conf

### ** processWorkflowFileToCluster(filename)

def processWorkFlowFileToCluster(filename, clusterName, conf = None) :
    """Process a workflow file to the dot string representing the cluster

    Args:
        filename (str): File name
        clusterName (str): Name of the cluster
        conf (namespace): Optional, configuration namespace

    Returns:
        str: String ready to be inserted in the dot file

    """
    content = processFileContent(filename)
    nodes = prepareNodes(content, conf)
    edges = prepareEdges(content)
    o = ""
    o += "subgraph cluster" + makeNameDotSafe(clusterName) + " {\n  "
    o += "label = \"" + clusterName + "\"\n  "
    o += nodes
    o += edges
    o += "}\n"
    return o

### ** workflowFileToLabel(filepath)

def workflowFileToLabel(filepath) :
    """Convert the path to a workflow file to the cluster label

    Args:
        filepath (str): Path to the workflow file (including the filename)

    Returns:
        str: Label for the cluster

    """
    o = os.path.dirname(filepath)
    o = os.path.basename(o)
    return o

### * Main function

def _main() :

    confFile = sys.argv[1]
    conf = loadConfFile(confFile, defaultConfig)
    with open("toto.dot", "w") as fo :
        fo.write("digraph G {\n")
        for fi in conf.workflowFileList :
            fo.write(processWorkFlowFileToCluster(fi, workflowFileToLabel(fi), conf))
        fo.write("}\n")
