"""This module provides a simple class to parse an input for :term:`clips`.
It uses the ENBF provided by the `Clips Basic Programming Guide`_

:TODO: This parser isnt complete yet. See sourcecode for further information.

.. _Clips Basic Programming Guide: https://www.clipsrules.net/documentation/v641/bpg641.pdf
"""
import pyparsing as pp
import abc
import typing as typ

class my_exc(pp.ParseFatalException):
    @classmethod
    def raise_this(cls, s, location, t):
        raise cls(s, location, t[0])
    @classmethod
    def raise_if(cls, identifier):
        return identifier.setParseAction(cls.raise_this)


class exc_name(my_exc):
    def __init__(self, s, loc, msg):
        super().__init__(s, loc, "Invalid Name '%s'" % msg)

class exc_rule_lhs(my_exc):
    def __init__(self, s, loc, msg):
        super().__init__(s, loc, "Invalid leftside '%s'" % msg)

class exc_conditional_element(my_exc):
    def __init__(self, s, loc, msg):
        super().__init__(s, loc, "invalid conditional for rule; '%s'" % msg)

_re_term = ""

class clips_EBNF:
    """Basic implementation of a parser for clips.
    Methods are used within the parser, so overwritting them via subclassing
    will directly change, how the parser works.

    :TODO: single_field_LHS_slot seems like a duplicate to multifield_LHS_slot
    """
    symbol: object
    """pp.Regex("[a-zA-Z<>]+")"""
    variable: object
    """[?]+symbol"""
    prim_integer:object
    """pp.pyparsing_common.integer"""
    prim_float: object
    """pp.pyparsing_common.real"""
    prim_string: object
    """'[\"][^\"]*[\"] | [\'][^\'\"]*[\']"""
    name:object
    """symbol"""
    comment: object
    """prim_string"""
    variable_symbol: object
    """symbol"""
    instance_name:object
    """symbol"""
    constant: object
    """symbol | prim_string | prim_integer | prim_float | instance_name"""
    function_name: object
    """symbol"""
    deftemplate_name: object
    """symbol"""
    slot_name: object
    """symbol"""
    function_call: object
    """( + function_name + pp.ZeroOrMore(expression) + )"""
    expression: object
    """constant | variable | function_call"""
    action: object
    """expression"""
    constant: object
    """symbol | prim_string | prim_float | prim_integer | instance_name"""
    single_field_variable: object
    """ ? + variable_symbol"""
    multifield_variable: object
    """$? + variable_symbol"""
    RHS_field: object
    """variable | constant | function_call"""
    single_field_RHS_slot: object
    """( + slot_name + RHS_field + )"""
    multifield_RHS_slot: object
    """( + slot_name + pp.ZeroOrMore(RHS_field) + )"""
    #RHS_slot = single_field_RHS_slot | multifield_RHS_slot
    #global_variable = "?*" + symbol + "*"
    #global_variable.leave_whitespace()
    #variable = single_field_variable\
    #        | multifield_variable\
    #        | global_variable
    #RHS_field = variable | constant | function_call
    #ordered_RHS_pattern = pp.Suppress("(") + symbol\
    #        + pp.OneOrMore(RHS_field) + pp.Suppress(")")
    #template_RHS_pattern = pp.Suppress("(") + deftemplate_name\
    #        + pp.ZeroOrMore(RHS_slot) + pp.Suppress(")")
    #RHS_pattern = ordered_RHS_pattern\
    #        | template_RHS_pattern

    #Defrule construct
    #boolean_symbol = pp.Regex("TRUE") | pp.Regex("FALSE")
    #term = constant\
    #        | single_field_variable\
    #        | multifield_variable\
    #        | (":" + function_call)\
    #        | ("=" + function_call)
    #single_constraint = term | ("~"+term)
    #connected_constraint = pp.Forward()
    #connected_constraint <<= single_constraint\
    #        | (single_constraint + "&" + connected_constraint)\
    #        | (single_constraint + "|" + connected_constraint)
    #constraint = pp.Regex("[?]") | "$?" | connected_constraint
    #single_field_LHS_slot = "(" + slot_name\
    #        + constraint + ")"
    #multifield_LHS_slot = "(" + slot_name\
    #        + pp.ZeroOrMore(constraint) + ")"
    #LHS_slot = single_field_LHS_slot\
    #        | multifield_LHS_slot
    #attribute_constraint = ("(is-a" + constraint + ")")\
    #        | ("(name" + constraint +")")\
    #        | ("(" + slot_name + pp.ZeroOrMore(constraint) + ")")
    #ordered_pattern_CE = pp.Suppress("(") + symbol\
    #        + pp.ZeroOrMore(constraint) + pp.Suppress(")")
    #template_pattern_CE = pp.Suppress("(") + deftemplate_name\
    #        + pp.ZeroOrMore(LHS_slot) + pp.Suppress(")")
    #object_pattern_CE = pp.Suppress("(object")\
    #        + pp.ZeroOrMore(attribute_constraint) + pp.Suppress(")")
    #pattern_CE = ordered_pattern_CE\
    #        | template_pattern_CE\
    #        | object_pattern_CE
    #assigned_pattern_CE = single_field_variable + "<-"\
    #        + pattern_CE
    #not_CE = "(not" + conditional_element + ")"
    #and_CE = "(and" + pp.OneOrMore(conditional_element) + ")"
    #or_CE = "(or" + pp.OneOrMore(conditional_element) + ")"
    #logical_CE = "(logical"\
    #        + pp.OneOrMore(conditional_element) + ")"
    #test_CE = "(test" + function_call + ")"
    #exists_CE = "(exists"\
    #        + pp.OneOrMore(conditional_element) + ")"
    #forall_CE = "(forall" + conditional_element\
    #        + pp.OneOrMore(conditional_element) + ")"
    #conditional_element <<= pattern_CE\
    #        | assigned_pattern_CE\
    #        | not_CE | and_CE | or_CE\
    #        | logical_CE | test_CE\
    #        | exists_CE | forall_CE\
    #        #| error(exc_conditional_element)
            
    #rule_property = (pp.Suppress("(salience") \
    #        + prim_integer + pp.Suppress(")"))\
    #        | ("(auto-focus" + boolean_symbol + ")")
    #declaration = pp.Suppress("(declare")\
    #        + pp.OneOrMore(rule_property) + pp.Suppress(")")
    #deffacts_construct = pp.Suppress("(deffacts")\
    #        + (name | exc_name.raise_if(pp.Regex("\S*")))\
    #        + pp.Optional(comment) + pp.ZeroOrMore(RHS_pattern)\
    #        + pp.Suppress(")")
    #defrule_construct = (pp.Suppress("(defrule")\
    #        + (name.set_results_name("name")
    #           | exc_name.raise_if(pp.Regex("\S*")))\
    #        + pp.Optional(comment).set_results_name("comment")\
    #        + pp.Optional(declaration)\
    #        .set_results_name("declaration")\
    #        + pp.ZeroOrMore(conditional_element)\
    #        .set_results_name("conditionals")\
    #        - (pp.Suppress("=>")
    #           | exc_rule_lhs.raise_if(pp.Regex(".*=>")))\
    #        + pp.OneOrMore(action).set_results_name("actions")\
    #        + pp.Suppress(")"))
    #construct = (deffacts_construct\
    #        #| deftemplate_construct\
    #        #| defglobal_construct\
    #        | defrule_construct\
    #        #| deffunction_construct\
    #        #| defgeneric_construct\
    #        #| defmethod_construct\
    #        #| defclass_construct\
    #        #| definstance_construct\
    #        #| defmessage_handler_construct\
    #        #| defmodule_construct\
    #        ) #remove () when nothing is comented out
    #Clips_program = pp.OneOrMore(construct)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.symbol = pp.Regex("[a-zA-Z][a-zA-Z0-9.:\/\-_#&$]*")
        #self.variable = pp.Regex("\?[a-zA-Z][a-zA-Z0-9.:\/\-_#&$]*")
        self.symbol = pp.Regex("[a-zA-Z<>][^() \t\n]+")
        #self.variable = pp.Regex("\?[a-zA-Z][^()\s]+")
        self.variable = pp.Forward()
        self.prim_integer = pp.pyparsing_common.integer
        self.prim_float = pp.pyparsing_common.real
        #self.prim_string = pp.QuotedString()
        self.prim_string = pp.Regex("[\"][^\"]*[\"]") \
                          | pp.Regex("[\'][^\'\"]*[\']")
        self.name = self.symbol
        self.comment = self.prim_string
        self.variable_symbol = self.symbol
        self.instance_name = self.symbol
        self.constant = self.symbol | self.prim_string | self.prim_integer\
                | self.prim_float | self.instance_name
        self.function_name = self.symbol
        self.deftemplate_name = self.symbol
        self.slot_name = self.symbol
        self.expression = pp.Forward()
        self.function_call = pp.Suppress("(") + self.function_name\
                + pp.ZeroOrMore(self.expression) + pp.Suppress(")")
        self.expression <<= self.constant | self.variable | self.function_call
        self.action = self.expression
        self.constant = self.symbol | self.prim_string\
                | self.prim_float | self.prim_integer | self.instance_name
        #need to have no whitespaces between ? and symbol but whitespaces
        #before ? must be allowed
        self.single_field_variable = pp.Combine(\
                (pp.Suppress("?") + self.variable_symbol).leave_whitespace())
        self.multifield_variable = pp.Combine(\
                (pp.Suppress("$?") + self.variable_symbol).leave_whitespace())
        self.RHS_field = self.variable | self.constant | self.function_call
        self.single_field_RHS_slot = pp.Suppress("(") + self.slot_name\
                + self.RHS_field + pp.Suppress(")")
        self.multifield_RHS_slot = pp.Suppress("(") + self.slot_name\
                + pp.ZeroOrMore(self.RHS_field) + pp.Suppress(")")
        self.RHS_slot = self.single_field_RHS_slot | self.multifield_RHS_slot
        self.global_variable = pp.Suppress("?*") + self.symbol + pp.Suppress("*")
        self.global_variable.leave_whitespace()
        self.variable <<= self.single_field_variable\
                | self.multifield_variable\
                | self.global_variable
        self.RHS_field = self.variable | self.constant | self.function_call
        #RHS_field seems to be the same as expression
        self.ordered_RHS_pattern = pp.Suppress("(") + self.symbol\
                + pp.OneOrMore(self.RHS_field) + pp.Suppress(")")
        self.template_RHS_pattern = pp.Suppress("(") + self.deftemplate_name\
                + pp.ZeroOrMore(self.RHS_slot) + pp.Suppress(")")
        self.RHS_pattern = self.ordered_RHS_pattern\
                | self.template_RHS_pattern

        #Defrule construct
        self.boolean_symbol = pp.Regex("TRUE") | pp.Regex("FALSE")
        self.term = self.constant\
                | self.single_field_variable\
                | self.multifield_variable\
                | (":" + self.function_call)\
                | ("=" + self.function_call)
        self.single_constraint = self.term
        self.single_negated_constraint = "~" + self.term
        self.connected_constraint = pp.Forward()
        self.connected_constraint <<= self.single_constraint\
                | self.single_negated_constraint\
                | (self.single_constraint + "&" + self.connected_constraint)\
                | (self.single_constraint + "|" + self.connected_constraint)
        self.single_wildcard = pp.Suppress("?")
        self.multi_wildcard = pp.Suppress("$?")
        self.constraint = self.connected_constraint | self.single_wildcard\
                | self.multi_wildcard
        self.constraint = self.connected_constraint
        self.single_field_LHS_slot = "(" + self.slot_name\
                + self.constraint + ")"
        self.multifield_LHS_slot = "(" + self.slot_name\
                + pp.ZeroOrMore(self.constraint) + ")"
        self.LHS_slot = self.single_field_LHS_slot\
                | self.multifield_LHS_slot
        self.attribute_constraint = ("(is-a" + self.constraint + ")")\
                | ("(name" + self.constraint +")")\
                | ("(" + self.slot_name + pp.ZeroOrMore(self.constraint) + ")")
        self.ordered_pattern_CE = pp.Suppress("(") + self.symbol\
                + pp.ZeroOrMore(self.constraint) + pp.Suppress(")")
        self.template_pattern_CE = pp.Suppress("(") + self.deftemplate_name\
                + pp.ZeroOrMore(self.LHS_slot) + pp.Suppress(")")
        self.object_pattern_CE = pp.Suppress("(object")\
                + pp.ZeroOrMore(self.attribute_constraint) + pp.Suppress(")")
        self.pattern_CE = self.ordered_pattern_CE\
                | self.template_pattern_CE\
                | self.object_pattern_CE
        self.assigned_pattern_CE = self.single_field_variable + "<-"\
                + self.pattern_CE
        self.conditional_element = pp.Forward()
        self.not_CE = "(not" + self.conditional_element + ")"
        self.and_CE = "(and" + pp.OneOrMore(self.conditional_element) + ")"
        self.or_CE = "(or" + pp.OneOrMore(self.conditional_element) + ")"
        self.logical_CE = "(logical"\
                + pp.OneOrMore(self.conditional_element) + ")"
        self.test_CE = "(test" + self.function_call + ")"
        self.exists_CE = "(exists"\
                + pp.OneOrMore(self.conditional_element) + ")"
        self.forall_CE = "(forall" + self.conditional_element\
                + pp.OneOrMore(self.conditional_element) + ")"
        self.conditional_element <<= self.pattern_CE\
                | self.assigned_pattern_CE\
                | self.not_CE | self.and_CE | self.or_CE\
                | self.logical_CE | self.test_CE\
                | self.exists_CE | self.forall_CE\
                | exc_conditional_element.raise_if(pp.Regex("[(][^)]*[)]+"))\
                
        self.rule_property = (pp.Suppress("(salience") \
                + self.prim_integer + pp.Suppress(")"))\
                | ("(auto-focus" + self.boolean_symbol + ")")
        self.declaration = pp.Suppress("(declare")\
                + pp.OneOrMore(self.rule_property) + pp.Suppress(")")
        self.deffacts_construct = pp.Suppress("(deffacts")\
                + (self.name.set_results_name("name")\
                | exc_name.raise_if(pp.Regex(".*")))\
                + pp.Optional(self.comment).set_results_name("comment")\
                + pp.ZeroOrMore(self.RHS_pattern).set_results_name("facts")\
                + pp.Suppress(")")
        self.defrule_construct = (pp.Suppress("(defrule")\
                + (self.name.set_results_name("name")
                   | exc_name.raise_if(pp.Regex(".*")))\
                + pp.Optional(self.comment).set_results_name("comment")\
                + pp.Optional(self.declaration)\
                .set_results_name("declaration")\
                + pp.ZeroOrMore(self.conditional_element)\
                .set_results_name("conditionals")\
                - (pp.Suppress("=>")
                   | exc_rule_lhs.raise_if(pp.Regex(".*=>")))\
                + pp.OneOrMore(self.action).set_results_name("actions")\
                + pp.Suppress(")"))
        self.construct = (self.deffacts_construct\
                #| self.deftemplate_construct\
                #| self.defglobal_construct\
                | self.defrule_construct\
                #| self.deffunction_construct\
                #| self.defgeneric_construct\
                #| self.defmethod_construct\
                #| self.defclass_construct\
                #| self.definstance_construct\
                #| self.defmessage_handler_construct\
                #| self.defmodule_construct\
                ) #remove () when nothing is comented out
        self.Clips_program = pp.OneOrMore(self.construct)

        program_comment = ";[^\r\n]*[\r\n$]" #im not sure if $ should be included
        self.Clips_program.ignore(program_comment)
        #self.Clips_program.set_default_whitespace_chars(" \r\n\t")

    def parse_string(self, string):
        result = self.Clips_program.parse_string(string)
        q, = result
        return q

