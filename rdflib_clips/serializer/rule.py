from .base import clips_rule_base
import rdflib

import abc
import typing as typ
import re
from typing import Any
_ruletype = typ.TypeVar("clipsrule")

SWRL = rdflib.Namespace("http://www.w3.org/2003/11/swrl#")
from ..shared import _RDFS, _RDF
_SWRL = rdflib.Namespace("http://www.w3.org/2003/11/swrl#")


class atom(abc.ABC):
    """Baseclass for every possible swrlatom"""
    used_vars: dict[rdflib.IdentifiedNode]
    implied_axioms: typ.Iterable["axiom"]
    """A list of all axioms which are implied by existence of this atom"""

    @abc.abstractmethod
    def serialize(self) -> str:
        ...

    def _serialize_iri(self, iri: rdflib.IdentifiedNode) -> str:
        """Common method to serialize a single iri"""
        try:
            return self.used_vars[iri]
        except KeyError:
            pass
        return f"<{iri}>"

class individual_property_atom(atom):
    def __init__(self, atom_id, property_to_object: dict,
                 used_vars: dict[rdflib.IdentifiedNode]):
        """
        :TODO: (self.prop, _RDF.type, _RDF.Property) doesnt seems to
            be the correct implied axiom
        """
        assert property_to_object.keys()\
                == {_RDF.type, _SWRL.propertyPredicate, _SWRL.argument1, _SWRL.argument2}
        self.prop = property_to_object[_SWRL.propertyPredicate]
        self.subj = property_to_object[_SWRL.argument1]
        self.obj = property_to_object[_SWRL.argument2]
        self.used_vars = {x: "?%s" % used_vars[x] for x in used_vars}
        self.implied_axioms = [
                (atom_id, _SWRL.propertyPredicate, self.prop),
                (atom_id, _SWRL.argument1, self.subj),
                (atom_id, _SWRL.argument2, self.obj),
                (self.prop, _RDF.type, _RDF.Property),
                ]
        self.implied_axioms.extend(
                (x, _RDF.type, _SWRL.Variable) for x in used_vars)

    def __repr__(self):
        name = type(self).__name__
        return f"<{name}:<{self.subj}>:<{self.prop}>:<{self.obj}>>"


class individual_property_atom_lhs(individual_property_atom):
    def serialize(self):
        prop, subj, obj = (self._serialize_iri(x)
                           for x in (self.prop, self.subj, self.obj))
        return f"(axiom {subj} {prop} {obj})"

class individual_property_atom_rhs(individual_property_atom):
    def serialize(self):
        prop, subj, obj = (self._serialize_iri(x)
                           for x in (self.prop, self.subj, self.obj))
        return f"(assert (axiom {subj} {prop} {obj}))"

class class_atom(atom):
    def __init__(self, atom_id, property_to_object: dict,
                 used_vars: dict[rdflib.IdentifiedNode]):
        """
        :TODO: (self.predicate, _RDF.type, _RDFS.Class) doesnt seem to 
            be the correct implied axiom
        """
        assert property_to_object.keys()\
                == {_RDF.type, _SWRL.classPredicate, _SWRL.argument1}
        self.predicate = property_to_object[_SWRL.classPredicate]
        self.target = property_to_object[_SWRL.argument1]
        self.used_vars = {x: "?%s" % used_vars[x] for x in used_vars}
        self.implied_axioms = [
                (atom_id, _SWRL.classPredicate, self.predicate),
                (atom_id, _SWRL.argument1, self.target),
                (self.predicate, _RDF.type, _RDFS.Class),
                ]
        self.implied_axioms.extend(
                (x, _RDF.type, _SWRL.Variable) for x in used_vars)

    def __repr__(self):
        name = type(self).__name__
        return f"<{name}:<{self.predicate}>:<{self.target}>>"


class class_atom_lhs(class_atom):
    def serialize(self):
        pred, target = (self._serialize_iri(x)
                        for x in (self.predicate, self.target))
        return f"(class {pred} {target})"


