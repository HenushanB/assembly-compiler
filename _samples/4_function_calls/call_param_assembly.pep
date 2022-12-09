    BR program
_UNIV:   .EQUATE 42
x:       .BLOCK 2


result:  .EQUATE 0
value:   .EQUATE 4

my_func: SUBSP 2,i
         LDWA value,s
         ADDA _UNIV,i
         STWA result,s
         DECO result,s 
         ADDSP 2,i
         RET
program: SUBSP 2,i
         DECI x,d
         LDWA x,d
         STWA 0,s
         CAll my_func
         ADDSP 2,i
         .END