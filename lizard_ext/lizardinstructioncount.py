"""
This extension counts operators in c++ source.
"""
from lizard_languages.code_reader import CodeStateMachine, CodeReader
from .extension_base import ExtensionBase
from instructions import *
from itertools import chain

from lizard_languages.clike import CLikeReader

def preprocess(self, tokens):
    #horrible inefficient hack to group derefs from whitespace
    for i, token in enumerate(tokens):
        if token is '*' or token is '&':
            if not tokens[i-1].isspace():
                tokens[i-1:i+1] = [tokens[i-1]+token]
            elif not tokens[i+1].isspace():
                tokens[i:i+2] = [token+tokens[i+1]]
    tilde = False
    for token in tokens:
        if token == '~':
            tilde = True
        elif tilde:
            tilde = False
            yield "~" + token
        elif not token.isspace() or token == '\n':
            macro = self.macro_pattern.match(token)
            if macro:
                if macro.group(1) in ('if', 'ifdef', 'elif'):
                    self.context.add_condition()
                elif macro.group(1) == 'include':
                    yield "#include"
                    yield macro.group(2) or "\"\""
                for _ in macro.group(2).splitlines()[1:]:
                    yield '\n'
            else:
                yield token

#CLikeReader.preprocess = preprocess

def operator_costs(instr):
    if instr == "++":
        return [Load(), Add(), Store()]
    if instr == "--":
        return [Load(), Sub(), Store()]
    if instr == "!":
        return [Load(), Cmp()]
    if instr == "~":
        return [Load(), Tilde()]
    if instr == "=":
        return [Store(), Load()]
    if instr == "+":
        return [Load(), Add(), Load()]
    if instr == "-":
        return [Load(), Sub(), Load()]
    if instr == "*":
        return [Load(), Mul(), Load()]
    if instr == "/":
        return [Load(), Div(), Load()]
    if instr == "%":
        return [Load(), Mod(), Load()]
    if instr == "+=":
        return [Store(), Load(), Add(), Load()]
    if instr == "-=":
        return [Store(), Load(), Sub(), Load()]
    if instr == "*=":
        return [Store(), Load(), Mul(), Load()]
    if instr == "/=":
        return [Store(), Load(), Div(), Load()]
    if instr == "%=":
        return [Store(), Load(), Mod(), Load()]
    if instr == "&":
        return [Load(), BitAnd(), Load()]
    if instr == "^":
        return [Load(), Exp(), Load()]
    if instr == "|":
        return [Load(), BitOr(), Load()]
    if instr == "&=":
        return [Store(), Load(), BitAnd(), Load()]
    if instr == "^=":
        return [Store(), Load(), Exp(), Load()]
    if instr == "|=":
        return [Store(), Load(), BitOr(), Load()]
    if instr == "<<":
        return [Load(), Shift(), Load()]
    if instr == "<<=":
        return [Store(), Load(), Shift(), Load()]
    if instr == ">>":
        return [Load(), Shift(), Load()]
    if instr == ">>=":
        return [Store(), Load(), Shift(), Load()]
    if instr == "==":
        return [Load(), Cmp(), Load()]
    if instr == "!=":
        return [Load(), Cmp(), Load()]
    if instr == ">":
        return [Load(), Cmp(), Load()]
    if instr == "<":
        return [Load(), Cmp(), Load()]
    if instr == ">=":
        return [Load(), Cmp(), Load()]
    if instr == "<=":
        return [Load(), Cmp(), Load()]
    if instr == "&&":
        return [Load(), Cmp(), Load(),Cmp()]
    if instr == "||":
        return [Load(), Cmp(), Load(),Cmp()]
    if instr == 'for':
        return [Load(), Cmp(), Jump()]
    if instr == 'if':
        return [Load(), Cmp(), Jump()]
    if instr == 'while':
        return [Load(), Cmp(), Jump()]
    if instr == '[':
        return [Load(), Load(), Add(), Add()]


class LizardExtension(ExtensionBase):  # pylint: disable=R0903
    """
    The purpose of this extension is to loosely estimate instructions from source code operators
    """

    FUNCTION_INFO = {"instruction_count": {"caption": "  INSTR  "}}

    general_register_ops = ["++", "--",
     "!", "~",
      "=", "+", "-", "*", "/",
       "%", "+=", "-=", "*=",
        "/=", "%=", "&", "^",
         "|", "&=", "^=", "|=",
          "<<", "<<=", ">>", ">>="]

    state_registers_ops = ["==",  "!=",  ">",  "<",  ">=",  "<=",  "&&",  "||"]

    conditional_ops = ['for', 'if', 'while']

    array_ops = ['[']

    ops = general_register_ops + state_registers_ops + conditional_ops + array_ops
    ops_string = ''.join(ops)

    def __init__(self, context=None):
        super(LizardExtension, self).__init__(context)
        self.total_instructions = 0

    def __call__(self, tokens, reader):
        self.context = reader.context
        reader.context.fileinfo.instructions = []
        reader.context.fileinfo.instruction_count = 0
        for token in tokens:
            if not hasattr(reader.context.current_function,
                               "instructions"):
                reader.context.current_function.instructions = []
                reader.context.current_function.instruction_count = 0
            self._state(token)
            yield token


    def _add_instruction(self,token,line_num):
        instrs = operator_costs(token)
        for instr in instrs:
            instr.line_num=line_num
        self.context.fileinfo.instructions = chain(self.context.fileinfo.instructions, instrs)
        self.context.current_function.instructions = chain(self.context.current_function.instructions, instrs)
        #self.context.fileinfo.instructions.extend(instrs)
        #self.context.current_function.instructions.extend(instrs)
        cost = len(instrs)
        self.context.fileinfo.instruction_count+=cost
        self.context.current_function.instruction_count+=cost

    def print_result(self):
        for instr in instructions:
            print(instr)
            print(instr.counter)

    def _state_global(self, token):
        if token in self.ops:
            self._add_instruction(token, self.context.current_line)

    @CodeStateMachine.read_until_then(ops_string+';')
    def _state_instr(self, token, rut):
        if token == ";":
            self.next(self._state_global)
        else:
            self._add_instruction(token, self.context.current_line)

    @staticmethod
    def set_args(parser):
        parser.add_argument(
            "--ISA",
            help='''Architecture ISA, default is BFIN.
            ''',
            type=str,
            dest="ISA",
            )

