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
import StringIO
import ast_parser as mod

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