class program_parse(clips_EBNF, abc.ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Clips_program.set_parse_action(\
                lambda result: self.parse_Clips_program(*result))

    @abc.abstractmethod
    def parse_Clips_program(self, *constructs):
        ...

class deffacts_parser(clips_EBNF, abc.ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deffacts_construct.set_parse_action(\
                lambda result: self.parse_deffacts_construct(**result))
        self.ordered_RHS_pattern.set_parse_action(\
                lambda result: self.parse_ordered_RHS_pattern(*result))
        self.template_RHS_pattern.set_parse_action(\
                lambda result: self.parse_template_RHS_pattern(*result))

    @abc.abstractmethod
    def parse_ordered_RHS_pattern(self, firstsymbol, *symbols):
        ...

    @abc.abstractmethod
    def parse_template_RHS_pattern(self, template_name, *slots):
        ...

    @abc.abstractmethod
    def parse_deffacts_construct(self, name, facts=[], comment=None):
        ...

class rule_parser(clips_EBNF, abc.ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.defrule_construct.set_parse_action(\
                lambda result: self.parse_defrule_construct(**result))
        self.ordered_pattern_CE.set_parse_action(\
                lambda result: self.parse_ordered_pattern_CE(*result))
        self.template_pattern_CE.set_parse_action(\
                lambda result: self.parse_template_pattern_CE(**result))
        self.object_pattern_CE.set_parse_action(\
                lambda result: self.parse_object_pattern_CE(**result))
        self.assigned_pattern_CE.set_parse_action(\
                lambda result: self.parse_assigned_pattern_CE(**result))
        self.not_CE.set_parse_action(\
                lambda result: self.parse_not_CE(**result))
        self.and_CE.set_parse_action(\
                lambda result: self.parse_and_CE(**result))
        self.or_CE.set_parse_action(\
                lambda result: self.parse_or_CE(**result))
        self.logical_CE.set_parse_action(\
                lambda result: self.parse_logical_CE(**result))
        self.test_CE.set_parse_action(\
                lambda result: self.parse_test_CE(**result))
        self.exists_CE.set_parse_action(\
                lambda result: self.parse_exists_CE(**result))
        self.forall_CE.set_parse_action(\
                lambda result: self.parse_forall_CE(**result))
        self.constant.set_parse_action(\
                lambda result: self.parse_constant(*result))
        self.single_field_variable.set_parse_action(\
                lambda result: self.parse_single_field_variable(*result))
        self.multifield_variable.set_parse_action(\
                lambda result: self.parse_multifield_variable(*result))
        self.global_variable.set_parse_action(\
                lambda result: self.parse_global_variable(*result))
        self.function_call.set_parse_action(\
                lambda result: self.parse_function_call(*result))

        self.single_constraint.set_parse_action(\
                lambda result: self.parse_single_constraint(*result))
        self.single_negated_constraint.set_parse_action(\
                lambda result: self.parse_single_negated_constraint(*result))
        self.connected_constraint.set_parse_action(\
                lambda result: self.parse_connected_constraint(*result))
        self.single_wildcard.set_parse_action(\
                lambda result: self.parse_single_wildcard())
        self.multi_wildcard.set_parse_action(\
                lambda result: self.parse_multi_wildcard())


    @abc.abstractmethod
    def parse_defrule_construct(self, name,
                                conditionals: list, actions: list,
                                comment=None, declaration=None):
        """Base method to process defrule."""
        ...

    @abc.abstractmethod
    def parse_single_wildcard(self):
        ...
    @abc.abstractmethod
    def parse_multi_wildcard(self):
        ...

    @abc.abstractmethod
    def parse_connected_constraint(self, first_constraint,
                                   operator: ("&", "|", None) = None,
                                   second_constraint = None):
        ...

    @abc.abstractmethod
    def parse_single_constraint(self, term):
        ...

    @abc.abstractmethod
    def parse_single_negated_constraint(self, term):
        ...

    #def parse_action

    @abc.abstractmethod
    def parse_constant(self, constant:str) -> object:
        ...

    @abc.abstractmethod
    def parse_single_field_variable(self, symbol):
        ...
    @abc.abstractmethod
    def parse_multifield_variable(self, symbol):
        ...
    @abc.abstractmethod
    def parse_global_variable(self, symbol):
        ...

    @abc.abstractmethod
    def parse_function_call(self, functionname:str, *function_arguments)\
            -> list[object]:
        ...

    #@abc.abstractmethod
    #def parse_conditional_element
    @abc.abstractmethod
    def parse_ordered_pattern_CE(self, firstsymbol, *symbols) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_template_pattern_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_object_pattern_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_assigned_pattern_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_not_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_and_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_or_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_logical_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_test_CE(self, **args) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_exists_CE(self) -> tuple[object]:
        ...

    @abc.abstractmethod
    def parse_forall_CE(self) -> tuple[object]:
        ...
