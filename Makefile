.PHONY: test
test:
	#python -m unittest
	python -m unittest

build: rdf_ruleml/__init__.py rdf_ruleml/example_parser.py rdf_ruleml/rdflib_parser.py rdf_ruleml/ruleml_classes.py
	python -m build

.PHONY: test_from_clips
test_from_clips:
	python -m tests.test_clips_to_swrl_parser

.PHONY: test_rdflib_plugin
test_rdflib_plugin:
	python -m tests.test_rdflib_plugin

.PHONY: test_logicgraph
test_logicgraph: tests/test_rdflogic.py
	python -m tests.test_rdflogic
