### * Description

# Python module to produce a dependency graph between functions within a module

### * Setup

### ** Import

import sys
import os
import ast
import argparse
import subprocess

### * Functions

### ** astParseFile(sourceFileName)

def astParseFile(sourceFileName) :
    """Parse a source file using the ``ast`` module
    
    Args:
        sourceFileName (str): Name of the source file to parse

    Returns:
        ast.Module: Output from ``ast.parse`` (ast.Module object)

    """
    with open(sourceFileName, "r") as fi :
        source = fi.read()
    return(ast.parse(source))

### ** _getImportedModules(astParsedSource)

def _getImportedModules(astParsedSource) :
    importFromStatements = [(x.names[0].name, x.names[0].asname)
                            for x in astParsedSource.body if x.__class__ == ast.ImportFrom]
    importStatements = [(x.names[0].name, x.names[0].asname)
                        for x in astParsedSource.body if x.__class__ == ast.Import]
    return(importFromStatements + importStatements)
    
### ** getFunctionDef(astParsedSource)

def getFunctionDef(astParsedSource) :
    """Extract the function definitions from a parsed source file

    Args:
        astParsedSource (ast.Module): Parsed source, output from 
          :func:`astParseFile`

    Returns:
        list of ast.FunctionDef: List of the function definitions 
          (``ast.FunctionDef`` objects)

    """
    return([x for x in astParsedSource.body if x.__class__ == ast.FunctionDef])

### ** _getFunctionCallsFromOne(astFunctionDef)

def _getFunctionCallsFromOne(astFunctionDef) :
    """Extract the function calls from a function definition

    Args:
        astFunctionDef (ast.FunctionDef): Function definition, 
          ``ast.FunctionDef`` object

    Returns:
        list: List of (unique) functions called in the function definition

    """
    calls = [x for x in ast.walk(astFunctionDef) if x.__class__ == ast.Call]
    calledFunctions = set([x.func.id for x in calls if x.func.__class__ == ast.Name])
    return list(calledFunctions)

### ** getFunctionCalls(listFuncDef)

def getFunctionCalls(listFuncDef) :
    """Extract the function calls from a list of function definitions, and 
    return them in a dictionary

    Args:
        listFuncDef (list of ast.FunctionDef): List of function definitions
          (such as returned by :func:`getFunctionDef`)

    Returns:
        dict: Dictionary mapping function names (str) and the functions they 
          call (list of str)

    """
    o = dict()
    for f in listFuncDef :
        assert f.name not in o.keys()
        o[f.name] = _getFunctionCallsFromOne(f)
    return o

### ** filterLocalCalls(funcCallDict)

def filterLocalCalls(funcCallDict) :
    """Filter a dictionary of function calls to keep only functions which are 
    defined locally. This is done by filtering the values of the dictionary 
    (lists) and keeping only in those lists function names which are present
    in the keys of the dictionary.

    Args:
        funcCallDict (dict): Function calls dictionary, output from
          :func:`getFunctionCalls`

    Returns:
        dict: A copy of the input dictionary, with the value lists filtered to
          keep only function names present in the keys

    """
    o = funcCallDict.copy()
    for k in o.keys() :
        o[k] = [x for x in o[k] if x in o.keys()]
    return o

### ** getDotOptions(parsedArgs)

def getDotOptions(parsedArgs) :
    """Produce a dictionary with dot options from parsed arguments.
    """
    options = dict()
    options["nodeShape"] = parsedArgs.nodeShape
    return options

### ** writeDotSubgraphs(subgraphGroups, builtIn)

def writeDotSubgraphs(subgraphGroups, builtIn = False) :
    o = ""
    for cluster in subgraphGroups.keys() :
        if (cluster != "built-in" or builtIn) :
            o += "subgraph cluster" + cluster + " {\n"
            o += "label = \"" + cluster + "\";"
            for element in subgraphGroups[cluster] :
                o += element + ";\n"
            o += "}\n"
    return o
        

### ** _getFuncFromRelations(relations, getSingles = False)

def _getFuncFromRelations(relations, getSingles = False) :
    """Get the list of all functions present in a dictionary describing 
    function call relations

    Args:
        relations (dict): Dictionary describing the function relations, 
          output from :func:`getFunctionCalls` or :func:`filterLocalCalls`
        getSingles (boolean): If False, do not return functions which are not 
          calling nor called by another function

    Returns:
        list: List of function names

    """
    allFunctions = set([])
    if getSingles :
        for caller in relations.keys() :
            allFunctions.add(caller)
            for called in relations[caller] :
                allFunctions.add(called)
    else :
        for caller in relations.keys() :
            for called in relations[caller] :
                allFunctions.add(caller)
                allFunctions.add(called)
    return list(allFunctions)
                
### ** makeDotFileContent(relations, dotOptions, drawSingles)

