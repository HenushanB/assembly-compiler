import ast


class StaticMemoryAllocation:
    def __init__(self, global_vars: dict()) -> None:
        self.__global_vars = global_vars

    def generate(self):
        print("; Allocating Global (static) memory")
        for n in self.__global_vars.keys():
            if len(n) >= 2 and n[0] == "_" and n[1:].isupper():
                print(
                    f'{str(n+":"):<9}\t.EQUATE '
                    + str(self.__global_vars[n].value)
                )  # reserving memory
            elif isinstance(
                self.__global_vars[n], ast.Constant
            ) and isinstance(self.__global_vars[n].value, int):
                print(
                    f'{str(n+":"):<9}\t.WORD '
                    + str(self.__global_vars[n].value)
                )  # reserving memory
            else:
                print(f'{str(n+":"):<9}\t.BLOCK 2')  # reserving memory
