import unittest
import logging
logger = logging.getLogger(__name__)
from rdflib_clips import clips_to_swrl as clp2swrl
import rdflib
import rdflib.compare


class TestSimple(unittest.TestCase):
    def test_deffacts_to_rdf(self):
        clipsprogram = "(deffacts myfacts (axiom duck called dough))"
        testfacts = """
            @prefix ex: <http://example.com/> .
            ex:duck ex:called ex:dough .
            """
        g = rdflib.Graph().parse(data=testfacts, format="ttl")
        mybase = rdflib.Namespace("http://example.com/")
        p = clp2swrl.parser()
        result = p.parse_string(clipsprogram)
        q = result.as_rdfgraph(mybase)
        logger.debug(q.serialize())
        cg1 = rdflib.compare.to_isomorphic(g)
        cg2 = rdflib.compare.to_isomorphic(q)
        try:
            self.assertEqual(cg1, cg2, "didnt get the expected graph back. "
                             "See info-log for more information")
        except Exception:
            inboth, in1, in2 = rdflib.compare.graph_diff(cg1, cg2)
            logger.info(f"only in expected graph:\n{in1.serialize()}")
            logger.info(f"only in generated graph:\n{in2.serialize()}")
            raise
        
    def test_rule_to_rdf(self):
        clipsprogram = "(defrule myexc (axiom duck called dough) => "\
                + "(assert (axiom duck notcalled brubru)))"
        testrule = """
            @prefix ex: <http://example.com/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix swrl: <http://www.w3.org/2003/11/swrl#> .

            [] a swrl:Imp ;
                rdfs:label ex:myexc ;
                swrl:body [ a rdf:Seq ;
                        rdf:_1 [ a swrl:IndividualPropertyAtom ;
                                swrl:argument1 ex:duck ;
                                swrl:argument2 ex:dough ;
                                swrl:propertyPredicate ex:called ] ] ;
                swrl:head [ a rdf:Seq ;
                        rdf:_1 [ a swrl:IndividualPropertyAtom ;
                                swrl:argument1 ex:duck ;
                                swrl:argument2 ex:brubru ;
                                swrl:propertyPredicate ex:notcalled ] ] .
            """
        g = rdflib.Graph().parse(data=testrule, format="ttl")
        mybase = rdflib.Namespace("http://example.com/")
        p = clp2swrl.parser()
        result = p.parse_string(clipsprogram)
        q = result.as_rdfgraph(mybase)
        logger.debug(q.serialize())
        cg1 = rdflib.compare.to_isomorphic(g)
        cg2 = rdflib.compare.to_isomorphic(q)
        try:
            self.assertEqual(cg1, cg2, "didnt get the expected graph back. "
                             "See info-log for more information")
        except Exception:
            inboth, in1, in2 = rdflib.compare.graph_diff(cg1, cg2)
            logger.info(f"only in expected graph:\n{in1.serialize()}")
            logger.info(f"only in generated graph:\n{in2.serialize()}")
            raise


if __name__=='__main__':
    logging.basicConfig( level=logging.WARNING )
    #logging.getLogger("route.to.module").setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    unittest.main()
