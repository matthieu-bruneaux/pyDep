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
	@echo "  test                Run tests                                 "
	@echo "  clean               Clean everything                          "

### * Main targets

### ** examples
examples:
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT)
	dot -Tpdf $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).graph.pdf
	$(PYTHON) $(MYSCRIPT) $(EXAMPLE_MOD_NOPY).py
	dot -Tpdf $(EXAMPLE_MOD_NOPY).graph.dot -o $(EXAMPLE_MOD_NOPY).graph.pdf

### ** test
test:
	nosetests $(TEST_SCRIPT) --with-coverage --cover-package=ast_parser --cover-html
	@echo "\nThe coverage results are accessible from cover/index.html"

### ** clean
clean:
	# pyc files
	rm -f *.pyc tests/*.pyc
	# Coverage files
	rm -f .coverage
	rm -fr cover
	# Example files
	rm -f $(MYSCRIPT_NOPY).graph.dot $(MYSCRIPT_NOPY).graph.pdf
	rm -f $(EXAMPLE_MOD_NOPY).graph.dot $(EXAMPLE_MOD_NOPY).graph.pdf
