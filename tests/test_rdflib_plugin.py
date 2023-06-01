"""Testmethods for clips interpreter as rdflib-plugin.

:TODO: TestClipsInterpreterAsRDFPlugin.test_ToClipsBackToRDF_AxiomRetainment
"""
import rdflib_clips.serializer

import unittest
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

<obj1> a ex:A;
    ex:a <obj2>.
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
    _fromClips_array = [
            ("rule", _example_defrule, _example_rule2),
            ("facts", _example_deffacts, _example_facts2),
            ]

    def setUp(self):
        rdflib.plugin.register("clp", rdflib.serializer.Serializer,
                               "rdflib_clips.serializer", "ClipsSerializer")
        rdflib.plugin.register("clp", rdflib.parser.Parser,
                               "rdflib_clips.clips_parser", "ClipsParser")

    def test_SwrlFromClips(self, clips_format="clp"):
        """Tests translation from clips to rdf."""
        base = "urn://example.com/base#"
        for name, testinput, testoutput in self._fromClips_array:
            with self.subTest(name):
                outputgraph = compare.to_isomorphic(
                        rdflib.Graph().parse(data=testoutput))
                g = rdflib.Graph()
                g.parse(data = testinput, format = clips_format, base=base)
                g.bind("base", base)
                cg = compare.to_isomorphic(g)
                try:
                    self.assertEqual(cg, outputgraph,
                                     "didnt get expected graph. Check warn "
                                     "log for more information.")
                except AssertionError:
                    in_both, in_first, in_second\
                            = compare.graph_diff(cg, outputgraph)
                    in_first.bind("base", base)
                    in_second.bind("base", base)
                    logger.warning("extra information:\n%s"
                                   % (in_first.serialize()))
                    logger.warning("missing information:\n%s"
                                   %(in_second.serialize()))
                    logger.warning("Got graph back:\n%s" %(g.serialize()))
                    raise

    def test_SwrlRuleToClips_andLogic(self, clips_format="clp"):
        """Tests rule translation from Swrl to Clips and if given
        rule works correctly.

        :TODO: Missing printout of watching facts and rules
        """
        g = rdflib.Graph()
        g.parse(data = _example_rules, format="ttl")
        g.parse(data = _example_facts, format="ttl")
        clips_input = g.serialize(format = clips_format)

        env = clips.environment.Environment()
        with tempfile.NamedTemporaryFile() as myfile:
            with open(myfile.name, "w") as q:
                q.write(clips_input)
            try:
                env.load(myfile.name)
            except clips.common.CLIPSError as err:
                raise Exception("invalid serialization: %s" % clips_input)\
                        from err
        #try:
        #    env.build(clips_input)
        #except Exception as err:
        #    raise Exception(clips_input) from err
        logger.debug("Input used for clips:\n%s"%(clips_input))
        #Currently dont know how to read out the output of clipspy
        #env.eval("(watch facts)")
        #env.eval("(watch rules)")
        env.reset()
        env.run()
        fact1 = ('axiom', '<file:///home/hfechner/Projects/rdflib_clips/obj2>',
                 '<example://b>',
                 '<file:///home/hfechner/Projects/rdflib_clips/obj1>')
        fact2 = ('class', '<example://B>',
                 '<file:///home/hfechner/Projects/rdflib_clips/obj1>')
        myfacts = [tuple([ax.template.name] + [str(x) for x in ax])
                   for ax in env.facts()]
        try:
            self.assertTrue(all(f in myfacts for f in (fact1, fact2)),
                            "Missing facts: %s" % [f for f in (fact1, fact2)
                                                   if f not in myfacts])
        except Exception as err:
            logger.warning(f"All contained facts:\n%s"
                           % ("\n".join(str(f) for f in myfacts)))
            raise Exception("Something went wrong. Logic didnt work as it"
                            "should. See warnlogging for print of clips file"
                            ) from err

    @unittest.skip("currently doesnt correctly translates names and "
                   "bases. Also has its problems creating labels as strings "
                   "and not as IRIs.")
    def test_ToClipsBackToRDF_AxiomRetainment(self,\
            infograph: rdflib.Graph = None,\
            binding: dict = {},\
            clips_format="clp",\
            ):
        """Translates given Graph into Clips and back to RDF. Tests if all 
        information is translated back correctly.
        """
        if infograph is None:
            infograph = rdflib.Graph()
            infograph.parse(data = _example_rules, format="ttl")
            infograph.parse(data = _example_facts, format="ttl")
        logger.debug("used graph:\n%s" % infograph.serialize())
        clips_input = infograph.serialize(format = clips_format)
        logger.debug("Input used for clips:\n%s"%(clips_input))
        newgraph = rdflib.Graph()
        newgraph.parse(data = clips_input, format = clips_format)
        cg_init = compare.to_isomorphic(infograph)
        cg_transformed = compare.to_isomorphic(newgraph)
        try:
            self.assertEqual(cg_init, cg_transformed,
                             "Didnt retained information as expected")
        except AssertionError:
            _, missing, additional\
                    =compare.graph_diff(cg_init, cg_transformed)
            for name, iri in binding.items():
                missing.bind(name, iri)
                additional.bind(name, iri)
            logger.warning("extra information:\n%s" % additional.serialize())
            logger.warning("missing information:\n%s" % missing.serialize())
            logger.warning("got graph back:\n%s" % newgraph.serialize())
            raise


if __name__=='__main__':
    logging.basicConfig( level=logging.DEBUG )
    #logging.getLogger("route.to.module").setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    unittest.main()
