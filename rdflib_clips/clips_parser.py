import rdflib
import rdflib.parser
try:
    rdflib.RDFS.Statement
    _RDFS = rdflib.RDFS
except AttributeError:
    _RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
_RDF = rdflib.RDF

from typing import IO, Optional, Union, TextIO, Any
import pathlib
from . import clips_to_swrl as clp2swrl
import logging
logger = logging.getLogger(__name__)
import pyparsing.exceptions

class BadSyntax(SyntaxError):
    pass

class SimpleOrga(rdflib.parser.Parser):
    def parse(self, source, sink, base=None, context=None, version=1.0):
        if base is None:
            base = sink.absolutize(
                    source.getPublicId() or source.getSystemId() or ""
                    )
        elif not isinstance(base, rdflib.IdentifiedNode):
            base = rdflib.URIRef(base)
        if context is None and hasattr(source, "url") and hasattr(source, "links"):
            if TYPE_CHECKING:
                assert isinstance(source, URLInputSource)
            context = context_from_urlinputsource(source)

        try:
            version = float(version)
        except ValueError:
            version = None
        return base, context, version


class ClipsParser(SimpleOrga):
    def parse(self,
              source: rdflib.parser.InputSource,
              sink: rdflib.Graph,
              encoding = "utf-8",
              base: str = None,
              mapping = {},
              **kwargs):
        """

        :param mapping: Used to :term:`map symbols` in clips program unto 
            IRIs.
            If empty string ('') is given, it will be used as base and
            specified base will be ignored.
            :term:`Standard translation` will be used for keywords, 'axiom'
            and 'type'
        """
        base_, context, version = super().parse(source=source, sink=sink,
                                               base=base,
                                               **kwargs)

        datastring = source.getCharacterStream().read()

        conj_sink: Graph

        myparser = clp2swrl.parser()
        try:
            result = myparser.parse_string(datastring)
        except pyparsing.exceptions.ParseSyntaxException as err:
            logger.debug(f"Failed to parse string:\n{datastring}")
            raise BadSyntax("couldnt parse, check debug logging. "
                            "Line with error: "
                            + err.mark_input_line()) from err
        if "" in mapping and base is not None:
            logger.warning(f"Will ignore specified base ({base}) and "
                           "instead use mapping[''] ({mapping['']}).")
        #mapping may be changed within as_rdfgraph
        mapping = dict(mapping)
        mapping.setdefault("", base_)
        mapping.setdefault("axiom", _RDFS.Statement)
        mapping.setdefault("type", _RDF.type)
        newgraph = result.as_rdfgraph(mapping)
        if sink.context_aware:
            sink.addN(newgraph.quads())
        else:
            for ax in newgraph:
                sink.add(ax)


from rdflib.parser import (
    BytesIOWrapper,
    InputSource,
    PythonInputSource,
    StringInputSource,
    URLInputSource,
    create_input_source,
)
