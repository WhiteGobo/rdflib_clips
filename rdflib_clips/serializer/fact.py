from . import base
from ..shared import _RDFS, _RDF
import rdflib

import typing as typ

class deffacts_construct:
    name: str
    facts: list[base.fact_base]
    def __init__(self, name, axioms):
        self.name = name
        self.facts = []
        for subj, pred, obj in axioms:
            if pred == _RDF.type:
                self.facts.append(class_fact(obj, subj))
            else:
                self.facts.append(simple_fact(subj, pred, obj))

    def serialize(self):
        facts = "\n".join("    %s" % f.serialize() for f in self.facts)
        return f"(deffacts {self.name}\n{facts}\n)"

class class_fact(base.fact_base):
    subject: typ.Any
    classtype: typ.Any
    def __init__(self, classtype, subject):
        self.subject = subject
        self.classtype = classtype
    def serialize(self):
        subj, clstype = (f"<{x}>" if isinstance(x, rdflib.URIRef) else x
                           for x in (self.subject, self.classtype))
        return f"(class {clstype} {subj})"

class simple_fact(base.fact_base):
    def __init__(self, subj, pred, obj):
        self.subj = subj
        self.pred = pred
        self.obj = obj
    def serialize(self):
        subj, pred, obj = (f"<{x}>" if isinstance(x, rdflib.URIRef) else x
                           for x in (self.subj, self.pred, self.obj))
        return f"(axiom {subj} {pred} {obj})"
