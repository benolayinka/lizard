class Instruction(object):
    counter = 0
    def __init__(self, line_num = None):
        Instruction.counter += 1
        self.line_num = line_num

class Store(Instruction):
    counter = 0
    current = 200
    def __init__(self, line_num = None):
        Store.counter += 1
        super(Store, self).__init__(line_num)

class Shift(Instruction):
    counter = 0
    current = 300
    def __init__(self, line_num = None):
        Shift.counter += 1
        super(self.__class__, self).__init__(line_num)

class Mul(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Mul.counter += 1
        super(self.__class__, self).__init__(line_num)

class Load(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Load.counter += 1
        super(self.__class__, self).__init__(line_num)

class Add(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Add.counter += 1
        super(self.__class__, self).__init__(line_num)

class Sub(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Sub.counter += 1
        super(self.__class__, self).__init__(line_num)

class Cmp(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Cmp.counter += 1
        super(self.__class__, self).__init__(line_num)

class Tilde(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Tilde.counter += 1
        super(self.__class__, self).__init__(line_num)

class Div(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Div.counter += 1
        super(self.__class__, self).__init__(line_num)

class Mod(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Mod.counter += 1
        super(self.__class__, self).__init__(line_num)

class Exp(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Exp.counter += 1
        super(self.__class__, self).__init__(line_num)

class BitAnd(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        BitAnd.counter += 1
        super(self.__class__, self).__init__(line_num)

class BitOr(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        BitOr.counter += 1
        super(self.__class__, self).__init__(line_num)

class Jump(Instruction):
    counter = 0
    def __init__(self, line_num = None):
        Jump.counter += 1
        super(self.__class__, self).__init__(line_num)

instructions = [Store, Shift, Mul, Load, Add, Sub, Cmp, Tilde, Div, Mod, Exp, BitAnd, BitOr, Jump]