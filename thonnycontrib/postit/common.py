from typing import NamedTuple
from pathlib import Path
from PIL import Image, ImageTk


from keyword import iskeyword

from collections import Counter



# dict{str:dict}
common_postit_tabs = {}


# image dict
def load_image(name):
    global common_images
    _im = Image.open(Path(__file__).parent / 'images' / (name + '.png'))       
    common_images[name] = ImageTk.PhotoImage(_im)

common_images = {}
load_image('enter')
load_image('enter_small')
load_image('backspace')
load_image('pilcrow')
load_image('undo')
load_image('redo')
load_image('indent')
load_image('dedent')
load_image('comment')
load_image('variable_add')
load_image('variable_assign')
load_image('variable_comma')
load_image('variable_dot')
load_image('variable_get')

#  
# setup vars counter and default


common_default_vars = ('變數x','變數y','名字', '文字', '數字', '項目', '清單')
#common_default_vars =()

# share postit . should be assign carefully
# beacause create later. So do not use 'from common import share_vars_postit' 
share_vars_postit = None
share_var_get_postit = None
share_var_assign_postit = None
share_var_comma_postit = None
share_var_dot_postit = None

def enable_var_buttons():
    share_var_get_postit.postit_button.config(state='normal')
    share_var_assign_postit.postit_button.config(state='normal')
    share_var_comma_postit.postit_button.config(state='normal')
    share_var_dot_postit.postit_button.config(state='normal')

def disable_var_buttons():
    share_var_get_postit.postit_button.config(state='disable')
    share_var_assign_postit.postit_button.config(state='disable')
    share_var_comma_postit.postit_button.config(state='disable')
    share_var_dot_postit.postit_button.config(state='disable')




#

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



# variable set
class VariableNotValidError(Exception):pass
class VariableShouldNotKeywordError(Exception):pass
class VariableKeyError(Exception):pass

class VariableSet():
    def __init__(self):
        self._custom_set = set()
        self._runtime_and_custom_set = set()  

    def __repr__(self):
        s = "runtime+custom : " + repr(self._runtime_and_custom_set) + '\n'
        s = s +  "custom : " +  repr(self._custom_set)
        return s

    def __iter__(self):
        return iter(self._runtime_and_custom_set)

    def get_custom_set(self):
        return self._custom_set

    def get_runtime_set(self):
        return self._runtime_and_custom_set - self._custom_set


    def add(self, var_name):
        self.check_name(var_name)
        self._runtime_and_custom_set.add(var_name)
        self._custom_set.add(var_name)

    def remove(self, var_name):
        self.check_name(var_name)
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
        assert isinstance(name, str)

        if not name.isidentifier():
            raise VariableNotValidError('Not a valid variable name!')
        
        if iskeyword(name):
            raise VariableShouldNotKeywordError('Name should not be keyword!')

common_variable_set = VariableSet()
common_variable_set.add('x')
common_variable_set.add('y')
common_variable_set.add('變數i')
common_variable_set.add('變數j')


#if statement
class IfStatement:
    def __init__(self):
        self._elif_num = 0
        self._else_flag = False
        self._if_clause = 'if _如果條件_ :\n_執行_\n'
        self._elif_clause = 'elif _不然條件_ :\n_執行_\n'
        self._else_clause = 'else:\n_否則執行_\n'

    def __repr__(self):
        s = self._if_clause

        for i in range(self._elif_num):
            s = s + self._elif_clause

        if self._else_flag:
            s = s + self._else_clause

        return s    

    def add_elif(self):
        self._elif_num += 1

    def subtract_elif(self):
        if self._elif_num > 0:
            self._elif_num -= 1

    @property
    def else_flag(self):
        return self._else_flag

    @else_flag.setter    
    def else_flag(self, status):
        self._else_flag = bool(status)

    @property
    def elif_num(self):
        return self._elif_num


if_statement = IfStatement()


# while loop
class WhileStatement():
    def __init__(self):
        self._break_flag = False

    def __repr__(self):
        s = "while _重複條件_ :\n_執行_\n"

        if self._break_flag :
            s = s + "if _離開條件_ :\nbreak\n"

        return s
        
    @property
    def break_flag(self):
        return self._break_flag

    @break_flag.setter    
    def break_flag(self, status):
        self._break_flag = bool(status)

while_statement = WhileStatement()
