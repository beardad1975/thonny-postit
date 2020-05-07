import tkinter as tk
from tkinter import ttk
from collections import Counter

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import common_vars_postit, common_default_vars
                       



class VariableMenuWidget(ttk.Frame):
    """ composite and mixin approach postit"""
    def widget_init(self, master):
        # just combobox. don't need to handle tab and image
        self.last_focus = ''
        self.vars_counter = None
        # self.vars_counter = Counter()
        # self.vars_counter['變數x'] = 1
        # self.vars_counter['變數y'] = 1
        # self.vars_counter['名字'] = 1
        # self.vars_counter['位置'] = 1

        self.vars_limit = 30
        self.tk_var = tk.StringVar()

        ttk.Frame.__init__(self, master)        
        self.vars_combobox = ttk.Combobox(self, width=12, state="readonly",
                justify=tk.CENTER,textvariable=self.tk_var,takefocus=0,
                values=[])
        self.restore_default_vars()

        self.vars_combobox.pack(side=tk.LEFT, anchor='w')

        self.vars_combobox.current(0)

        self.vars_combobox.bind('<<ComboboxSelected>>', self.on_combo_select)
        #self.vars_combobox.bind('<<Selection>>', self.on_select)
        self.vars_combobox.bind('<Button-1>',self.on_combo_click)

        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)

    def restore_default_vars(self):
        if self.vars_counter:
            del self.vars_counter
        self.vars_counter = Counter(common_default_vars)
        self.update_vars_menu()

    def update_vars_menu(self):
        vars_list =[v for v,_ in self.vars_counter.most_common(self.vars_limit)]
        self.vars_combobox.config(values=vars_list)
        self.vars_combobox.current(0)

    # def get_most_common(self):
    #     most_common_vars = self.vars_counter.most_common(self.vars_limit)
    #     # skip count, just name list
    #     return [v for v, _ in most_common_vars]
        
    #def on_select(self):
     #   print('here')

    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
            
        self.selection_clear()

    def on_combo_click(self, event):
        #print('click')    
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        #self.selection_clear()
        
    def _handle_toplevel_response(self, event):
        if "globals" in event:
            self.vars_counter.update(event['globals'].keys())
            self.update_vars_menu()


class VariableMenuPostit(VariableMenuWidget, 
                    BasePopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master)
        #self.code_init()
        #self.post_init()
        #self.popup_init()


class VariableAddToolPostMixin:
    pass


class VariableAddToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableAddToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'variable_add')
        self.code_init()
        self.post_init()
        #self.popup_init()

