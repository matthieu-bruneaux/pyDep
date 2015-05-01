### * Description

# Test script for pyDep module

### ** Requirements

# sudo pip install nose
# sudo pip install coverage

### ** Usage

# nosetests tests.py
# nosetests tests.py --with-coverage --cover-html --cover-package=ast_parser

### * Setup

### ** Import

import unittest
import sys
sys.path.append("..")
import os
import StringIO
import ast_parser as mod

### ** Parameters

MY_TEST_MODULE = "exampleModule.py"
if not os.path.isfile(MY_TEST_MODULE) :
    MY_TEST_MODULE = os.path.join("tests", MY_TEST_MODULE)

### * Run

### ** class TestArgParser

class TestArgParser(unittest.TestCase) :

### *** setUp and TearDown

    def setUp(self) :
        # We redirect stderr so that there is no error message displayed when
        # we test for parser error message.
        self.stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    def tearDown(self) :
        sys.stderr.close()
        sys.stderr = self.stderr

### *** test_inputFiles

    def test_inputFiles_missing(self) :
        commandLine = []
        with self.assertRaises(SystemExit) :
            mod.parser.parse_args(commandLine)

    def test_inputFiles_one(self) :
        commandLine = ["myMod01.py"]
        result = mod.parser.parse_args(commandLine)
        self.assertEqual(result.inputModules, ["myMod01.py"])
            
    def test_inputFiles_multiple(self) :
        commandLine = ["myMod01.py", "myMod02.py"]
        result = mod.parser.parse_args(commandLine)
        self.assertEqual(result.inputModules, ["myMod01.py", "myMod02.py"])

### *** test_option_all

    def test_option_all_False(self) :
        commandLine = ["myMod01.py"]
        result = mod.parser.parse_args(commandLine)
        self.assertFalse(result.all)

    def test_option_all_True(self) :
        commandLine = ["myMod01.py", "--all"]
        result = mod.parser.parse_args(commandLine)
        self.assertTrue(result.all)

### *** test_option_nodeShape

    def test_option_nodeShape_default(self) :
        commandLine = ["myMod01.py", "--all"]
        result = mod.parser.parse_args(commandLine)
        self.assertEqual(result.nodeShape, "box")

    def test_option_nodeShape_circle(self) :
        commandLine = ["myMod01.py", "--nodeShape", "circle"]
        result = mod.parser.parse_args(commandLine)
        self.assertEqual(result.nodeShape, "circle")

    def test_option_nodeShape_missing(self) :
        commandLine = ["myMod01.py", "--nodeShape"]
        with self.assertRaises(SystemExit) :
            result = mod.parser.parse_args(commandLine)

### ** class TestSourceParsing

class TestSourceParsing(unittest.TestCase) :

### *** setUp and tearDown

    def setUp(self) :
        self.astParsedSource = mod.astParseFile(MY_TEST_MODULE)
        self.functionDef = mod.getFunctionDef(self.astParsedSource)
        self.functionCalls = mod.extractFunctionCalls(self.functionDef)

### *** test_astParseFile

    def test_astParseFile_returnAstModule(self) :
        self.assertEqual(self.astParsedSource.__class__, mod.ast.Module)

    def test_astParseFile_lenModuleBody(self) :
        self.assertEqual(len(self.astParsedSource.body), 9)

### *** test_getFunctionDef

    def test_getFunctionDef_returnClasses(self) :
        classCheck = [x.__class__ == mod.ast.FunctionDef for x in self.functionDef]
        self.assertTrue(all(classCheck))

    def test_getFunctionDef_lenReturn(self) :
        self.assertEqual(len(self.functionDef), 9)

    def test_getFunctionDef_elementName(self) :
        self.assertEqual(self.functionDef[1].name, "sensibleFib")

### *** test_extractFunctionCalls

    def test_extractFunctionCalls_lenReturn(self) :
        self.assertEqual(len(self.functionCalls), 9)

    def test_extractFunctionCalls_typeReturn(self) :
        self.assertEqual(type(self.functionCalls), dict)

    def test_extractFunctionCalls_simpleFunc_calls(self) :
        expected = set([])
        self.assertEqual(self.functionCalls["simpleFunc"], expected)

    def test_extractFunctionCalls_fib_calls(self) :
        expected = set(["type", "fib"])
        self.assertEqual(self.functionCalls["fib"], expected)

    def test_extractFunctionCalls_transcribeDNA_calls(self) :
        expected = set(["validateDNAstring", "makeDNAcomplement"])
        self.assertEqual(self.functionCalls["transcribeDNA"], expected)

