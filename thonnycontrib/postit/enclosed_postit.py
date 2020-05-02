import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseWidget,BaseCode, BasePost, BasePopup
from .common import common_postit_tabs,common_images

class EnclosedWidget(ttk.Frame):

    def widget_init(self, tab_name):
        # store tab
        self.tab_name = tab_name
        self.tab = common_postit_tabs[tab_name]
        # image
        self.enter_image = common_images['enter_small']

        ttk.Frame.__init__(self, self.tab.frame)
        #f = font.Font(size=11, weight=font.NORMAL, family='Microsoft JhengHei')
        self.head_decoration_label = tk.Label(self, text='', bg=self.tab.fill_color)
        self.head_decoration_label.pack(side=tk.LEFT, anchor='w',padx=2)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        self.postit_button = tk.Button(self,  
                                        relief='flat',
                                        borderwidth=0,
                                        text='***' , 
                                        fg=self.tab.font_color, 
                                        bg=self.tab.fill_color,
                                        justify='left', 
                                        font=f,
                                        compound='right',
                                        #image=self.enter_image,

                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        # a type label for distinguish
        self.tail_decoration_label = tk.Label(self, text='', bg=self.tab.fill_color)
        self.tail_decoration_label.pack(side=tk.LEFT, anchor='w',padx=2)

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)



class EnclosedCodeMixin:
    def code_init(self, enclosed_head, enclosed_tail, 
                        code_display, note, postfix_enter):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.enclosed_head = enclosed_head
        self.enclosed_tail = enclosed_tail
        self.code = enclosed_head + enclosed_tail

        if not code_display :
            self.code_display = self.code
        else: 
            self.code_display = code_display
        self.note = note

        if postfix_enter:
            self.var_postfix_enter.set(True)
        
        self.update_postit_code()



class EnclosedPostMixin:
    def insert_into_editor(self, text_widget, selecting, dragging):
        if selecting:
            # enclosed slection
            text_widget.insert(tk.SEL_FIRST, self.enclosed_head)
            stored_index = text_widget.index(tk.SEL_LAST)
            text_widget.insert(tk.SEL_LAST, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            text_widget.mark_set(tk.INSERT, stored_index)
            text_widget.tag_remove(tk.SEL,'0.0', tk.END)

        else: # no selecting    
            text_widget.insert(tk.INSERT, self.enclosed_head)
            stored_index = text_widget.index(tk.INSERT)
            text_widget.insert(tk.INSERT, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            text_widget.mark_set(tk.INSERT, stored_index)

        if self.var_postfix_enter.get():
            text_widget.event_generate("<Return>")

    def insert_into_shell(self, text_widget, selecting, dragging):
        if text_widget.compare(tk.INSERT, '>=' , 'input_start'):
            if selecting:
                # enclosed slection
                text_widget.insert(tk.SEL_FIRST, self.enclosed_head)
                stored_index = text_widget.index(tk.SEL_LAST)
                text_widget.insert(tk.SEL_LAST, self.enclosed_tail)
                #keep insert cursor in the stored_index 
                text_widget.mark_set(tk.INSERT, stored_index)
                text_widget.tag_remove(tk.SEL,'0.0', tk.END)

            else: # no selecting    
                text_widget.insert(tk.INSERT, self.enclosed_head)
                stored_index = text_widget.index(tk.INSERT)
                text_widget.insert(tk.INSERT, self.enclosed_tail)
                #keep insert cursor in the stored_index 
                text_widget.mark_set(tk.INSERT, stored_index)
        else: # insert before input start
            if selecting:
                pass
            else: # not selecting
                text_widget.mark_set(tk.INSERT, 'end-1c')

                text_widget.insert(tk.INSERT, self.enclosed_head)
                stored_index = text_widget.index(tk.INSERT)
                text_widget.insert(tk.INSERT, self.enclosed_tail)
                #keep insert cursor in the stored_index 
                text_widget.mark_set(tk.INSERT, stored_index)



        if self.var_postfix_enter.get():
            text_widget.event_generate("<Return>")


class EnclosedPostit(EnclosedWidget, 
                     EnclosedCodeMixin, BaseCode,
                     EnclosedPostMixin, BasePost, 
                     BasePopup):
    """  enclosed postit linke () [] '' "" {}  only for single line """
    def __init__(self, tab_name, enclosed_head, enclosed_tail,
                    code_display=None, note=None, postfix_enter=False):
        self.widget_init(tab_name)
        # remove newline
        enclosed_head = enclosed_head.replace('\n','')
        enclosed_tail = enclosed_tail.replace('\n','')
        self.code_init(enclosed_head, enclosed_tail, 
                        code_display, note, postfix_enter)
        self.post_init()
        self.popup_init()