class class_atom_rhs(class_atom):
    def serialize(self):
        pred, target = (self._serialize_iri(x)
                        for x in (self.predicate, self.target))
        return f"(assert (class {pred} {target}))"


class _clips_rule(clips_rule_base):
    init_query = """
            SELECT ?ruleid ?name ?comment
            WHERE {
                ?ruleid a swrl:Imp.
                OPTIONAL {?ruleid rdfs:label ?rulename.}
                OPTIONAL {?ruleid rdfs:comment ?comment.}
            }"""
    name: str
    lhs: list[atom]
    rhs: list[atom]
    comment: Any
    axioms: typ.List["axiom"]
    """all used axioms by this rule"""
    def __init__(self, name, lhs, rhs, axioms, comment: str = None,
                 axiom_prefix: typ.Match[str] = "axiom",
                 ):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs
        self.comment = comment
        assert re.match("^[a-zA-Z][a-zA-Z0-9]*$", axiom_prefix), axiom_prefix
        self.axiom_prefix = axiom_prefix
        self.dedicated_axioms = []
        self.axioms = axioms

    @classmethod
    def generate_lhs_atom(cls, atom_id, predicate_object,
                          is_var: list[rdflib.IdentifiedNode]):
        po = list(predicate_object)
        assert len(set(p for p, o in po)) == len(po), "Syntax wrong"
        q = dict(po)
        if q.get(_RDF.type) == _SWRL.IndividualPropertyAtom:
            return individual_property_atom_lhs(atom_id, q, is_var)
        elif q.get(_RDF.type) == _SWRL.ClassAtom:
            return class_atom_lhs(atom_id, q, is_var)
        else:
            raise NotImplementedError(q[_RDF.type],
                                      "Cant decipher this atom type")

    @classmethod
    def generate_rhs_atom(cls, atom_id, predicate_object,
                          is_var: list[rdflib.IdentifiedNode]):
        po = list(predicate_object)
        assert len(set(p for p, o in po)) == len(po), "Syntax wrong"
        q = dict(po)
        if q[_RDF.type] == _SWRL.IndividualPropertyAtom:
            return individual_property_atom_rhs(atom_id, q, is_var)
        elif q[_RDF.type] == _SWRL.ClassAtom:
            return class_atom_rhs(atom_id, q, is_var)
        else:
            raise NotImplementedError(q[_RDF.type],
                                      "Cant decipher this atom type")



    @classmethod
    def from_queryresult(cls: _ruletype, infograph: rdflib.Graph,
                      ruleid) -> _ruletype:
        assert len(list(infograph.objects(ruleid, _RDFS.label))) <= 1
        assert len(list(infograph.objects(ruleid, _RDFS.comment))) <= 1

        data = {}
        all_axioms = []
        all_axioms.append((ruleid, _RDF.type, _SWRL.Imp))
        try:
            name, = infograph.objects(ruleid, _RDFS.label)
            all_axioms.append((ruleid, _RDFS.label, name))
        except ValueError as err:
            raise SyntaxError("Exactly one name per rule is expected") from err
        comments = list(infograph.objects(ruleid, _RDFS.comment))
        if len(comments) == 1:
            data["comment"], = comments
            all_axioms.extend((ruleid, _RDFS.comment, c) for c in comments)
        elif len(comments) > 1:
            raise NotImplementedError("currently only 1 comment per rule.")

        ax_lhs, = infograph.triples((ruleid, _SWRL.body, None))
        ax_rhs, = infograph.triples((ruleid, _SWRL.head, None))
        lhs_id = ax_lhs[2]
        rhs_id = ax_rhs[2]
        all_axioms.append(ax_lhs)
        all_axioms.append(ax_rhs)
        lhs, tmp_axioms = _get_collection(infograph, lhs_id)
        all_axioms.extend(tmp_axioms)
        for n in lhs:
            all_axioms.extend(infograph.triples((n, None, None)))
        rhs, tmp_axioms = _get_collection(infograph, rhs_id)
        all_axioms.extend(tmp_axioms)
        for n in rhs:
            all_axioms.extend(infograph.triples((n, None, None)))

        data["lhs"] = []
        i = 0
        is_var = {}
        for subject in lhs:
            pred_obj = tuple(infograph.predicate_objects(subject))
            for _, obj in pred_obj:
                if obj in is_var:
                    continue
                try:
                    ax = infograph.triples((obj, _RDF.type, _SWRL.Variable))\
                            .__next__()
                    all_axioms.extend(ax)
                    is_var[obj] = f"var{i}"
                    i += 1
                except StopIteration:
                    pass
            atom = cls.generate_lhs_atom(subject, pred_obj, is_var)
            all_axioms.extend(atom.implied_axioms)
            data["lhs"].append(atom)
        data["rhs"] = []
        for subject in rhs:
            pred_obj = tuple(infograph.predicate_objects(subject))
            for _, obj in pred_obj:
                if obj in is_var:
                    continue
                elif (obj, _RDF.type, _SWRL.Variable) in infograph:
                    raise SyntaxError("Not known Variable on the right-hand "
                                      "side of a rule.", obj)
            atom = cls.generate_rhs_atom(subject, pred_obj, is_var)
            all_axioms.extend(atom.implied_axioms)
            data["rhs"].append(atom)
        return cls(name, axioms=all_axioms, **data)

    def serialize(self):
        lhs = " ".join(atom.serialize() for atom in self.lhs)
        rhs = " ".join(atom.serialize() for atom in self.rhs)
        return f"(defrule {self.name} {lhs} => {rhs})"
        return tru.create_clips_rule(self.name,
                                     self.lhs,
                                     self.rhs,
                                     self.axiom_prefix)

    @classmethod
    def extract_from(cls: _ruletype, store: rdflib.store) -> list[_ruletype]:
        """
        :TODO: Something for documentation. member, index, length seems to
            be special variablenames for rdf:containers
        """
        variablequery = """SELECT ?var WHERE {?var a swrl:Variable.}"""
        variables = list([result.var for result in store.query(variablequery)])
        trans_vars = lambda *l: tuple(f"?{x}" if x in variables else str(x)
                                         for x in l)

        class qq:
            def __init__(self, basenode, name, comment=None):
                self.name = name
                self.comment = comment
                self.lhs = {}
                self.rhs = {}

                self.basenode = basenode
                self.lhs_basenodes = []
                self.rhs_basenodes = []
            def __repr__(self):
                return f"<qq:{self.name}:{self.lhs}=>{self.rhs}>"
            def as_input(self):
                d = {"name":self.name}
                d["lhs"] = [self.lhs[i] for i in sorted(self.lhs.keys())]
                d["rhs"] = [self.rhs[i] for i in sorted(self.rhs.keys())]
                if self.comment is not None:
                    d["comment"] = self.comment
                return d
            def dedicated_axioms(self):
                yield (self.basenode, _RDFS.label, self.name)
                if self.comment is not None:
                    yield (self.basenode, _RDFS.comment, self.comment)
                yield (self.basenode, _SWRL.body, self.lhs_basenodes[0])
                yield (self.basenode, _SWRL.head, self.rhs_basenodes[0])
                for bn, atoms in ((self.lhs_basenodes, self.lhs),
                                  (self.rhs_basenodes, self.rhs)):
                    i = 0
                    for x,y in zip(bn[:-1], bn[1:]):
                        yield (x, _RDF.first, atoms.basenode[i])
                        yield (x, _RDF.rest, y)
                        i+=1
                yield (self.lhs_basenodes[-1], _RDF.rest, _RDF.nil)
                yield (self.rhs_basenodes[-1], _RDF.rest, _RDF.nil)


        rulequery = """
            SELECT ?ruleid ?name ?comment
            WHERE {
                ?ruleid a swrl:Imp.
                OPTIONAL {?ruleid rdfs:label ?rulename.}
                OPTIONAL {?ruleid rdfs:comment ?comment.}
            }"""

        data = {}
        for ruledata in store.query(rulequery):
            kwargs = {
                    "name": ruledata.name or ruledata.ruleid,
                    "comment": ruledata.comment,
                    }
            tmp_rule = data.setdefault(ruledata.ruleid, qq(ruledata.ruleid, **kwargs))

        lhs_rulequery = """
            SELECT ?ruleid ?listindex ?arg1 ?arg2 ?prop ?type ?qq
            WHERE {
                ?ruleid a swrl:Imp;
                        swrl:body ?lhs.
                #?lhs ?index ?axiom.
                ?lhs rdf:rest*/rdf:first ?axiom.

                {SELECT (COUNT(?q) AS ?listindex) WHERE {
                    ?lhs rdf:rest+ ?q.
                    ?q rdf:rest*/rdf:first ?axiom.
                }}
                #?lhs ?container_index ?axiom.
                #FILTER regex (?container_index, "http:\/\/www.w3.org\/1999\/02\/22-rdf-syntax-ns#_(\d+)")
                #BIND (REPLACE(?container_index, "http:\/\/www.w3.org\/1999\/02\/22-rdf-syntax-ns#_(\d+)", "$1") AS ?listindex)

                ?axiom a ?type.
                OPTIONAL {?axiom swrl:argument1 ?arg1 .}
                OPTIONAL {?axiom swrl:argument2 ?arg2 .}
                OPTIONAL {?axiom swrl:propertyPredicate|swrl:classPredicate ?prop .}
            }
            """

        data = {}
        for ruledata in store.query(lhs_rulequery):
            tmp_rule = data.setdefault(ruledata.ruleid, qq(name = ruledata.ruleid))
            i = int(ruledata.listindex)
            if ruledata.type == SWRL.IndividualPropertyAtom:
                tmp_rule.lhs[i] = trans_vars(ruledata.arg1, ruledata.prop, ruledata.arg2)
            elif ruledata.type == SWRL.ClassAtom:
                tmp_rule.lhs[i] = trans_vars(ruledata.arg1, RDF.type, ruledata.prop)
            else:
                raise Exception(ruledata.type)

        rhs_rulequery = """
            SELECT ?ruleid ?listindex ?axiom ?arg1 ?arg2 ?prop ?type
            WHERE {
                ?ruleid a swrl:Imp;
                        swrl:head ?rhs.
                #?rhs ?index ?axiom.
                ?rhs rdf:rest*/rdf:first ?axiom.
                {SELECT (COUNT(?q) AS ?listindex) WHERE {
                    ?lhs rdf:rest+ ?q.
                    ?q rdf:rest*/rdf:first ?axiom.
                }}
                ?axiom a ?type.
                OPTIONAL {?axiom swrl:argument1 ?arg1 .}
                OPTIONAL {?axiom swrl:argument2 ?arg2 .}
                OPTIONAL {?axiom swrl:propertyPredicate|swrl:classPredicate ?prop .}
            }
            """

        for ruledata in store.query(rhs_rulequery):
            tmp_rule = data.setdefault(ruledata.ruleid, qq(name = ruledata.ruleid))
            i = int(ruledata.listindex)
            if ruledata.type == SWRL.IndividualPropertyAtom:
                tmp_rule.rhs[i] = trans_vars(ruledata.arg1, ruledata.prop, ruledata.arg2)
            elif ruledata.type == SWRL.ClassAtom:
                tmp_rule.rhs[i] = trans_vars(ruledata.arg1, RDF.type, ruledata.prop)
            else:
                raise Exception(ruledata.type)

        for x in data.values():
            yield cls(**x.as_input())


def _get_collection(infograph: rdflib.Graph,
                    collection_id: rdflib.IdentifiedNode,
                    ) -> typ.Tuple[typ.Iterable, typ.Iterable["axiom"]]:
    all_axioms = []
    if (collection_id, _RDF.rest, None) in infograph:
        collection = rdflib.collection.Collection(infograph, collection_id)
        for i in range(len(collection)):
            n = collection._get_container(i)
            all_axioms.extend(infograph.triples((n, None, None)))
    else:
        collection = rdflib.Seq(infograph, collection_id)
        all_axioms.extend(infograph.triples((collection_id, None, None)))
    return collection, all_axioms