### ** class TestDotPreparation

class TestDotPreparation(unittest.TestCase) :

### *** setUp and tearDown

    def setUp(self) :
        relations = {
            "f1" : set([]),
            "f2" : set(["f1", "len"]),
            "f3" : set(["f3"])
            }
        self.relations = relations
        self.dotContentLocal = mod.makeDotFileContent(relations, onlyLocal = True)
        self.dotContentGlobal = mod.makeDotFileContent(relations, onlyLocal = False)
        self.dotContentLocalBox = mod.makeDotFileContent(relations,
                                                         dotOptions = {"nodeShape" : "circle"},
                                                         onlyLocal = True)

### *** test_getDotOptions

    def test_getDotOptions_nodeShape(self) :
        class Args :
            pass
        args = Args()
        args.nodeShape = "heartShaped"
        result = mod.getDotOptions(args)
        expected = {"nodeShape" : "heartShaped"}
        self.assertDictEqual(result, expected)

### *** test_makeDotFileContent

    def test_makeDotFileContent_local(self) :
        expected = "digraph G {\nf2 -> f1;\nf3 -> f3;\n}\n"
        self.assertEqual(self.dotContentLocal, expected)

    def test_makeDotFileContent_global(self) :
        expected = "digraph G {\nf2 -> f1;\nf2 -> len;\nf3 -> f3;\n}\n"
        self.assertEqual(self.dotContentGlobal, expected)

    def test_makeDotFileContent_nodeShape(self) :
        expected = "digraph G {\nnode[shape=circle];\nf2 -> f1;\nf3 -> f3;\n}\n"
        self.assertEqual(self.dotContentLocalBox, expected)

### ** class TestMain

class TestMain(unittest.TestCase) :

### *** setUp and TearDown

    def setUp(self) :
        # Remove pre-existing output file, if any
        output_file = MY_TEST_MODULE[:-3] + ".graph.dot"
        if os.path.isfile(output_file) :
            os.remove(output_file)
        # Load expected files content
        localGraphFile = os.path.join(os.path.dirname(MY_TEST_MODULE),
                                      "expectedFiles",
                                      os.path.basename(MY_TEST_MODULE[:-3]) +
                                      ".local.graph.dot")
        globalGraphFile = os.path.join(os.path.dirname(MY_TEST_MODULE),
                                      "expectedFiles",
                                       os.path.basename(MY_TEST_MODULE[:-3])
                                       + ".global.graph.dot")
        with open(localGraphFile, "r") as fi :
            self.localGraphContent = fi.read()
        with open(globalGraphFile, "r") as fi :
            self.globalGraphContent = fi.read()
            
    def tearDown(self) :
        output_file = MY_TEST_MODULE[:-3] + ".graph.dot"
        if os.path.isfile(output_file) :
            os.remove(output_file)

### *** test_main

    def test_main_local_fileExists(self) :
        args = [MY_TEST_MODULE]
        mod.main(mod.parser.parse_args(args))
        self.assertTrue(os.path.isfile(MY_TEST_MODULE[:-3] + ".graph.dot"))

    def test_main_local_fileContent(self) :
        args = [MY_TEST_MODULE]
        mod.main(mod.parser.parse_args(args))
        with open(MY_TEST_MODULE[:-3] + ".graph.dot", "r") as fi :
            result = fi.read()
        self.assertEqual(result, self.localGraphContent)

    def test_main_global_fileExists(self) :
        args = [MY_TEST_MODULE, "--all"]
        mod.main(mod.parser.parse_args(args))
        self.assertTrue(os.path.isfile(MY_TEST_MODULE[:-3] + ".graph.dot"))

    def test_main_global_fileContent(self) :
        args = [MY_TEST_MODULE, "--all"]
        mod.main(mod.parser.parse_args(args))
        with open(MY_TEST_MODULE[:-3] + ".graph.dot", "r") as fi :
            result = fi.read()
        self.assertEqual(result, self.globalGraphContent)