def makeDotFileContent(relations, dotOptions = None, drawSingles = False) :
    if dotOptions is None :
        dotOptions = dict()
    o = ""
    o += "digraph G {\n"
    o += "rankdir=LR;\n"
    o += "subgraph cluster_1 {\n"
    allFunctions = _getFuncFromRelations(relations, drawSingles)
    if "nodeShape" in dotOptions.keys() :
        o += ("node[shape=" + dotOptions["nodeShape"] + "," +
              "style=filled," +
              "fillcolor=\"" + "#dfaf8f" + "\"];\n")
    for f in allFunctions :
        if f.startswith("_") and not f.startswith("_main"):
            o += f + ";\n"
    if "nodeShape" in dotOptions.keys() :
        o += ("node[shape=" + dotOptions["nodeShape"] + "," +
              "style=filled," +
              "fillcolor=\"" + "#7cb8bb" + "\"];\n")
    for f in allFunctions :
        if not f.startswith("_") :
            o += f + ";\n"
    if "nodeShape" in dotOptions.keys() :
        o += ("node[shape=" + dotOptions["nodeShape"] + "," +
              "style=filled," +
              "fillcolor=\"" + "#9fc59f" + "\"];\n")
    for f in allFunctions :
        if f.startswith("_main") :
            o += f + ";\n"
    for caller in relations.keys() :
        for called in relations[caller] :
            o += caller + " -> " + called + ";\n"
    o += "}\n"        
    o += "}\n"
    return(o)

### ** viewDotContent(content)

def viewDotContent(content) :
    """Display the rendered graph from a dot content, using ``ImageMagick``. 
    ``Dot`` and ``ImageMagick`` should be installed for this to work.

    Args:
        content (str): Dot content to be rendered

    Returns:
        subprocess returncode: The returned value from the ``display`` process.

    """
    if not (_isAvailable("dot") and _isAvailable("display")) :
        raise Exception("Dot or ImageMagick is missing, cannot display the graph")
    commandLineDot = ["dot", "-Tpng"]
    pDot = subprocess.Popen(commandLineDot, stdout = subprocess.PIPE,
                            stdin = subprocess.PIPE)
    commandLineDisplay = ["display", "-"]
    pDisplay = subprocess.Popen(commandLineDisplay, stdin = subprocess.PIPE)
    pDisplay.communicate(input = pDot.communicate(content)[0])
    return pDisplay.wait()

### ** _isAvailable(program)

def _isAvailable(program) :
    """Function to test if a program can be called from Python. Based on a post
    from stackoverflow: http://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script
    The function tries to execute: program --help.

    Args:
        program (str): Command to call the program to be tested

    Returns:
        boolean

    """
    try:
        devnull = open(os.devnull, "w")
        a = subprocess.Popen([program, "--help"], stdout = devnull,
                         stderr = devnull)
        a.communicate()
        a.wait()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


### ** makeDotFromSrc(filename)

def makeDotFromSrc(filename, dotOptions = None, drawSingles = False) :
    """Prepare the dot content describing a source file dependency graph

    Args:
        filename (str): Name of the source file

    Returns:
        str: Dot content describing the dependency graph

    """
    parsedSource = astParseFile(filename)
    functionDefs = getFunctionDef(parsedSource)
    functionCalls = filterLocalCalls(getFunctionCalls(functionDefs))
    if dotOptions is None :
        dotOptions = {"nodeShape" : "box"}
    dotContent = makeDotFileContent(functionCalls,
                                    dotOptions,
                                    drawSingles)
    return dotContent

### * Main-related functions

### ** _makeParser()

def _makeParser() :
    """Build the parser for the command-line script

    Returns:
        argparse.ArgumentParser: Argument parser object

    """
    parser = argparse.ArgumentParser(
        description =
        "Produce a dependency graph between functions within a module. The output "
        "is a dot file to be processed with graphviz.",
        epilog =
        "For more information about the node options, please refer to the Dot "
        "documentation (add url here).")
    parser.add_argument(dest = "inputModule", metavar = "MODULE.PY",
                        nargs = 1,
                        help = "A Python module file",
                        type = str)
    parser.add_argument("--nodeShape", type = str, default = "box",
                        help = "Node shape (default: box)")
    parser.add_argument("-q", "--quickView", action = "store_true",
                        help = "Provide a simple display of the dot file through "
                        "ImageMagick and remove the dot file")
    parser.add_argument("-s", "--drawSingles", action = "store_true",
                        help = "Draw functions which are not calling nor called by "
                        "another function")
    # parser.add_argument("-m", "--getMethods", action = "store_true",
    #                     help = "Also output method calls",
    #                     default = False)
    # parser.add_argument("-a", "--all", action = "store_true",
    #                     help = "Output all function calls, not only calls between "
    #                     "functions of the module")
    # parser.add_argument("--clusters", action = "store_true",
    #                     help = "Group the functions by their module of origin",
    #                     default = True)
    return parser

### ** _main(args = None, stdout = None, stderr = None)

def _main(args = None, stdout = None, stderr = None) :
    """Main function, entry point for the command line script

    Args:
        args (list): List of command line arguments. If None, the arguments are 
          taken from the command line
        stdout (file): stdout stream. If None, use sys.stdout
        stderr (file): stderr stream. If None, use sys.stderr
    
    """
    # Argument parser
    parser = _makeParser()
    if args is None :
        args = parser.parse_args()
    else :
        args = parser.parse_args(args)
    # Streams
    if stdout is None :
        stdout = sys.stdout
    if stderr is None :
        stderr = sys.stderr
    # Main logic
    dotContent = makeDotFromSrc(args.inputModule[0],
                                getDotOptions(args),
                                args.drawSingles)
    if args.quickView :
        viewDotContent(dotContent)
    else :
        stdout.write(dotContent)
