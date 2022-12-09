class DynamicMemoryAllocation:
    def __init__(self, local_vars: dict()) -> None:
        self.__local_vars = local_vars

    def generate(self):
        print("; Allocating local (dynamic) memory")
        for n in self.__local_vars.keys():
            print(
                f'{str(n+":"):<9}\t.EQUATE ' + str(self.__local_vars[n])
            )  # reserving memory
