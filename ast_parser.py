import ast

fileName = "process_aln.py"

with open(fileName, "r") as fi :
    source = fi.read()

a = ast.parse(source)

# Get only function definitions

b = [x for x in a.body if x.__class__ == ast.FunctionDef]

relations = dict()

for func in b :
    print(func.name)
    calls = [x for x in ast.walk(func) if x.__class__ == ast.Call]
    print([x.func.id for x in calls if x.func.__class__ == ast.Name])
    print([x.func.attr for x in calls if x.func.__class__ == ast.Attribute])
    calledFunctions = [x.func.id for x in calls if x.func.__class__ == ast.Name]
    for call in calledFunctions :
        relations[func.name] = relations.get(func.name, set([]))
        relations[func.name].add(call)
    print("\n")

def makeDotFile(relations, onlyLocal = True) :
    o = ""
    o += "digraph G {\n"
    for caller in relations.keys() :
        for called in relations[caller] :
            if (not onlyLocal) or (called in relations.keys()) :
                o += caller + " -> " + called + ";\n"
    o += "}\n"
    return(o)

with open("dependencies.dot", "w") as fo :
    fo.write(makeDotFile(relations))
