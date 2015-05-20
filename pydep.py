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
    with open(sourceFileName, "r") as fi :
        source = fi.read()
    return(ast.parse(source))

### ** getImportedModules(astParsedSource)

def getImportedModules(astParsedSource) :
    importFromStatements = [(x.names[0].name, x.names[0].asname)
                            for x in astParsedSource.body if x.__class__ == ast.ImportFrom]
    importStatements = [(x.names[0].name, x.names[0].asname)
                        for x in astParsedSource.body if x.__class__ == ast.Import]
    return(importFromStatements + importStatements)
    
### ** getFunctionDef(astParsedSource)

def getFunctionDef(astParsedSource) :
    return([x for x in astParsedSource.body if x.__class__ == ast.FunctionDef])

### ** extractFunctionCalls(functionDefs)

def extractFunctionCalls(functionDefs, getMethods = False) :
    calls = dict()
    for func in functionDefs :
        calls[func.name] = calls.get(func.name, set([]))
        callsByFunc = [x for x in ast.walk(func)
                       if x.__class__ == ast.Call]
        calledFunctions = [x.func.id for x in callsByFunc
                           if x.func.__class__ == ast.Name]
        calledMethods = [(x.func.value, x.func.attr) for x in callsByFunc
                         if x.func.__class__ == ast.Attribute]
        for call in calledFunctions :
            calls[func.name].add(call)
        if getMethods :
            for call in calledMethods :
                value = call[0]
                if value.__class__ == ast.Name :
                    className = value.id
                elif value.__class__ == ast.Str :
                    className = "str"
                elif value.__class__ == ast.Subscript :
                    className = "dict"
                else :
                    className = "toto"
                    # raise Exception("Unknown ast attr class" + repr(value.__class__))
                method = call[1]
                calls[func.name].add("_mthd_".join([className, method]))
    return calls

### ** getFunctionOrigin(functionCalls, moduleName)

def getFunctionOrigin(functionCalls, moduleName, keepOnlyFrom = None) :
    origins = dict()
    origins["built-in"] = set([])
    origins[moduleName] = set([])
    allFunctions = functionCalls.keys()
    for x in functionCalls.values() :
        allFunctions += list(x)
    for func in allFunctions :
        if func in functionCalls.keys() :
            origins[moduleName].add(func)
        elif "_mthd_" in func :
            (className, method) = func.split("_mthd_")
            origins[className] = origins.get(className, set([]))
            origins[className].add(func)
        else :
            origins["built-in"].add(func)
    if not keepOnlyFrom is None :
        filteredOrigins = {}
        for key in origins.keys() :
            if key in keepOnlyFrom or key == moduleName :
                filteredOrigins[key] = origins[key]
        origins = filteredOrigins
    return origins
        
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
        
### ** makeDotFileContent(relations, onlyLocal)

def makeDotFileContent(relations, funcOrigin = None, dotOptions = dict(),
                       onlyLocal = True) :
    o = ""
    o += "digraph G {\n"
    o += "rankdir=LR;\n"
    allFunctions = set()
    if not funcOrigin is None :
        # Get names of functions in modules
        allowedFunctions = []
        for f in funcOrigin.values() :
            allowedFunctions += f
    else :
        allowedFunctions = []    
    for caller in relations.keys() :
        for called in relations[caller] :
            if ((not onlyLocal) or (called in relations.keys()) or
                (called in allowedFunctions)) :
                allFunctions.add(caller)
                allFunctions.add(called)
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
    if not funcOrigin is None :
        # Write subgraphs
        #o += writeDotSubgraphs(funcOrigin)
        # Get names of functions in modules
        allowedFunctions = []
        for f in funcOrigin.values() :
            allowedFunctions += f
    else :
        allowedFunctions = []    
    for caller in relations.keys() :
        for called in relations[caller] :
            if ((not onlyLocal) or (called in relations.keys()) or
                (called in allowedFunctions)) :
                o += caller + " -> " + called + ";\n"
    o += "}\n"
    return(o)

### ** viewDotContent(content)

def viewDotContent(content) :
    commandLineDot = ["dot", "-Tpng"]
    pDot = subprocess.Popen(commandLineDot, stdout = subprocess.PIPE,
                            stdin = subprocess.PIPE)
    commandLineDisplay = ["display", "-"]
    pDisplay = subprocess.Popen(commandLineDisplay, stdin = subprocess.PIPE)
    pDisplay.communicate(input = pDot.communicate(content)[0])
    return pDisplay.wait()
    
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
    parser.add_argument("-a", "--all", action = "store_true",
                        help = "Output all function calls, not only calls between "
                        "functions of the module")
    parser.add_argument("--nodeShape", type = str, default = "box",
                        help = "Node shape (default: box)")
    parser.add_argument("--clusters", action = "store_true",
                        help = "Group the functions by their module of origin",
                        default = True)
    parser.add_argument("-q", "--quickView", action = "store_true",
                        help = "Provide a simple display of the dot file through "
                        "ImageMagick and remove the dot file")
    parser.add_argument("-m", "--getMethods", action = "store_true",
                        help = "Also output method calls",
                        default = False)
    return parser

### ** _makeDotFromSrc(filename)

def _makeDotFromSrc(filename, getMethods = False) :
    """Prepare the dot content describing a source file dependency graph

    Args:
        filename (str): Name of the source file

    Returns:
        str: Dot content describing the dependency graph

    """
    parsedSource = astParseFile(filename)
    functionDefs = getFunctionDef(parsedSource)
    functionCalls = extractFunctionCalls(functionDefs)
    importedModules = set([])
    [importedModules.add(x[0]) for x in getImportedModules(parsedSource)]
    [importedModules.add(x[1]) for x in getImportedModules(parsedSource)]
    functionOrigins = getFunctionOrigin(functionCalls, "myModule",
                                        keepOnlyFrom = importedModules)
    dotOptions = {"nodeShape" : "box"}
    dotContent = makeDotFileContent(functionCalls,
                                    funcOrigin = functionOrigins,
                                    dotOptions = dotOptions,
                                    onlyLocal = True)
    return dotContent

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
    dotContent = _makeDotFromSrc(args.inputModule[0])
    if args.quickView :
        viewDotContent(dotContent)
    else :
        stdout.write(dotContent)
