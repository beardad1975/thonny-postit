from typing import NamedTuple
from pathlib import Path
from PIL import Image, ImageTk


from keyword import iskeyword

from collections import Counter, namedtuple



# dict{str:dict}
common_postit_tabs = {}


### code namedtuple

CodeNTuple = namedtuple('CodeNTuple','menu_display code code_display note long_note')

# image dict
def load_image(name):
    global common_images
    _im = Image.open(Path(__file__).parent / 'images' / (name + '.png'))       
    common_images[name] = ImageTk.PhotoImage(_im)

### common images dict
common_images = {}
# images for tools
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
load_image('variable_plus_assign')
load_image('variable_minus_assign')
load_image('variable_comma')
load_image('variable_dot')
load_image('variable_get')
load_image('variable_parentheses')
load_image('variable_square')
load_image('copy')
load_image('cut')
load_image('paste')
load_image('symbol')
load_image('keyword')
# images for  postit
load_image('dropdown')
load_image('enclosed_right') 
load_image('enclosed_left') 

#  
# setup vars counter and default


common_default_vars = ('變數x','變數y','名字', '文字', '數字', 'i','項目', '清單')
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

def disable_var_buttons():
    share_var_get_postit.postit_button.config(state='disable')
    share_var_assign_postit.postit_button.config(state='disable')





