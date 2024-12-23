from typing import NamedTuple
from pathlib import Path
from PIL import Image, ImageTk


from keyword import iskeyword

from collections import Counter, namedtuple

import tkinter.font as font

# 
TAB_DATA_PATH = Path(__file__).parent / 'tab_data'




#postit_tabs = {}

postit_view = None

### code namedtuple

CodeNTuple = namedtuple('CodeNTuple','menu_display code code_display note long_note ')

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
load_image('enter_key')
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
load_image('dropdown_empty')
load_image('empty')
load_image('enclosed_right') 
load_image('enclosed_left') 
load_image('block_enclosed') 
load_image('block_enclosed_small') 
load_image('note') 
load_image('paste_postit')
load_image('gear')
load_image('info')
load_image('keyin_display')
load_image('avatar_ai')
load_image('avatar_me')
load_image('wait_answer0')
load_image('wait_answer1')
load_image('wait_answer2')
load_image('wait_answer3')
load_image('send_msg')
load_image('disconnect')

#  
# setup vars counter and default


common_default_vars = ['x','y','z','數字','文字','清單','數','索引','項目','字典','i','j']
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
    #share_var_assign_postit.postit_button.config(state='normal')

def disable_var_buttons():
    share_var_get_postit.postit_button.config(state='disable')
    #share_var_assign_postit.postit_button.config(state='disable')


# font
postit_font = font.Font(size=12, weight=font.NORMAL, family='Consolas') 
note_font = font.Font(size=10, weight=font.NORMAL, family='Consolas')
popup_menu_font = font.Font(size=10, weight=font.NORMAL, family='Consolas')


dialog_title_font = font.Font(size=14, weight=font.NORMAL, family='Consolas')
dialog_font = font.Font(size=10, weight=font.NORMAL, family='Consolas')

symbol_font = font.Font(size=10, weight=font.NORMAL, family='Consolas')
postit_para_font = font.Font(size=11, weight=font.NORMAL, family='Consolas')
tab_title = font.Font(size=12, weight=font.NORMAL, family='Consolas')
tab_label = font.Font(size=12, weight=font.NORMAL, family='Consolas')


aiassist_tab = False

aiassist_intro = '以下為python相關,以繁體中文回答,對象為青少年,簡短回答'

# type: text code error
AnswerNTuple = namedtuple('AnswerNTuple', 'type answer')
ANS_TYPE_TEXT = 'text'
ANS_TYPE_CODE = 'code'
ANS_TYPE_ERROR = 'error'

editor_text = None
shell_text = None

ask_append_list = [
    '',
    '將以上英文翻譯成中文',
    '請解釋以上的程式碼',
    '請將以上的程式改寫',
    '以上的程式哪裡有錯誤，請修正',
    '以上的提問請簡單回答',
]
