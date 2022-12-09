import ast


class LocalVariableExtraction(ast.NodeVisitor):
    """
    We extract all the local variables inside the functions
    """

    def __init__(self, globals, global_symbols, return_exists) -> None:
        super().__init__()
        self.local_results = {}
        self.local_symbol_table = {}
        self.parent_globals = globals
        self.parent_global_symbols = global_symbols
        self.return_exists = return_exists
        self.counter = 0

    def visit_Assign(self, node):
        if len(node.targets[0].id) != 1:
            raise ValueError("Only unary assignments are supported")

        if (
            (not node.targets[0].id in self.local_symbol_table)
            and (not node.targets[0].id in self.local_results)
            and not (node.targets[0].id in self.parent_global_symbols)
            and not (node.targets[0].id in self.parent_globals)
        ):

            rename = "loc" + str(len(self.local_symbol_table))
            self.local_symbol_table[node.targets[0].id] = rename
            if self.counter == 2:
                self.counter += 2
            self.local_results[rename] = self.counter
            self.counter += 2

    def visit_Return(self, node):
        rename = "ret_func"
        self.local_symbol_table[node.value.id] = rename
        self.local_results[rename] = "0"
