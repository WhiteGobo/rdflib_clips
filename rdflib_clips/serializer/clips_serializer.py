from typing import IO, Optional, TypeVar

import rdflib
from rdflib.graph import Graph
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer
from rdflib.term import BNode, Literal, URIRef
_ruletype = TypeVar("clipsrule")
from typing import Any
import typing as typ
import re
import abc

from .base import clips_rule_base
from .rule import _clips_rule
from .fact import deffacts_construct

_default_rules = [
        _clips_rule,
        ]

class ClipsSerializer(Serializer):
    used_rules: typ.List
    def __init__(self, *args, used_rules:typ.Iterator = None, **kwargs):
        """
        :param used_rules: Use this option to set which type of rules
            are created. If None uses ._default_rules instead
        """
        super().__init__(*args, **kwargs)
        if used_rules is None:
            self.used_rules = list(_default_rules)
        else:
            self.used_rules = list(used_rules)

    def serialize(self,
                  stream: IO[bytes],
                  base: Optional[str] = None,
                  #use_rdf_type = False,
                  #auto_compact = False,
                  #indent = 2,
                  #sort_keys = True,
                  encoding: Optional[str] = "utf-8",
                  axiom_prefix: str = "axiom",
                  serialize_rules: bool = True,
                  serialize_all_axioms: bool = True,
                  used_rules = None,
                  ):
        """Serializer for clips. 
        Supports different output variants. It can currently serialize
        all rules as defrules and all facts as triples. triple classname
        defined by axiom_prefix.

        :param base: defines base for nameresolution. Isnt implemented yet
        :param encoding: defines encoding of output
        :param axiom_prefix: labels :term:`rdf:Statement<Statement>` in the
            resulting clips-file. Triples will get this as Prefix.
        :param serialize_all_axioms: Defines if output should contain
            information about all axioms
        :param serialize_rules: Defines if output should contain information
            about rules within the store
        """
        if used_rules is None:
            used_rules = self.used_rules
        used_axioms = []
        if serialize_rules:
            rulelist = list(self.generate_rules(self.store, used_rules))
            for rule in rulelist:
                stream.write(rule.serialize().encode(encoding))
                stream.write("\n\n".encode(encoding))
                used_axioms.extend(rule.axioms)
        from .. import utils_to_clips as tru
        if serialize_all_axioms:
            #for g in conj_graph:
            filtered = [ax for ax in self.store if ax not in used_axioms]
            factsname = base or "allfacts"
            q = deffacts_construct(factsname, filtered)
            stream.write(q.serialize().encode(encoding))
            #facts = tru.deffacts(factsname, filtered, axiom_prefix)
            #stream.write(facts.encode(encoding))
            stream.write("\n".encode(encoding))

        if axiom_prefix != "axiom":
            raise NotImplementedError()


    def generate_rules(self, infograph,
                       used_rules: typ.List[clips_rule_base] = _default_rules,
                       ) -> typ.Iterator[clips_rule_base]:
        dedicated_axioms = []
        for ruletype in used_rules:
            tmp_rules = []
            #try:
            #    tmp_rules = ruletype.extract_from(infograph)
            #except AttributeError:
            used_axioms = []
            results = infograph.query(ruletype.init_query).bindings
            for result in results:
                result = {str(key): val for key, val in result.items()}
                newrule = ruletype.from_queryresult(infograph, **result)
                tmp_rules.append(newrule)
                if not any(ax in used_axioms for ax in newrule.dedicated_axioms):
                    dedicated_axioms.extend(newrule.dedicated_axioms)
                    yield newrule
