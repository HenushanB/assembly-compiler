import ast

LabeledInstruction = tuple[str, str]


class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self, entry_point) -> None:
        super().__init__()
        self.__instructions = list()
        self.__record_instruction("NOP1", label=entry_point)
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        self.__should_assign = True
        self.__visited = {}
        self.__func_vars = set()

        self.inverted = {
            ast.Lt: "BRGE",  # '<'  in the code means we branch if '>='
            ast.LtE: "BRGT",  # '<=' in the code means we branch if '>'
            ast.Gt: "BRLE",  # '>'  in the code means we branch if '<='
            ast.GtE: "BRLT",  # '>=' in the code means we branch if '<'
            ast.NotEq: "BREQ",  # '!=' in the code means we branch if '=='
            ast.Eq: "BRNE",  # '!=' in the code means we branch if '=='
        }

    def finalize(self):
        self.__instructions.append((None, ".END"))
        return self.__instructions

    def get_global_results(self, symbol):
        self.__symbol_table = symbol

    ####
    # Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        self.__current_variable = node.targets[0].id
        self.__variable_name_in_pep9 = self.__current_variable
        if self.__current_variable in self.__symbol_table:
            self.__variable_name_in_pep9 = self.__symbol_table[
                self.__current_variable
            ]
        temp_val = node.value

        # visiting the left part, now knowing where to store the result

        if (
            not (self.__current_variable in self.__visited)
            and self.__should_assign
            and isinstance(temp_val, ast.Constant)
            and not self.check_univ(self.__current_variable)
        ):
            self.__visited[self.__current_variable] = True
            self.__current_variable = None
            self.__variable_name_in_pep9 = None
            return

        self.visit(node.value)
        if self.__should_save:
            self.__record_instruction(f"STWA {self.__variable_name_in_pep9},d")
        else:
            self.__should_save = True
        self.__current_variable = None
        self.__variable_name_in_pep9 = None

    def visit_Constant(self, node):
        self.__record_instruction(f"LDWA {node.value},i")

    def check_univ(self, n):
        return len(n) >= 2 and n[0] == "_" and n[1:].isupper()

    def visit_Name(self, node):
        if len(node.id) >= 2 and node.id[0] == "_" and node.id[1:].isupper():
            self.__record_instruction(f"LDWA {node.value},i")
        else:
            if node.id in self.__symbol_table:
                self.__record_instruction(
                    f"LDWA {self.__symbol_table[node.id]},d"
                )
            else:
                self.__record_instruction(f"LDWA {node.id},d")

    def visit_BinOp(self, node):
        self.__access_memory(node.left, "LDWA")
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, "ADDA")
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, "SUBA")
        else:
            raise ValueError(f"Unsupported binary operator: {node.op}")

    def visit_Call(self, node):
        match node.func.id:
            case "int":
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case "input":
                # We are only supporting integers for now
                self.__record_instruction(
                    f"DECI {self.__variable_name_in_pep9},d"
                )
                self.__should_save = (
                    False  # DECI already save the value in memory
                )
            case "print":
                # We are only supporting integers for now
                temp_id = node.args[0].id
                if temp_id in self.__symbol_table:
                    self.__record_instruction(
                        f"DECO {self.__symbol_table[temp_id]},d"
                    )
                else:
                    self.__record_instruction(f"DECO {temp_id},d")
            case _:
                raise ValueError(f"Unsupported function call: {node.func.id}")

    ####
    # Handling While loops (only variable OP variable)
    ####

    def visit_If(self, node):
        condition_id = self.__identify()
        # left part can only be a variable
        self.__access_memory(
            node.test.left, "LDWA", label=f"test_{condition_id}"
        )
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], "CPWA")
        # Branching is condition is not true (thus, inverted)
        if len(node.orelse) > 0:
            self.__record_instruction(
                f"{self.inverted[type(node.test.ops[0])]} else_{condition_id}"
            )
        else:
            self.__record_instruction(
                f"{self.inverted[type(node.test.ops[0])]} end_{condition_id}"
            )

        self.__record_instruction(f"NOP1", label=f"if_{condition_id}")
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f"BR end_{condition_id}")
        if len(node.orelse) > 0:
            self.__record_instruction(f"NOP1", label=f"else_{condition_id}")
            for contents in node.orelse:
                self.visit(contents)
        self.__record_instruction(f"NOP1", label=f"end_{condition_id}")

        # self.__record_instruction(f"BR test_{condition_id}")
        # # Sentinel marker for the end of the loop
        # self.__record_instruction(f"NOP1", label=f"end_2_{condition_id}")

    def visit_While(self, node):
        loop_id = self.__identify()
        # left part can only be a variable
        self.__access_memory(node.test.left, "LDWA", label=f"test_{loop_id}")
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], "CPWA")
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(
            f"{self.inverted[type(node.test.ops[0])]} end_l_{loop_id}"
        )
        # Visiting the body of the loop
        order = self.__should_assign
        self.__should_assign = False
        for contents in node.body:
            self.visit(contents)
        self.__should_assign = order
        self.__record_instruction(f"BR test_{loop_id}")
        # Sentinel marker for the end of the loop
        self.__record_instruction(f"NOP1", label=f"end_l_{loop_id}")

    ####
    # Not handling function calls
    ####

    def visit_FunctionDef(self, node):

        func_id = node.name
        return_statement = 0
        local_var_count = 0
        for content in node.body:
            if isinstance(content, ast.Return):
                return_statement = 1
                return_var = content.value.id

    ####
    # Helper functions to
    ####

    def __record_instruction(self, instruction, label=None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f"{instruction} {node.value},i", label)
        else:
            if node.id in self.__symbol_table:
                self.__record_instruction(
                    f"{instruction} {self.__symbol_table[node.id]},d", label
                )
            else:
                self.__record_instruction(f"{instruction} {node.id},d", label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result
