### * Description

# Python module to produce a dependency graph between functions within a module

### * Setup

### ** Import

### ** Built-in modules

import sys
import ast
import argparse

### ** Argument parser

parser = argparse.ArgumentParser(
    description =
    "Produce a dependency graph between functions within a module. The output "
    "is a dot file to be processed with graphviz.")
parser.add_argument(dest = "inputModules", metavar = "MODULE.PY",
                    nargs = "+",
                    help = "One or several Python module files",
                    type = str)
parser.add_argument("-a", "--all", action = "store_true",
                    help = "Output all function calls, not only calls between "
                    "functions of the module")

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

### ** makeDotFileContent(relations, onlyLocal)

def makeDotFileContent(relations, onlyLocal = True) :
    o = ""
    o += "digraph G {\n"
    for caller in relations.keys() :
        for called in relations[caller] :
            if (not onlyLocal) or (called in relations.keys()) :
                o += caller + " -> " + called + ";\n"
    o += "}\n"
    return(o)

### * main(args)

def main(args) :
    print(args.all)
    for f in args.inputModules :
        assert f.endswith(".py")
        parsedSource = astParseFile(f)
        functionDefs = getFunctionDef(parsedSource)
        functionCalls = extractFunctionCalls(functionDefs)
        dotContent = makeDotFileContent(functionCalls, onlyLocal = not args.all)
        with open(f[:-3] + ".graph.dot", "w") as fo :
            fo.write(dotContent)

### * Run

if (__name__ == "__main__") :
    args = parser.parse_args()
    main(args)
