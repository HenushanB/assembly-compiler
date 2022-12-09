         BR program
_UNIV:           .WORD 42
variable:        .WORD 3
tempOne:         .WORD 1
value:           .BLOCK 2
result:          .BLOCK 2
program:         DECI value,d
                 LDWA _UNIV,d 
                 ADDA value,d
                 SUBA variable,d
                 SUBA tempOne,d
                 STWA result,d
                 DECO result,d
                 .END