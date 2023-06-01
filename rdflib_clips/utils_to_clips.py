"""This module provides methods to translate from rdf to clips and vice-versa,
e.g. translate :term:`axioms<axiom>`, :term:`IRIs<IRI>`, :term:`rules<rule>`

"""
import rdflib
DEFAULT_axiom = "fact"

def IRI_to_clips(iri: rdflib.IdentifiedNode):
    """Translates an iri to a :term:`single field value`"""
    return str(iri)

def axiom_to_clips(axiom, axiom_base=None, **extra_args_translator) -> str:
    """

    :param axiom_base: first attribute of every :term:`fact` in clips,
        that represents an :term:`axiom` in :term:`RDF`.
        Uses DEFAULT_axiom if left as None
    :param extra_args_translator: will be given to IRI_to_clips
    """
    if axiom_base is None:
        axiom_base = DEFAULT_axiom
    try:
        assert len(axiom) == 3
    except AssertionError:
        raise TypeError(axiom)
    subject = IRI_to_clips(axiom[0], **extra_args_translator)
    predicate = IRI_to_clips(axiom[1], **extra_args_translator)
    object = IRI_to_clips(axiom[2], **extra_args_translator)
    return f"({axiom_base} {subject} {predicate} {object})"

def assert_axiom(axiom, axiom_base=None, **extra_args_translator) -> str:
    """Funnels axiom to axiom_to_clips but creates an clips assert of that
    axiom
    """
    axiom = axiom_to_clips(axiom, axiom_base, **extra_args_translator)
    return f"(assert {axiom})"

def create_clips_rule(name, lhs, rhs, axiom_prefix):
    """
    :param name: name of the rule
    :param lhs: Left-hand side of rule
    :param rhs: Right-hand side of rule
    """
    lhs = " ".join(axiom_to_clips(ax, axiom_prefix)
                   for ax in lhs)
    rhs = " ".join(assert_axiom(ax, axiom_prefix)
                   for ax in rhs)
    return f"(defrule {name} {lhs} => {rhs})"

def deffacts(name, facts, axiom_prefix):
    facts = "\n".join("    %s"
             %(axiom_to_clips(ax, axiom_prefix))
             for ax in facts)
    return f"(deffacts {name}\n{facts}\n)"

