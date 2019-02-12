"""
This extension counts operators in c++ source.
"""

from .extension_base import ExtensionBase


DEFAULT_ISA = "bfin"

instruction_costs = {
    "++":3,
     "--":3,
     "+( )":0,
     "-( )":1,
     "!( )":3,
     "~( )":1,
     "=":2,
     "+":2,
     "-":2,
     "*":2,
     "/":10,
     "%":30,
     "+=":3,
     "-=":3,
     "*=":3,
     "/=":13,
     "%=":16,
     "&":2,
     "^":2,
     "|":2,
     "&=":3,
     "^=":3,
     "|=":3,
     "<<":2,
     "<<=":3,
     ">>":2,
     ">>=":3,
     "==":2, #ben same as greater than
     "!=":3,
     ">":3,
     "<":3,
     ">=":3,
     "<=":3,
     "&&":1,
     "||":1,
    }


class LizardExtension(object):  # pylint: disable=R0903
    """
    The purpose of this extension is to loosely estimate instructions from source code operators
    """

    FUNCTION_INFO = {"instruction_count": {"caption": "  INSTR  "}}

    general_register_ops = ["++", "--", "+( )",
     "-( )", "!( )", "~( )",
      "=", "+", "-", "*", "/",
       "%", "+=", "-=", "*=",
        "/=", "%=", "&", "^",
         "|", "&=", "^=", "|=",
          "<<", "<<=", ">>", ">>="]

    state_registers_ops = ["==",  "!=",  ">",  "<",  ">=",  "<=",  "&&",  "||"]

    extra_symbols = general_register_ops + state_registers_ops

    @staticmethod
    def set_args(parser):
        parser.add_argument(
            "--ISA",
            help='''Architecture ISA, default is %s.
            ''' % DEFAULT_ISA,
            type=str,
            dest="ISA",
            default=DEFAULT_ISA)

    def __init__(self):
        self.total_instructions = 0

    def _add_instruction(self, reader, token):
        instruction_cost = instruction_costs.get(token, 0)
        reader.context.fileinfo.instruction_count += instruction_cost
        reader.context.current_function.instruction_count += instruction_cost
        #if instruction_cost:
        #    print reader.context.current_function.name
        #    print token

    def __call__(self, tokens, reader):
        reader.context.fileinfo.instruction_count = 0
        for token in tokens:
            if not hasattr(reader.context.current_function,
                               "instruction_count"):
                reader.context.current_function.instruction_count = 0
            self._add_instruction(reader, token)
            yield token

    def cross_file_process(self, fileinfos):
        '''
        Combine the statistics from each file.
        '''
        for fileinfo in fileinfos:
            if hasattr(fileinfo, "instruction_count"):
                self.total_instructions += fileinfo.instruction_count
            yield fileinfo

    def print_result(self):
        print("Total instructions:", self.total_instructions)
