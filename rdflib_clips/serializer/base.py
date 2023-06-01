import rdflib
import abc
import typing as typ
_ruletype = typ.TypeVar("clipsrule")

class fact_base(abc.ABC):
    @abc.abstractmethod
    def serialize(self) -> str:
        ...

class clips_rule_base(abc.ABC):
    init_query: str
    """Sparqlquery to find this type of :term:`rule`."""

    dedicated_axioms: set
    """Axioms that cant be shared, with other rules."""

    axioms: set
    """All axioms, that are implicated by this rule."""

    @classmethod
    @abc.abstractmethod
    def from_queryresult(cls: _ruletype, infograph: rdflib.Graph,
                      **query_results: typ.Any) -> _ruletype:
        """
        :param query_results: The results of the query init_query will be
            given as keywords to this function.
        """
        ...
