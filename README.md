rdflib-clips
=============

This module provides a plugin for [rdflib](https://github.com/RDFLib/rdflib)
to parse and serialize code for [clips](https://www.clipsrules.net/).

This module is in an early stage of development. Currently it translates
only some rules and simple axioms.
It converts clips rules into [swrl-syntax](https://www.w3.org/Submission/SWRL/)
and all other statements into ordered facts.

Outside of later given examples currently no translation between clips and 
rdf is possible.


Current motivation
------------------

I want currently use clips as reasoning engine for rdf graphs but with RIF-PRD
rules. So in the future swrl support may be cut. And because i have no access
to typical clips programs i wont actively develope on supporting every
possible clips syntax.


fact translation example
------------------------

```
@prefix ex: <http://example.com/some-facts#>.

ex:obj a ex:class .
ex:obj ex:property ex:target .
```
Would be translated this way:

```
(deffacts myfacts
    (class <http://example.com/some-facts#class> <http://example.com/some-facts#obj>)
    (fact <http://example.com/some-facts#obj> <http://example.com/some-facts#property> <http://example.com/some-facts#target>)
)
```

or

```
(deffacts myfacts
    (class ex:class ex:obj)
    (axiom ex:obj ex:property ex:target)
)
```

rule translation example
------------------------

```
(defrule myrule
    (axiom ?var1 ex:property ex:target)
    =>
    (assert (class ex:class ?var1))
)
```

Is equal to

```
@prefix ex: <http://example.com/some-facts#>.

_:var1 a swrl:Variable .

[ a swrl:Imp;
    rdf:label "myrule";
    swrl:body ([
            a swrl:IndiviualPropertyAtom ;
            swrl:argument1 _:var1 ;
            swrl:propertyPredicate ex:property ;
            swrl:argument2 ex:target
        ]) ;
    swrl:head ([
            a swrl:ClassAtom ;
            swrl:argument1 _:var1 ;
            swrl:classPredicate ex:class
        ]) 
]
```
