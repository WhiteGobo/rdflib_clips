import abc
import re
import rdflib
import typing as typ
import logging
logger = logging.getLogger(__name__)

_RDF = rdflib.RDF
_CL2RDF = rdflib.Namespace("http://example.com/")
try:
    rdflib.RDFS.Statement
    _RDFS = rdflib.RDFS
except AttributeError:
    _RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
_swrl = rdflib.Namespace("http://www.w3.org/2003/11/swrl#")


class iri_object(abc.ABC):
    @abc.abstractmethod
    def as_iri(self, base: str) -> rdflib.URIRef:
        ...

_re_iri = re.compile("<(.*)>")
_re_shortened = re.compile("(.*):([^/].*)")
def name2iri(name: typ.Union[str, int, float, iri_object], mapping: dict):
    """Returns given name as uri. If its not a primitive extracts an id
    via as_iri. Afterwards the name or the id will be translated via mapping
    to a :term:`IRI`
    """
    try:
        _id = name.as_iri(mapping[""])
    except AttributeError:
        _id = name
    try:
        return mapping[_id]
    except KeyError:
        pass
    #This also works for rdflib.IdentifiedNode, .BNode and .URIRef
    assert isinstance(_id, (str, int, float))
    match = _re_iri.match(_id)
    if match:
        return rdflib.URIRef(match.groups()[0])
    match = _re_shortened.match(_id)
    if match:
        prefix, suffix = match.groups()
        return mapping[prefix] + suffix
    try:
        base = mapping[""]
        return base + _id
    except KeyError as err:
        raise Exception(f"Cant transform {name}, when no base "
                        "(mapping['']) is given.") from err

class variable(iri_object):
    """Superclass to all variables"""

class ordered_symbols(abc.ABC):
    """Superclass to everything that is expressed via ordered symbols 
    or elements.

    examples:
        (duck called dough)
        (duck called ?name)
        (duck called|labeld dough)
    """
    def __init__(self, firstsymbol, *symbols):
        self.firstsymbol = firstsymbol
        self.symbols = symbols

    def __iter__(self):
        yield self.firstsymbol
        for x in self.symbols:
            yield self.symbols

    def as_rdfgraph(self, mapping, assigned_basenode = None):
        """
        Uses :term:`cl2rdf:axiom`, :term:`cl2rdf:type`
        """
        q = name2iri(self.firstsymbol, mapping)
        extra_args = {}
        if assigned_basenode is not None:
            extra_args["assigned_basenode"] = assigned_basenode
        if q in (_RDFS.Statement, _CL2RDF.axiom):
            return self._as_rdfgraph_simpleaxiom(mapping, **extra_args)
        elif q in (_RDF.type, _CL2RDF.type):
            return self._as_rdfgraph_classification(mapping, **extra_args)
        elif len(self.symbols) == 3:
            logger.debug(f"Guessing {self} is meant as axiom.")
            return self._as_rdfgraph_simpleaxiom(mapping, **extra_args)
        elif len(self.symbols) == 2:
            logger.debug(f"Guessing {self} is meant as classification.")
            return self._as_rdfgraph_classification(mapping, **extra_args)
        elif len(self.symbols) == 1:
            logger.debug(f"Guessing {self} is meant as classification.")
            return self._as_rdfgraph_classification(mapping,\
                    symbols=(self.name, self.symbols[0]), **extra_args)
        raise NotImplementedError(q, f"number of args: {len(self.symbols)}", self)

    @abc.abstractmethod
    def _as_rdfgraph_classification(self, mapping, assigned_basenode,
                                    symbols=None):
        ...

    @abc.abstractmethod
    def _as_rdfgraph_simpleaxiom(self, mapping, assigned_basenode,
                                 symbols=None):
        ...

    def __repr__(self):
        name = type(self).__name__
        return f"<{name}:{self.firstsymbol}:{self.symbols}>"

