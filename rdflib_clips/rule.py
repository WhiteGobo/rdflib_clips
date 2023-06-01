import abc
import re
import rdflib
from .shared import ordered_symbols, name2iri
from . import shared

_RDF = rdflib.RDF
from .shared import _RDFS, _CL2RDF
_swrl = rdflib.Namespace("http://www.w3.org/2003/11/swrl#")

### abstract classes

class rdf_element(abc.ABC):
    @abc.abstractmethod
    def as_rdfgraph(self, mapping, assigned_basenode=None)\
            -> rdflib.Graph:
        """Transforms this object to a rdfgraph"""
        ...

### helper methods


### Implementataion

class _rule(rdf_element):
    def __init__(self, name, conditionals, actions,
                 comment=None, declaration=None):
        if any(isinstance(act, (str, int, float)) for act in actions):
            raise NotImplementedError("actions only support functions yet")
        self.name = name
        self.conditionals = conditionals
        self.actions = actions
        self.comment = None
        self.declaration = None

    def __repr__(self):
        if self.comment:
            return f"<rule:{self.name}:{comment}>"
        else:
            return f"<rule:{self.name}>"

    def as_rdfgraph(self, mapping,
                    assigned_basenode:rdflib.IdentifiedNode=None,
                    ):
        if assigned_basenode is None:
            assigned_basenode = rdflib.BNode()
        g = rdflib.Graph()
        g.add((assigned_basenode, _RDF.type, _swrl.Imp))
        identifier = name2iri(self.name, mapping)
        g.add((assigned_basenode, _RDFS.label, identifier))
        if self.comment is not None:
            raise NotImplementedError()
        if self.declaration is not None:
            raise NotImplementedError()
        conditionals = rdflib.Seq(g, rdflib.BNode())
        g.add((assigned_basenode, _swrl.body, conditionals.uri))
        for x in self.conditionals:
            tmp_id = rdflib.BNode()
            conditionals.append(tmp_id)
            for ax in x.as_rdfgraph(mapping=mapping,
                                    assigned_basenode=tmp_id):
                g.add(ax)
        actions = rdflib.Seq(g, rdflib.BNode())
        g.add((assigned_basenode, _swrl.head, actions.uri))
        for x in self.actions:
            tmp_id = rdflib.BNode()
            actions.append(tmp_id)
            for ax in x.as_rdfgraph(mapping=mapping,
                                    assigned_basenode=tmp_id):
                g.add(ax)
        return g


class variable(shared.variable):
    """Container for variables"""
    def __init__(self, name):
        self.name = name
    def as_iri(self, base):
        iri = rdflib.URIRef(base) + self.name
        return f"<{iri}>"
    def __repr__(self):
        return f"<var:{self.name}>"

class ordered_pattern(ordered_symbols):
    """Superclass to facts and single_conditionals.
    Might the same as LHS_slot
    Simple fact, so something in the form of (duck dough 123)
    """
    def _as_rdfgraph_classification(self, mapping, assigned_basenode,
                                    symbols=None):
        g = rdflib.Graph()
        if symbols is None:
            symbols = self.symbols
        var, cls = (name2iri(x, mapping) for x in symbols)
        g.add((assigned_basenode, _RDF.type, _swrl.ClassAtom))
        g.add((assigned_basenode, _swrl.argument1, var))
        g.add((assigned_basenode, _swrl.ClassAtom, cls))
        for x, name in zip(symbols, (var, cls)):
            if isinstance(x, variable):
                g.add((name, _RDF.type, _swrl.Variable))
        return g

    def _as_rdfgraph_simpleaxiom(self, mapping, assigned_basenode,
                                 symbols=None):
        g = rdflib.Graph()
        if symbols is None:
            symbols = self.symbols
        subject, predicate, _object = (name2iri(x, mapping) for x in symbols)
        g.add((assigned_basenode, _RDF.type, _swrl.IndividualPropertyAtom))
        g.add((assigned_basenode, _swrl.argument1, subject))
        g.add((assigned_basenode, _swrl.propertyPredicate, predicate))
        g.add((assigned_basenode, _swrl.argument2, _object))
        for x, name in zip(symbols, (subject, predicate, _object)):
            if isinstance(x, variable):
                g.add((name, _RDF.type, _swrl.Variable))
        return g


    def __repr__(self):
        return f"<ordered pattern:{self.firstsymbol}:{self.symbols}>"

class fact(ordered_pattern):
    """Simple fact like asserted by (assert (myfact ...)).
    """
    pass

class conditional:
    """All conditionals for LHS of a rule"""

class CE_ordered_pattern(ordered_pattern, conditional):
    """All conditionals, that can be mapped unto facts.
    E.g. (duck ?name thick|slim)
    """
    def __repr__(self):
        return f"<CE:ordered pattern:{self.firstsymbol}:{self.symbols}>"


class _function_call:
    """Container for functions"""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"<function:{self.name}:{self.args}>"

    def __iter__(self):
        yield self.name
        for x in self.args:
            yield x

    def _as_rdf_assert(self, mapping, assigned_basenode,
                       statement: "_function_call"):
        """Function for assert
        :type statement: _function_call
        """
        return ordered_pattern(*statement).as_rdfgraph(mapping,
                                                       assigned_basenode)

    def as_rdfgraph(self, mapping, assigned_basenode):
        if self.name == "assert":
            return self._as_rdf_assert(mapping, assigned_basenode, *self.args)
        raise NotImplementedError("cant create rdfgraph from function with"
                                  f"name {self.name}")


class clips_container:
    def __init__(self, *constructs):
        self.constructs = constructs

    def as_rdfgraph(self, mapping, assigned_basenode=None):
        g = rdflib.Graph()
        for tmpg in self.constructs:
            for ax in tmpg.as_rdfgraph(mapping=mapping):
                g.add(ax)
        return g
