'''
Language parser for Go lang
'''

from .code_reader import CodeReader, CodeStateMachine
from .clike import CCppCommentsMixin

class ASMReader(CodeReader, CCppCommentsMixin):
    # pylint: disable=R0903

    ext = ['s']
    language_names = ['asm']

    def __init__(self, context):
        super(ASMReader, self).__init__(context)
        self.parallel_states = [ASMStates(context)]
        self.context.instruction_count = 0

class ASMStates(CodeStateMachine):  # pylint: disable=R0903
    def _state_global(self, token):
        if token.startswith('.'):
            self._state = self._dot
        elif token.startswith('_'):
            self._state = self._underscore
        else:
            self.context.start_new_function(token)
            self._state = self._instruction

    @CodeStateMachine.read_until_then(';:\n')
    def _dot(self, token, _):
        self._state = self._state_global

    @CodeStateMachine.read_until_then(r':;\n')
    def _underscore(self, token, _):
        self._state = self._state_global

    @CodeStateMachine.read_until_then(r';:\n')
    def _instruction(self, _, tokens):
        self.context.instruction_count+=1
        self.context.add_to_function_name(''.join(tokens))
        self.context.end_of_function()
        self.next(self._state_global)
