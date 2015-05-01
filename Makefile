### * Description

# Makefile for the pyDep mdule

### * Variables

### ** Main script
PYTHON=python
MYSCRIPT_NOPY=ast_parser
MYSCRIPT=$(MYSCRIPT_NOPY).py

### ** Tests
TEST_DIR=tests
TEST_SCRIPT=$(TEST_DIR)/tests.py

### ** Examples
EXAMPLE_MOD_NOPY=$(TEST_DIR)/exampleModule

### * Help

help:
	@echo "Makefile for the pyDep module                                   "
	@echo "Type: \"make <target>\" where <target> is one of the following :  "
	@echo "  examples            Run basic examples                        "
	@echo "  doc_examples        Run doc examples                          "
	@echo "  test                Run tests                                 "
	@echo "  clean               Clean everything                          "
	@echo "  doc_clean           Clean doc examples                        "

### * Main targets

### ** examples
examples:
	# Local graph of the pyDep module
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT)
	dot -Tpdf $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).local.graph.pdf
	# Global graph of the pyDep module
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT) --all
	dot -Tpdf $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).global.graph.pdf
	# Local graph of simple example module
	$(PYTHON) $(MYSCRIPT) $(EXAMPLE_MOD_NOPY).py
	dot -Tpdf $(EXAMPLE_MOD_NOPY).graph.dot -o $(EXAMPLE_MOD_NOPY).graph.pdf

### ** doc_examples
doc_examples: doc_clean
	# Local graph of the pyDep module
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT)
	dot -Tpng $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).local.graph.png
	mv $(MYSCRIPT_NOPY).graph.dot doc_examples/$(MYSCRIPT_NOPY).local.graph.dot
	# Global graph of the pyDep module
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT) --all
	dot -Tpng $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).global.graph.png
	mv $(MYSCRIPT_NOPY).graph.dot doc_examples/$(MYSCRIPT_NOPY).global.graph.dot
	# Local graph of simple example module
	$(PYTHON) $(MYSCRIPT) $(EXAMPLE_MOD_NOPY).py
	dot -Tpng $(EXAMPLE_MOD_NOPY).graph.dot -o $(EXAMPLE_MOD_NOPY).graph.png
	mv $(EXAMPLE_MOD_NOPY).graph.dot doc_examples/
	# Move the output to doc_examples
	mv $(MYSCRIPT_NOPY).local.graph.png $(MYSCRIPT_NOPY).global.graph.png \
	  $(EXAMPLE_MOD_NOPY).graph.png doc_examples/

### ** test
test:
	nosetests $(TEST_SCRIPT) --with-coverage --cover-package=ast_parser --cover-html
	@echo "\nThe coverage results are accessible from cover/index.html"

tests: test

### ** clean
clean: doc_clean
	# pyc files
	rm -f *.pyc tests/*.pyc
	# Coverage files
	rm -f .coverage
	rm -fr cover
	# Example files
	rm -f $(MYSCRIPT_NOPY).graph.dot
	rm -f $(MYSCRIPT_NOPY).local.graph.pdf
	rm -f $(MYSCRIPT_NOPY).global.graph.pdf
	rm -f $(EXAMPLE_MOD_NOPY).graph.dot
	rm -f $(EXAMPLE_MOD_NOPY).graph.pdf

doc_clean:
	rm -f doc_examples/*
