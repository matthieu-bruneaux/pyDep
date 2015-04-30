### * Description

# Makefile for the pyDep mdule

### * Variables

PYTHON=python
MYSCRIPT_NOPY=ast_parser
MYSCRIPT=$(MYSCRIPT_NOPY).py
EXAMPLE_MOD_NOPY=tests/exampleModule

### * Help

help:
	@echo "Makefile for the pyDep module                                   "
	@echo "Type: \"make <target>\" where <target> is one of the following :  "
	@echo "  examples            Run basic examples                        "
	@echo "  clean               Clean the example output files            "

### * Main targets

examples:
	$(PYTHON) $(MYSCRIPT) $(MYSCRIPT)
	dot -Tpdf $(MYSCRIPT_NOPY).graph.dot -o $(MYSCRIPT_NOPY).graph.pdf
	$(PYTHON) $(MYSCRIPT) $(EXAMPLE_MOD_NOPY).py
	dot -Tpdf $(EXAMPLE_MOD_NOPY).graph.dot -o $(EXAMPLE_MOD_NOPY).graph.pdf

clean:
	rm -f $(MYSCRIPT_NOPY).graph.dot $(MYSCRIPT_NOPY).graph.pdf
	rm -f $(EXAMPLE_MOD_NOPY).graph.dot $(EXAMPLE_MOD_NOPY).graph.pdf
