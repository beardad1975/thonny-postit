import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseCode, BasePost
from .dropdown_postit import DropdownWidget,DropdownPostMixin, DropdownPopup, CodeListEmpty
from .common import common_images
from . import common


class CodeListEmpty(Exception): pass


class MissingColonOrPass(Exception): pass
# first line end in colon
# second line must be pass


class BlockEnclosedCodeMixin:
    def code_init(self, code, code_display=None, note=None, postfix_enter=None,
                     long_note=False):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.long_note = long_note

        if code_display is None:
            code_display = code

        # check colon and pass in code
        if not ':' in code or not 'pass' in code:
            raise MissingColonOrPass

        self.code = code
        self.code_display = code_display 
        self.note = note
        if postfix_enter:
            self.var_postfix_enter.set(True)
        
        self.update_postit_code()



class BlockEnclosedPostit( DropdownWidget, 
                      BlockEnclosedCodeMixin, BaseCode, 
                      DropdownPostMixin, BasePost, 
                      DropdownPopup):
    """   """
    def __init__(self, parent, tab, code_list, postfix_enter=False):
        # store code name tuple list
        #print('block enclosed postit')
        if not  code_list:
            raise CodeListEmpty

        self.code_list = code_list

        self.widget_init(parent, tab)
        # use first item as default code
        _, code, code_display, note, long_note = self.code_list[0]
        self.code_init(code, code_display, note, postfix_enter, long_note)
        
        self.post_init()
        self.popup_init()