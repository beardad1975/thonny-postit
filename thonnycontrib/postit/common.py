from typing import NamedTuple


ENTER = '\u23ce'


#symbol data
class Symbol(NamedTuple):
    code: str
    note: str
    enclosed: bool

#all symbol nametuple dictionay 
symbol_nt_dict = {}
symbol_nt_dict['+'] = Symbol('+', '加', False)
symbol_nt_dict['-'] = Symbol('-', '減', False)
symbol_nt_dict['*'] = Symbol('*', '乘', False)
symbol_nt_dict['/'] = Symbol('/', '除', False)

symbol_nt_dict['='] = Symbol('=', '指定', False)
symbol_nt_dict['‧'] = Symbol('‧', '點', False)
symbol_nt_dict[','] = Symbol(',', '逗號', False)
