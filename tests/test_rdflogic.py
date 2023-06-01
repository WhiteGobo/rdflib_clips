import rdflib_clips.serializer
from rdflib.plugins.stores.memory import Memory

import unittest
import os
import pathlib
import logging
logger = logging.getLogger(__name__)

import clips
import tempfile
import rdflib
import rdflib.serializer
import rdflib.parser
import rdflib.plugin

from rdflib import compare

_example_rules = """
@prefix ex: <example://> .
## im not sure what the difference is betweene swrl and swrlx
#@prefix swrlx: <http://www.w3.org/2003/11/swrlx> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
#@prefix swrla: <http://swrl.stanford.edu/ontologies/3.3/swrla.owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
#@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
#@prefix ruleml: <http://www.w3.org/2003/11/ruleml> .

_:y a swrl:Variable .
_:x a swrl:Variable .

## swrl:Imp seems equal to ruleml:imp
[] a swrl:Imp ;
    rdfs:label "asdf" ;
#    swrla:isRuleEnabled true ;
#    rdfs:comment ""^^xsd:string ;
#    ruleml:_rlab "http://example.org/naming_url" ;
## swrl:body seems equal to ruleml:_body
    swrl:body ( [
                        a swrl:IndividualPropertyAtom ;
                        swrl:argument1 _:x ;
                        swrl:argument2 _:y ;
                        swrl:propertyPredicate ex:a
                ] [
                        a swrl:ClassAtom ;
                        swrl:argument1 _:x ;
                        swrl:classPredicate ex:A
                ] ) ;
    swrl:head ( [
                        a swrl:IndividualPropertyAtom ;
                        swrl:argument1 _:y ;
                        swrl:argument2 _:x ;
                        swrl:propertyPredicate ex:b
                ] [
                        a swrl:ClassAtom ;
                        swrl:argument1 _:x ;
                        swrl:classPredicate ex:B
                ] ) .
"""

_example_rule2 = """
@prefix base: <urn://example.com/base#> .
@prefix ns1: <http://www.w3.org/2003/11/swrl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

base:var2 a ns1:Variable .

base:var1 a ns1:Variable .

[] a ns1:Imp ;
    rdfs:label base:rule1 ;
    ns1:body [ a rdf:Seq ;
            rdf:_1 [ a ns1:IndividualPropertyAtom ;
                    ns1:argument1 base:var1 ;
                    ns1:argument2 base:var2 ;
                    ns1:propertyPredicate <example://a> ] ;
            rdf:_2 [ a ns1:ClassAtom ;
                    ns1:ClassAtom <example://A> ;
                    ns1:argument1 base:var1 ] ] ;
    ns1:head [ a rdf:Seq ;
            rdf:_1 [ a ns1:IndividualPropertyAtom ;
                    ns1:argument1 base:var2 ;
                    ns1:argument2 base:var1 ;
                    ns1:propertyPredicate <example://b> ] ;
            rdf:_2 [ a ns1:ClassAtom ;
                    ns1:ClassAtom <example://B> ;
                    ns1:argument1 base:var1 ] ] .
"""

_example_facts = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <example://> .

ex:a a rdfs:Class.
ex:A a rdf:Property.
ex:b a rdfs:Class.
ex:B a rdf:Property.

ex:obj1 a ex:A;
    ex:a ex:obj2.
"""

_example_facts2 = """
@prefix base: <urn://example.com/base#> .

base:duck base:called base:dough .
"""

_example_deffacts = """(deffacts myfacts
    (axiom example://a http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://www.w3.org/2000/01/rdf-schema#Class)
    (axiom n5383d1c3d8c8423a8bc55a7627d63895b4 http://www.w3.org/2003/11/swrl#propertyPredicate example://a)
    (axiom file:///home/hfechner/Projects/rdflib-clips/obj1 example://a file:///home/hfechner/Projects/rdflib-clips/obj2)
    (axiom example://A http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://www.w3.org/1999/02/22-rdf-syntax-ns#Property)
    (axiom n5383d1c3d8c8423a8bc55a7627d63895b5 http://www.w3.org/2003/11/swrl#classPredicate example://A)
    (axiom file:///home/hfechner/Projects/rdflib-clips/obj1 http://www.w3.org/1999/02/22-rdf-syntax-ns#type example://A)
)"""
_example_deffacts = "(deffacts myfacts (axiom duck called dough))"

_example_defrule = """(defrule rule1
    (axiom ?var1 <example://a> ?var2)
    (type ?var1 <example://A>)
    =>
    (assert (axiom ?var2 <example://b> ?var1))
    (assert (type ?var1 <example://B>))
)"""

class TestClipsInterpreterAsRDFPlugin(unittest.TestCase):
    def setUp(self):
        rdflib.plugin.register("clp", rdflib.serializer.Serializer,
                               "rdflib_clips.serializer", "ClipsSerializer")
        rdflib.plugin.register("clp", rdflib.parser.Parser,
                               "rdflib_clips.clips_parser", "ClipsParser")

    def test_SwrlRuleToClips_andLogic(self, clips_format="clp"):
        """Tests rule translation from Swrl to Clips and if given
        rule works correctly.

        :TODO: Missing printout of watching facts and rules
        """
        ex = rdflib.Namespace("http://example.com/mydata#")
        mem = Memory()
        conjg = rdflib_clips.logicgraph(store = mem)
        datagraph = rdflib.Graph(store = mem, identifier=ex.datagraph_id)
        datagraph.parse(data = _example_rules, format="ttl")
        rulegraph = rdflib.Graph(store = mem, identifier=ex.rulegraph_id)
        rulegraph.parse(data = _example_facts, format="ttl")
        allfacts = conjg.run()

        ex = rdflib.Namespace("example://")
        from rdflib import RDF
        fact1 = (ex.obj2, ex.b, ex.obj1)
        fact2 = (ex.obj1, RDF.type, ex.B)

        try:
            self.assertTrue(all(f in allfacts for f in (fact1, fact2)),
                            "Missing facts: %s" % [f for f in (fact1, fact2)
                                                   if f not in allfacts])
        except Exception as err:
            logger.warning(f"All contained facts:\n%s" % allfacts.serialize())
            raise Exception("Something went wrong. Logic didnt work as it"
                            "should. See warnlogging for print of clips file"
                            ) from err


if __name__=='__main__':
    logging.basicConfig( level=logging.DEBUG )
    #logging.getLogger("route.to.module").setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    unittest.main()
