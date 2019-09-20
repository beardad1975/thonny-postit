from typing import NamedTuple
from keyword import iskeyword






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

class VariableNameError(Exception):pass
class VariableKeyError(Exception):pass

class VariableSet():
    def __init__(self):
        self._custom_set = set()
        self._runtime_and_custom_set = set()  

    def __repr__(self):
        print("all  set: ",self._runtime_and_custom_set)
        print("custom set: ", self._custom_set)


    def __iter__(self):
        return iter(self._runtime_and_custom_set)

    def get_custom_set(self):
        return self._custom_set

    def get_runtime_set(self):
        return self._runtime_and_custom_set - self._custom_set


    def add(self, var_name):
        self.check_name()
        self._runtime_and_custom_set.add(var_name)
        self._custom_set.add(var_name)

    def remove(self, var_name):
        self.check_name()
        if not var_name in self._runtime_and_custom_set:
            raise VariableKeyError('Variable is not a member!')

        self._runtime_and_custom_set.discard(var_name)
        self._custom_set.discard(var_name)

    def clear_all(self):
        self._runtime_and_custom_set.clear()
        self._custom_set.clear()

    def clear_runtime(self):
        self._runtime_and_custom_set &= self._custom_set    

    def clear_custom(self):
        self._runtime_and_custom_set -= self._custom_set
        self._custom_set.clear()

    def runtime_update(self, list_):
        self._runtime_and_custom_set.update(set(list_))
        
    def check_name(self, name):
        #raise exception if not a valid identifier
        assert isinstance(name, str), raise TypeError('Not a string type!')

        if not name.isidentifier():
            raise VariableNameError('Not a valid variable name!')
        
        if iskeyword(name):
            raise VariableNameError('Name should not be keyword!')

variable_set = VariableSet()

        

