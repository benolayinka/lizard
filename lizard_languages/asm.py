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

    def preprocess(self, tokens):
        #return (t for t in tokens if not t.isspace())
        for token in tokens:
            if not token.isspace():
                print [token]
                yield token

class ASMStates(CodeStateMachine):  # pylint: disable=R0903
    def _state_global(self, token):
        print "global" + token
        if token == '.':
            print "entering dot"
            #return self.next(self._dot, token)
            self._state = self._dot
        elif token == '_':
            print "entering underscore"
            self._state = self._underscore
        else:
            print "entering instruction" + token
            self.context.start_new_function(token)
            self._state = self._instruction

    @CodeStateMachine.read_until_then(r';\n')
    def _dot(self, token, _):
        print "rut" + str(_)
        print "exiting dot" + token
        self._state = self._state_global

    @CodeStateMachine.read_until_then(r';\n')
    def _underscore(self, token, _):
        print "exiting underscore" + token
        self._state = self._state_global

    @CodeStateMachine.read_until_then(r';\n')
    def _instruction(self, token, tokens):
        self.context.add_to_function_name(token)
        self.next(self._state_global)

    @CodeStateMachine.read_inside_brackets_then("()", '_function_name')
    def _member_function(self, tokens):
        self.context.add_to_long_function_name(tokens)

    @CodeStateMachine.read_inside_brackets_then("()", '_expect_function_impl')
    def _function_dec(self, token):
        if token not in '()':
            self.context.parameter(token)

    def _expect_function_impl(self, token):
        self.next_if(self._function_impl, token, '{')

    @CodeStateMachine.read_inside_brackets_then("{}")
    def _function_impl(self, _):
        self._state = self._state_global
        self.context.end_of_function()
