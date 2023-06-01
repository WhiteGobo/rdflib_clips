from .rule import rdf_element
from .shared import ordered_symbols, name2iri
import rdflib

from rdflib import RDF as _RDF
from .shared import _RDFS
_swrl = rdflib.Namespace("http://www.w3.org/2003/11/swrl#")

class _deffacts(rdf_element):
    def __init__(self, name, facts, comment=None):
        self.name = name
        self.facts = facts
        self.comment = comment

    def as_rdfgraph(self, mapping, assigned_basenode=None, store=None):
        if assigned_basenode is None:
            identifier = name2iri(self.name, mapping)
        else:
            identifier = assigned_basenode
            logger.debug("ignore deffacts-name and use given "
                         "assigned-basenode instead")
        extraargs = {}
        if store is not None:
            extraargs["store"] = store
        g = rdflib.Graph(identifier=identifier, **extraargs)
        for f in self.facts:
            try:
                for ax in f.as_rdfgraph(mapping):
                    g.add(ax)
            except TypeError as err:
                raise Exception(f"Something went wrong with object {f}.\n"
                                "object type: {type(f)}"
                                ) from err
        return g

class simple_fact(ordered_symbols):
    def _as_rdfgraph_classification(self, mapping, symbols=None):
        g = rdflib.Graph()
        if symbols is None:
            symbols = self.symbols
        cls, var = (name2iri(x, mapping) for x in symbols)
        g.add((var, _RDF.type, cls))
        return g

    def _as_rdfgraph_simpleaxiom(self, mapping, symbols=None):
        g = rdflib.Graph()
        if symbols is None:
            symbols = self.symbols
        g.add(name2iri(x, mapping) for x in symbols)
        return g
