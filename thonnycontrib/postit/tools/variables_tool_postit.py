import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from collections import Counter


import thonny.codeview
from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell
from thonny.plugins.notes import NotesText

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import common_vars_postit, common_default_vars, common_images
                       



class VariableMenuWidget(ttk.Frame):
    """ composite and mixin approach postit"""
    def widget_init(self, master):
        # just combobox. don't need to handle tab and image
        self.last_focus = ''
        self.vars_counter = None


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



    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
            
        self.selection_clear()

    def on_combo_click(self, event):
  
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        #self.selection_clear()
        
    def _handle_toplevel_response(self, event):
        #print('got toplevel event')
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


        

class VariableAddToolPostit(ttk.Frame):
    """special postit"""
    def __init__(self, master):
        # don't need to handle tab
        self.tool_name = 'variable_add'
        self.tool_image = common_images[self.tool_name]
        self.select_text = ''

        ttk.Frame.__init__(self, master)        
        self.postit_button = tk.Button(self,  
                                        relief='groove',
                                        borderwidth=0,
                                        compound='right',
                                        image=self.tool_image,
                                        padx=0,
                                        pady=0,
                                        state='disable',
                                        command=self.on_mouse_click
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        
        # bind text select on code view , shell and notes 
        self.bind_all('<<Selection>>',self.on_text_select,True)

    def on_text_select(self, event):
        widget = event.widget
        if isinstance(widget,CodeViewText) or isinstance(widget,ShellText)\
                                    or isinstance(widget, NotesText):
                        
            # only select within a line
            self.select_text = widget.get(tk.SEL_FIRST,tk.SEL_LAST)
            if len(self.select_text) and '\n' not in self.select_text:
                print(self.select_text)
                self.postit_button.config(state='normal')
            else:
                self.select_text = ''
                self.postit_button.config(state='disable')
                

    def on_mouse_click(self):
        print("clicked")






