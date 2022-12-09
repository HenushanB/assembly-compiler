import ast
from visitors.LocalVariables import LocalVariableExtraction
from generators.DynamicMemoryAllocation import DynamicMemoryAllocation


class GlobalVariableExtraction(ast.NodeVisitor):
    """
    We extract all the left hand side of the global (top-level) assignments
    """

    def __init__(self) -> None:
        super().__init__()
        self.results = {}
        self.symbol_table = {}
        self.local_results = {}
        self.local_memalloc = None

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        if (not node.targets[0].id in self.symbol_table) and (
            not node.targets[0].id in self.results
        ):
            if len(node.targets[0].id) <= 8:
                self.results[node.targets[0].id] = node.value
            else:
                if (
                    node.targets[0].id[0] == "_"
                    and node.targets[0].id[1:].isupper()
                ):
                    rename = "_UNIV" + str(len(self.symbol_table))
                    self.symbol_table[node.targets[0].id] = rename
                    self.results[rename] = node.value
                else:
                    rename = "VAR" + str(len(self.symbol_table))
                    self.symbol_table[node.targets[0].id] = rename
                    self.results[rename] = node.value

    def visit_FunctionDef(self, node):
        """We do not visit function definitions,
        they are not global by definition"""
        returnExists = False
        for content in node.body:
            if isinstance(content, ast.Return):
                returnExists = True
        self.local_var_extractor = LocalVariableExtraction(
            self.results, self.symbol_table, returnExists
        )
        self.local_var_extractor.visit(node.body)
        counter = self.local_var_extractor.counter
        self.local_memalloc = DynamicMemoryAllocation(
            self.local_var_extractor.results
        )
        self.local_memalloc.generate()
        for arg in node.args.args:
            print(
                f'{str(arg.arg+":"):<9}\t.EQUATE ' + str(counter)
            )  # reserving memory
            counter += 2
