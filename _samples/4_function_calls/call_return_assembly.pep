    BR program
_UNIV:   .EQUATE 42
x:       .BLOCK 2
result:  .BLOCK 2

result1:  .EQUATE 0 
value:   .EQUATE 4
retVal:  .EQUATE 6

my_func: SUBSP 2, i         
         LDWA value, s
         ADDA _UNIV, i
         STWA result1, s
         LDWA result1, s
         STWA retVal, s
         ADDSP 2,i
         RET 
program: SUBSP 4,i
         DECI x, d
         LDWA x, d
         STWA 0, s
         CALL my_func
         ADDSP 2,i
         LDWA result1, s
         STWA result, d
         ADDSP 2,i
         DECO result, d
         .END