"""
This extension counts operators in c++ source.
"""
from lizard_languages.code_reader import CodeStateMachine, CodeReader
from .extension_base import ExtensionBase
from .instructions import *
from itertools import chain

from lizard_languages.clike import CLikeReader
from lizard import Nesting, BARE_NESTING

debug = False

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

class ConditionalStack(list):
    def __init__(self):
        self.pending_condition = None

    def start_condition(self, condition):
        self.pending_condition = condition

    def create_condition(self):
        tmp = self.pending_condition
        self.pending_condition = None
        self.append(tmp)
        return tmp

class ConditionalInfo(Nesting):  # pylint: disable=R0902

    def __init__(self, name, parent, start_line=0):
        self.name = name
        self.long_name = name
        self.start_line = start_line
        self.end_line = start_line
        self.instructions = []
        self.instruction_count = 0
        self.parent = parent
        self.top_nesting_level = -1
        self.length = 0
        self.children = ConditionalStack()

    @property
    def name_in_space(self):
        return self.name + "."

    @property
    def unqualified_name(self):
        '''
        name without qualification like namespaces or classes.
        Just the bare name without '::'.
        '''
        return self.name.split('::')[-1]

    location = property(lambda self:
                        " %(name)s@%(start_line)s-%(end_line)s@%(filename)s"
                        % self.__dict__)

    condition_count = property(lambda self: len(self.conditions))

    def add_to_name(self, app):
        self.name += app
        self.long_name += app

    def add_to_long_name(self, app):
        if self.long_name:
            if self.long_name[-1].isalpha() and app[0].isalpha():
                self.long_name += ' '
        self.long_name += app

    def add_condition(self, condition):
        self.add_to_long_name(" " + condition)

        if not self.conditions or condition == ",":
            self.conditions.append(condition)
        else:
            self.conditions[-1] = condition


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
        self.current_condition = None

    def __call__(self, tokens, reader):

        def preprocess_tokens():
            #horrible inefficient hack to group derefs from whitespace
            for i, token in enumerate(tokens):
                if token is '*' or token is '&':
                    if not tokens[i-1].isspace():
                        tokens[i-1:i+1] = [tokens[i-1]+token]
                    elif not tokens[i+1].isspace():
                        tokens[i:i+2] = [token+tokens[i+1]]

        self.context = reader.context
        for token in tokens:
            current_function = self.context.current_function
            if not hasattr(current_function,
                               "instructions"):
                current_function.instructions = []
                current_function.instruction_count = 0
            if not hasattr(current_function,
                               "conditional_info"):
                current_function.conditional_info = ConditionalInfo(current_function.name, current_function, current_function.start_line)
                self.current_condition = current_function.conditional_info
                if debug:
                    print('current function: ')
                    print(current_function)
                    print(current_function.__dict__)
                    print(token)
            self._state(token)
            yield token

    def _add_instruction(self,token):
        if debug:
            print('instruction found at ' + str(self.context.current_line))
            print(token)
        instrs = operator_costs(token)

        for instr in instrs:
            instr.line_num=self.context.current_line
            instr.operator = token

        self.current_condition.instructions.extend(instrs)
        #self.current_condition.instructions = chain(self.current_condition.instructions, instrs)
        #self.context.fileinfo.instructions.extend(instrs)
        #self.context.current_function.instructions.extend(instrs)
        cost = len(instrs)
        self.current_condition.instruction_count+=cost

        #ben added to include operators in conditional both in parent and child
        pending = self.current_condition.children.pending_condition
        if pending:
            pending.instructions.extend(instrs)
            pending.instruction_count+=cost

        if debug:
            self.total_instructions+=1
            print(self.total_instructions)

    def _open_conditional(self, token):
        self.current_condition.children.start_condition(
            ConditionalInfo(
            token,
            self.current_condition,
            self.context.current_line)
            )

    def _add_conditional(self):
        current_function = self.context.current_function

        self.current_condition = self.current_condition.children.create_condition()

        self.current_condition.top_nesting_level = self.context.current_nesting_level
        if debug:
            print('conditional ' + self.current_condition.name + ' at ' + str(self.context.current_line))
            print('current condition: ')
            print(self.current_condition)
            print(self.current_condition.__dict__)
            print('parent condition: ')
            print(self.current_condition.parent)
            print(self.current_condition.parent.__dict__)

    def _state_global(self, token):
        if token in self.conditional_ops:
            self._open_conditional(token)
            self._state = self._state_conditional
        if token in self.ops:
            self._add_instruction(token)
        if token == '}':
            if self.context.current_nesting_level-1 == self.current_condition.top_nesting_level:
                #pop
                self.current_condition.end_line = self.context.current_line
                self.current_condition = self.current_condition.parent
            if debug:
                print('nesting level at ' + str(self.context.current_line))
                print(self.context.current_nesting_level)
                print('current condition: ')
                print(self.current_condition)
                print(self.current_condition.__dict__)

    def _state_conditional(self, token):
        if token == '(':
            self._state = self._state_dec
        else:
            self._state = self._state_global

    def _state_dec(self, token):
        if token == ')':
            self.next(self._state_begin)
        elif token in self.ops:
            self._add_instruction(token)
            self.current_condition.children.pending_condition.add_to_long_name(token)
        elif token in ['&', '&&', '|', '||']:
            #todo - conditional params
            if debug:
                print('multiple conditions!')
            self.current_condition.children.pending_condition.add_to_long_name(token)
        else:
            self.current_condition.children.pending_condition.add_to_long_name(token)

    def _state_begin(self, token):
        if token == '{':
            self._add_conditional()
            self._state = self._state_global

    @CodeStateMachine.read_until_then(ops_string+';')
    def _state_instr(self, token, rut):
        if token == ";":
            self.next(self._state_global)
        else:
            self._add_instruction(token, self.context.current_line)

    def print_result(self):
        for function in self.context.fileinfo.function_list:
            function.instruction_count, function.instructions = self.get_children_instruction_count(function.conditional_info, True)
            print('Total instructions: ' + str(function.instruction_count))
            name = function.name + '_lizard_estimate.txt'
            with open(name, 'w') as f:
                f.write(function.name)
                f.write(' total instruction_count: ')
                f.write(str(function.instruction_count))
                f.write('\n')
                total_current=0
                instrs=''
                for instr in function.instructions:
                    total_current+=instr.current
                    instrs += (str(instr))
                    instrs += '\n'
                f.write('Avg current: ')
                f.write(str(total_current/function.instruction_count))
                f.write('\n')
                f.write('Instr\tOp\tLine\n')
                f.write(instrs)

        if debug:
            for instr in instructions:
                print(instr)
                print(instr.counter)

    def get_children_instruction_count(self, conditional_root, user = False):
        instructions = []
        instruction_count = 0
        exc = 1
        if user:
            exc = int(input('# executions: (' + conditional_root.long_name + ') ? '))
        instruction_count += exc * conditional_root.instruction_count
        instructions.extend(exc * conditional_root.instructions)
        for cond in conditional_root.children:
            instruction_count_children, instructions_children = self.get_children_instruction_count(cond, user)
            instruction_count += instruction_count_children
            instructions.extend(instructions_children)
        return instruction_count, instructions

    def cross_file_process(self, fileinfos):
        for fileinfo in fileinfos:
            for func in fileinfo.function_list:
                func.instruction_count, dummy = self.get_children_instruction_count(func.conditional_info)
            yield fileinfo

    @staticmethod
    def set_args(parser):
        parser.add_argument(
            "-u",
            help='''User input for path tracing
            ''',
            type=str,
            dest="u",
            )

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
        return [Jump()]
    if instr == 'if':
        return [Jump()]
    if instr == 'while':
        return [Jump()]
    if instr == '[':
        return [Load()]