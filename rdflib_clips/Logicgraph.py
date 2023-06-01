import rdflib
from .rdfclips_namespace import RDFCLIPS as _RDFCLIPS
import tempfile
import clips
import logging
logger = logging.getLogger(__name__)

class logicgraph(rdflib.ConjunctiveGraph):
    """Conjunctive graph with implemented logic.
    """
    default_logic_graph: rdflib.IdentifiedNode
    def __init__(self, *args,
                 default_logic_graph = _RDFCLIPS.default_graph,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.default_logic_graph = default_logic_graph

    def run(self, logic_graph: rdflib.IdentifiedNode = None) -> rdflib.Graph:
        """
        :param logic_graph: overwrites default_logic_graph for this run 
            action. The default_logic_graph Defines, where new information is
            put.
        :TODO: try to circumvent usage of format in serialize(format='clp')
            so this is not dependent on registering serializer in rdflib.
        :TODO: replace Exception
        :TODO: Missing logging of watching facts and rules
        """
        if logic_graph is None:
            logic_graph = self.default_logic_graph
        clips_input = self.serialize(format = "clp")
        logger.debug("Uses clips input:\n%s" % clips_input)
        env = clips.environment.Environment()
        with tempfile.NamedTemporaryFile() as myfile:
            with open(myfile.name, "w") as q:
                q.write(clips_input)
            try:
                env.load(myfile.name)
            except clips.common.CLIPSError as err:
                raise Exception("This shouldnt have happend. Invalid "
                                "serialization: %s" % clips_input) from err
        #Currently dont know how to read out the output of clipspy
        #env.eval("(watch facts)")
        #env.eval("(watch rules)")
        env.reset()
        env.run()
        return_fact_construct\
                = "(deffacts resulting_facts\n%s\n)"\
                % ("\n".join(str(x) for x in env.facts()))
        g = rdflib.Graph(store = self.store, identifier = logic_graph)
        g.parse(data=return_fact_construct, format = "clp")
        return g
