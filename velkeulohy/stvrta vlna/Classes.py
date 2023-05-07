from enum import Enum


class BasicObjT(Enum):
    Val = 1
    Var = 2


class SimpleObj:

    def __init__(self, t, value):
        self.type = t
        self.value = value

    def __str__(self):
        return str(self.value)

    def eval(self, variable_map):
        if self.type == BasicObjT.Val:
            return self.value
        if self.type == BasicObjT.Var:
            value = variable_map[self.value]
            if value:
                return value
            raise RuntimeError(f"Variable {self.value} not initialized")
        raise RuntimeError(f"Unknown value type {self.type}")


class BinOP:

    def __init__(self, op, l, r):
        self.op = op if op != "=" else "=="
        self.left = l
        self.right = r

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def eval(self, variable_map):
        ls = self.left.eval(variable_map)
        rs = self.right.eval(variable_map)
        if self.op == "+":
            return ls + rs
        if self.op == "-":
            return ls - rs
        if self.op == "*":
            return ls * rs
        if self.op == "/":
            return ls / rs
        if self.op == "<":
            return ls < rs
        if self.op == ">":
            return ls > rs
        if self.op == "==":
            return ls == rs
        raise RuntimeError(f"Unsupported operator {self.op}")


class CommandT(Enum):
    Assign = 1
    Print = 2
    Read = 3
    Jmp = 4


class Command:

    def __init__(self, t, r, l = None):
        self.type = t
        self.right = r
        self.left = l  # only useful for the jump command

    def __str__(self):
        if self.type == CommandT.Assign:
            return f"{self.left} := {self.right}\n"
        if self.type == CommandT.Print:
            return f"PRINT {self.right}\n"
        if self.type == CommandT.Read:
            return f"READ {self.right}\n"
        return f"JMP [{self.left}] {self.right}\n"

    def eval(self, variable_map):
        if self.type == CommandT.Assign:
            if self.left.type != BasicObjT.Var:
                raise RuntimeError("Assigning value to non-variable")
            variable_name = self.left.value
            value = self.right.eval(variable_map)
            variable_map[variable_name] = value
        elif self.type == CommandT.Print:
            value = self.right.eval(variable_map)
            print(value)
        elif self.type == CommandT.Read:
            if self.right.type != BasicObjT.Var:
                raise RuntimeError("READ parameter type mismatch")
            variable_name = self.right.value
            value = input()
            variable_map[variable_name] = value
        elif self.type == CommandT.Jmp:
            condition = self.left.eval(variable_map)
            if condition:
                return self.right
        else:
            raise RuntimeError(f"Unsupported command {self.type}")


class Block:
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands

    def __str__(self):
        result = f"BLOCK {self.name}" + "{\n"
        for command in self.commands:
            result += f" {command}"
        return result + "}"

    def eval(self, variable_map):
        for command in self.commands:
            block_name = command.eval(variable_map)
            if block_name:
                return block_name


class Program:
    def __init__(self, parts):
        self.parts = parts
        # dictionary in the form {block_name : Block}

    def __str__(self):
        result = ""
        for part in self.parts.values():
            result += f"{part}\n"
        return result

    def eval(self):
        variable_map = {}
        block_name = "main"
        while block_name:
            block = self.parts.get(block_name)
            if not block:
                raise RuntimeError(f"Block {block_name} not found")
            block_name = block.eval(variable_map)
