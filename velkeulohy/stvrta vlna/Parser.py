from Classes import BasicObjT, Block, BinOP, Command, CommandT, Program, SimpleObj
from typing import List

Token = str


class Stack:
    def __init__(self, tokens) -> None:
        self.ls: List[Token] = tokens

    def push(self, token: Token):
        self.ls.append(token)

    def pop(self) -> Token:
        return self.ls.pop() if (len(self.ls) > 0) else ""

    def is_empty(self) -> bool:
        return len(self.ls) == 0


class Parser:

    def __init__(self, code):
        self.tokens = self.tokenize(code)

    def tokenize(self, code) -> Stack:
        delimiters = {
            "{", "}", "[", "]", ">", "<", "=", "*", "/", "+", "-", ";"
        }
        tokens = []
        token = ""
        for letter in code:
            if letter.isspace():
                if token:
                    tokens.append(token)
                    token = ""
            else:
                if letter in delimiters:
                    if token == ":":
                        tokens.append(token + letter)
                    else:
                        if token:
                            tokens.append(token)
                        tokens.append(letter)
                    token = ""
                else:
                    token += letter
        if token:
            tokens.append(token)

        stack = Stack(list(reversed(tokens)))
        return stack

    def Parse(self):
        program = self.P()
        return program

    def P(self):
        blocks = {}
        while not self.tokens.is_empty():
            if self.tokens.pop() != "BLOCK":
                raise TypeError("P: BLOCK is expected")
            block_name = self.tokens.pop()
            if self.tokens.pop() != "{":
                raise TypeError("P: { is expected after BLOCK Name")
            block = self.B()
            if not block:
                raise TypeError("P: B is expected after BLOCK Name {")
            if self.tokens.pop() != "}":
                raise TypeError("P: } is expected after BLOCK Name { B")
            blocks[block_name] = Block(block_name, block)

        return Program(blocks)

    def B(self):
        commands = []
        c = self.C()
        while c:
            commands.append(c)
            delimiter = self.tokens.pop()
            if delimiter == ";":
                c = self.C()
                if not c:
                    raise TypeError("B: C is expected after ;")
            else:
                self.tokens.push(delimiter)
                break
        return commands

    def C(self):
        command = self.tokens.pop()
        if command == "PRINT":
            f = self.F()
            if not f:
                raise TypeError("C: F is expected after PRINT")
            return Command(CommandT.Print, f)
        if command == "READ":
            v = self.Variable()
            if not v:
                raise TypeError("C: Var is expected after READ")
            return Command(CommandT.Read, v)
        if command == "JMP":
            if self.tokens.pop() != "[":
                raise TypeError("C: [ is expected after JMP")
            be = self.BE()
            if not be:
                raise TypeError("C: BE is expected after JMP [")
            if self.tokens.pop() != "]":
                raise TypeError("C: ] is expected after JMP [BE")
            block_name = self.tokens.pop()
            if not block_name:
                raise TypeError("C: Name is expected after JMP [BE]")
            return Command(CommandT.Jmp, block_name, be)
        self.tokens.push(command)

        v = self.Variable()
        if not v:
            raise TypeError("C: No command found")
        if self.tokens.pop() != ":=":
            raise TypeError("C: := is expexted after Var")
        e = self.E()
        if not e:
            raise TypeError("C: E is expexted after Var :=")
        return Command(CommandT.Assign, e, v)

    def BE(self):
        le = self.E()
        if not le:
            return None
        op = self.OP(["<", ">", "="])
        if not op:
            raise TypeError("BE: OP is expected after E")
        re = self.E()
        if not re:
            raise TypeError("BE: E is expected after OP")
        return BinOP(op, le, re)

    def E(self):
        ls = self.T()
        if not ls:
            return None
        op = self.OP(["+", "-"])
        while op:
            rs = self.T()
            if not rs:
                raise TypeError("E: T is expected after OP")
            ls = BinOP(op, ls, rs)
            op = self.OP(["+", "-"])
        return ls

    def T(self):
        ls = self.F()
        if not ls:
            return None
        op = self.OP(["*", "/"])
        while op:
            rs = self.F()
            if not rs:
                raise TypeError("T: F is expected after OP")
            ls = BinOP(op, ls, rs)
            op = self.OP(["*", "/"])
        return ls

    def OP(self, operators):
        token = self.tokens.pop()
        if token in operators:
            return token
        self.tokens.push(token)
        return None

    def F(self):
        result = self.Int()
        if result:
            return result
        result = self.Variable()
        return result

    def Int(self):
        token = self.tokens.pop()
        if token.isdecimal():
            return SimpleObj(BasicObjT.Val, int(token))
        self.tokens.push(token)
        return None

    def Variable(self):
        token = self.tokens.pop()
        if token.isascii:
            return SimpleObj(BasicObjT.Var, token)
        self.tokens.push(token)
        return None


# Example:
P = Parser("BLOCK main {x := 4; PRINT x; JMP [x - 2 + 2 > x - 2] otter} BLOCK other {y := 9*x + 56; PRINT y} BLOCK otter {JMP [8 - 2 * 2 - 2 * 2 = 0] other}")
parsed = P.Parse()
print(parsed)
# print("-----------------")
parsed.eval()
