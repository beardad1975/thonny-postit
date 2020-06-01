import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseWidget,BaseCode, BasePost, BasePopup
from .common import common_postit_tabs,common_images


class CodeListEmpty(Exception): pass

class DropdownWidget(ttk.Frame):

    def widget_init(self, tab_name):
        # store tab
        self.tab_name = tab_name
        self.tab = common_postit_tabs[tab_name]
        
        # image
        self.enter_image = common_images['enter_small']

        # frame init
        ttk.Frame.__init__(self, self.tab.frame)

        # main and bottom sub-frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.TOP)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side=tk.TOP, anchor='w')

        # dropdown list button
        if len(self.code_list) > 1:
            self.dropdown_image = common_images['dropdown']
        else:
            self.dropdown_image = common_images['dropdown_empty']
        self.dropdown_button = tk.Button(self.main_frame, 
                                        relief='flat',
                                        borderwidth=0,
                                        image=self.dropdown_image, 
                                        padx=0,
                                        justify='left',
                                        )
        self.dropdown_button.pack(side=tk.LEFT, anchor='w',padx=0)
        

        # postit button 
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        #self.postit_button = ttk.Button(self.main_frame, text='1234')
        self.postit_button = tk.Button(self.main_frame,  
                                        relief='solid',
                                        borderwidth=1,
                                        text='***' , 
                                        fg=self.tab.font_color, 
                                        bg=self.tab.fill_color,
                                        justify='left', 
                                        font=f,
                                        compound='right',
                                        #image=self.enter_image,
                                        padx=0,
                                        pady=0,
                                         
                                        state='normal',
                                        )

        # two notes
        self.main_note_label = tk.Label(self.main_frame, text='' ) 
        self.bottom_note_label = tk.Label(self.bottom_frame, text='')

        # 1st row sub-frame
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        self.main_note_label.pack(side=tk.LEFT, anchor='w',padx=5)
        # 2nd row sub-frame
        
        self.bottom_note_label.pack(side=tk.LEFT,padx=15)


class DropdownPopup:
    def popup_init(self):
        # button popup menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_checkbutton(label="【選項】結尾Enter換行", onvalue=1, offvalue=0, 
                variable=self.var_postfix_enter,
                command=self.toggle_postfix_enter,
                )
        self.postit_button.bind("<Button-3>", self.popup)

        # dropdown popup menu
        if len(self.code_list) > 1:
            self.dropdown_menu = tk.Menu(self, tearoff=0)
            for i, code_item in enumerate(self.code_list):
                text = code_item.menu_display
                f = lambda index=i: self.switch_postit(index)
                self.dropdown_menu.add_command(label=text, command=f)
            self.dropdown_button.bind("<Button-1>", self.dropdown_popup)

    def popup(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)

    def dropdown_popup(self, event):
        self.dropdown_menu.tk_popup(event.x_root, event.y_root)

    def switch_postit(self, code_index):
        code_item = self.code_list[code_index]
        self.code = code_item.code
        self.code_display = code_item.code_display
        self.note = code_item.note
        self.long_note = code_item.long_note

        self.set_code_display(self.code_display)
        self.set_note(self.note)
        self.update_button_enter_sign()

class DropdownPostit( DropdownWidget, 
                      BaseCode,
                      BasePost, 
                      DropdownPopup):
    """   """
    def __init__(self,  tab_name, code_list, postfix_enter=False):
        # store code name tuple list

        if not  code_list:
            raise CodeListEmpty

        self.code_list = code_list

        self.widget_init(tab_name)
        # use first item as default code
        _, code, code_display, note, long_note = self.code_list[0]
        self.code_init(code, code_display, note, postfix_enter, long_note)
        
        self.post_init()
        self.popup_init()