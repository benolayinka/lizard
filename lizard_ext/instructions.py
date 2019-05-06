class Instruction(object):
    counter = 0
    def __init__(self, line_num = None):
        Instruction.counter += 1
        self.line_num = line_num
        self.operator = ''

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' Operator: ' + self.operator + ' Line: ' + str(self.line_num) + '>'

    def __str__(self):
        return self.__class__.__name__ + '\t' + self.operator + '\t' + str(self.line_num)

class ALU(Instruction):
    current = 301
    def __init__(self, line_num = None):
        ALU.counter += 1
        super(ALU, self).__init__(line_num)

class MAC(Instruction):
    current = 301
    def __init__(self, line_num = None):
        MAC.counter += 1
        super(MAC, self).__init__(line_num)

class SHIFT(Instruction):
    current = 300
    def __init__(self, line_num = None):
        SHIFT.counter += 1
        super(SHIFT, self).__init__(line_num)

class MOVE(Instruction):
    current = 301
    def __init__(self, line_num = None):
        MOVE.counter += 1
        super(MOVE, self).__init__(line_num)

class OTHER(Instruction):
    current = 290
    def __init__(self, line_num = None):
        OTHER.counter += 1
        super(OTHER, self).__init__(line_num)

class JUMP(Instruction):
    current = 311
    def __init__(self, line_num = None):
        JUMP.counter += 1
        super(JUMP, self).__init__(line_num)

class Store(MOVE):
    counter = 0
    def __init__(self, line_num = None):
        Store.counter += 1
        super(Store, self).__init__(line_num)

class Shift(SHIFT):
    counter = 0
    def __init__(self, line_num = None):
        Shift.counter += 1
        super(self.__class__, self).__init__(line_num)

class Mul(MAC):
    counter = 0
    def __init__(self, line_num = None):
        Mul.counter += 1
        super(self.__class__, self).__init__(line_num)

class Load(MOVE):
    counter = 0
    def __init__(self, line_num = None):
        Load.counter += 1
        super(self.__class__, self).__init__(line_num)

class Add(ALU):
    counter = 0
    def __init__(self, line_num = None):
        Add.counter += 1
        super(self.__class__, self).__init__(line_num)

class Sub(ALU):
    counter = 0
    def __init__(self, line_num = None):
        Sub.counter += 1
        super(self.__class__, self).__init__(line_num)

class Cmp(ALU):
    counter = 0
    def __init__(self, line_num = None):
        Cmp.counter += 1
        super(self.__class__, self).__init__(line_num)

class Tilde(ALU):
    counter = 0
    def __init__(self, line_num = None):
        Tilde.counter += 1
        super(self.__class__, self).__init__(line_num)

#DIV, MOD, EXP implemented in SW..

class Div(MAC):
    counter = 0
    def __init__(self, line_num = None):
        Div.counter += 1
        super(self.__class__, self).__init__(line_num)

class Mod(MAC):
    counter = 0
    def __init__(self, line_num = None):
        Mod.counter += 1
        super(self.__class__, self).__init__(line_num)

class Exp(MAC):
    counter = 0
    def __init__(self, line_num = None):
        Exp.counter += 1
        super(self.__class__, self).__init__(line_num)

class BitAnd(ALU):
    counter = 0
    def __init__(self, line_num = None):
        BitAnd.counter += 1
        super(self.__class__, self).__init__(line_num)

class BitOr(ALU):
    counter = 0
    def __init__(self, line_num = None):
        BitOr.counter += 1
        super(self.__class__, self).__init__(line_num)

class Jump(JUMP):
    counter = 0
    def __init__(self, line_num = None):
        Jump.counter += 1
        super(self.__class__, self).__init__(line_num)

instructions = [ALU, MAC, SHIFT, MOVE, OTHER, JUMP, Store, Shift, Mul, Load, Add, Sub, Cmp, Tilde, Div, Mod, Exp, BitAnd, BitOr, Jump]