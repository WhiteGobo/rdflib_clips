from . import clips_pyparsing as cp_parse
from .rule import _function_call, _rule, conditional, CE_ordered_pattern, clips_container, variable
from .facts import _deffacts, simple_fact


class facts_parser(cp_parse.deffacts_parser):
    def parse_deffacts_construct(self, name, facts=[], comment=None):
        extraargs = {}
        if comment is not None:
            extraargs["comment"] = comment
        return _deffacts(name, facts, **extraargs)

    def parse_template_RHS_pattern(self, template_name, *slots):
        raise NotImplementedError()

    def parse_ordered_RHS_pattern(self, firstsymbol, *symbols):
        return simple_fact(firstsymbol, *symbols)

class rule_parser(cp_parse.rule_parser):
    """
    :todo: rework __symbol_to_info
    """
    def parse_defrule_construct(self, name,
                                conditionals: list[conditional],
                                actions: list,
                                comment=None, declaration=None):

        extraargs = {}
        if comment is not None:
            extraargs["comment"] = comment
        if declaration is not None:
            extraargs["declaration"] = declaration
        return _rule(name, conditionals, actions, **extraargs)

    def parse_constant(self, constant: str) -> object:
        return constant

    def parse_single_field_variable(self, symbol: str) -> tuple[object]:
        return variable(symbol)

    def parse_multifield_variable(self, symbol: str) -> tuple[object]:
        raise NotImplementedError(symbol)

    def parse_global_variable(self, symbol: str) -> tuple[object]:
        raise NotImplementedError(symbol)

    def parse_function_call(self, functionname, *args):
        return _function_call(functionname, args)

    def parse_ordered_pattern_CE(self, firstsymbol, *symbols):
        return CE_ordered_pattern(firstsymbol, *symbols)

    def parse_single_negated_constraint(self, term):
        raise NotImplementedError()

    def parse_single_constraint(self, term):
        return term

    def parse_connected_constraint(self, first_constraint,
                                   operator: ("&", "|", None) = None,
                                   second_constraint = None):
        """
        :TODO: rewrite with connected_conditional
        """

        if second_constraint:
            return first_constraint, operator, second_constraint
        else:
            return first_constraint

    def parse_single_wildcard(self):
        raise NotImplementedError()

    def parse_multi_wildcard(self):
        raise NotImplementedError()

    def parse_object_pattern_CE(self, **args) -> tuple[object]:
        raise NotImplementedError(args)

    def parse_template_pattern_CE(self, **args) -> tuple[object]:
        raise NotImplementedError(args)

    def parse_assigned_pattern_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_not_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_and_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_or_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_logical_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_test_CE(self, **args) -> tuple[object]:
        raise NotImplementedError()

    def parse_exists_CE(self) -> tuple[object]:
        raise NotImplementedError()

    def parse_forall_CE(self) -> tuple[object]:
        raise NotImplementedError()

class parser(rule_parser, facts_parser, cp_parse.program_parse):
    def parse_Clips_program(self, *constructs):
        return clips_container(*constructs)
