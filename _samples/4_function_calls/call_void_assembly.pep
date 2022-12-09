    BR program
_UNIV:   .EQUATE 42

result:  .EQUATE 0
value:   .EQUATE 2

my_func: SUBSP 4,i
         DECI value,s
         LDWA value,s
         ADDA _UNIV,i
         STWA result,s
         DECO result,s
         ADDSP 4,i
         RET
program: CALL my_func
         .END