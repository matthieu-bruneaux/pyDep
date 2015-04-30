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

### ** class(TestArgParser)

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

    def test_all_option_False(self) :
        commandLine = ["myMod01.py"]
        result = mod.parser.parse_args(commandLine)
        self.assertFalse(result.all)

    def test_all_option_True(self) :
        commandLine = ["myMod01.py", "--all"]
        result = mod.parser.parse_args(commandLine)
        self.assertTrue(result.all)

### ** class(TestSourceParsing)

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
