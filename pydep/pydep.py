### * Description

# Python module to produce a dependency graph between functions within a module

### * Setup

### ** Import

### ** Built-in modules

import sys
import os
import ast
import argparse
import subprocess

### ** Argument parser

parser = argparse.ArgumentParser(
    description =
    "Produce a dependency graph between functions within a module. The output "
    "is a dot file to be processed with graphviz.",
    epilog =
    "For more information about the node options, please refer to the Dot "
    "documentation (add url here).")
parser.add_argument(dest = "inputModules", metavar = "MODULE.PY",
                    nargs = "+",
                    help = "One or several Python module files",
                    type = str)
parser.add_argument("-a", "--all", action = "store_true",
                    help = "Output all function calls, not only calls between "
                    "functions of the module")
parser.add_argument("--nodeShape", type = str, default = "box",
                    help = "Node shape (default: box)")
parser.add_argument("--clusters", action = "store_true",
                    help = "Group the functions by their module of origin")
parser.add_argument("-q", "--quickView", action = "store_true",
                    help = "Provide a simple display of the dot file through "
                    "ImageMagick and remove the dot file")

### * Functions

### ** astParseFile(sourceFileName)

def astParseFile(sourceFileName) :
    with open(sourceFileName, "r") as fi :
        source = fi.read()
    return(ast.parse(source))

### ** getFunctionDef(astParsedSource)

def getFunctionDef(astParsedSource) :
    return([x for x in astParsedSource.body if x.__class__ == ast.FunctionDef])

### ** extractFunctionCalls(functionDefs)

def extractFunctionCalls(functionDefs) :
    calls = dict()
    for func in functionDefs :
        calls[func.name] = calls.get(func.name, set([]))
        callsByFunc = [x for x in ast.walk(func)
                       if x.__class__ == ast.Call]
        calledFunctions = [x.func.id for x in callsByFunc
                           if x.func.__class__ == ast.Name]
        # calledMethods = [x.func.attr for x in callsByFunc
        #                  if x.func.__class__ == ast.Attribute]
        for call in calledFunctions :
            calls[func.name].add(call)
    return calls

### ** getFunctionOrigin(functionCalls, moduleName)

def getFunctionOrigin(functionCalls, moduleName) :
    origins = dict()
    origins["built-in"] = set([])
    origins[moduleName] = set([])
    allFunctions = functionCalls.keys()
    for x in functionCalls.values() :
        allFunctions += list(x)
    for func in allFunctions :
        if func in functionCalls.keys() :
            origins[moduleName].add(func)
        else :
            origins["built-in"].add(func)
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
            for element in subgraphGroups[cluster] :
                o += element + ";\n"
            o += "}\n"
    return o
        
### ** makeDotFileContent(relations, onlyLocal)

def makeDotFileContent(relations, funcOrigin = None, dotOptions = dict(),
                       onlyLocal = True) :
    o = ""
    o += "digraph G {\n"
    if "nodeShape" in dotOptions.keys() :
        o += "node[shape=" + dotOptions["nodeShape"] + "];\n"
    if not funcOrigin is None :
        # Write subgraphs
        o += writeDotSubgraphs(funcOrigin)
    for caller in relations.keys() :
        for called in relations[caller] :
            if (not onlyLocal) or (called in relations.keys()) :
                o += caller + " -> " + called + ";\n"
    o += "}\n"
    return(o)

### ** viewDotFile(inputFile)

def viewDotFile(inputFile) :
    commandLineDot = ["dot", "-Tpng", inputFile]
    pDot = subprocess.Popen(commandLineDot, stdout = subprocess.PIPE)
    commandLineDisplay = ["display", "-"]
    pDisplay = subprocess.Popen(commandLineDisplay, stdin = subprocess.PIPE)
    pDisplay.communicate(input = pDot.communicate()[0])
    return pDisplay.wait()
    
### * main()

def main(args = None) :
    if args is None :
        args = parser.parse_args()
    for f in args.inputModules :
        assert f.endswith(".py")
        parsedSource = astParseFile(f)
        functionDefs = getFunctionDef(parsedSource)
        functionCalls = extractFunctionCalls(functionDefs)
        if (args.clusters) :
            functionOrigins = getFunctionOrigin(functionCalls, "myModule")
        else :
            functionOrigins = None
        dotOptions = getDotOptions(args)
        dotContent = makeDotFileContent(functionCalls,
                                        funcOrigin = functionOrigins,
                                        dotOptions = dotOptions,
                                        onlyLocal = not args.all)
        with open(os.path.basename(f[:-3]) + ".graph.dot", "w") as fo :
            fo.write(dotContent)
    if args.quickView :
        viewDotFile(os.path.basename(f[:-3]) + ".graph.dot")
        os.remove(os.path.basename(f[:-3]) + ".graph.dot")

### * run

if (__name__ == "__main__") :
    main()
