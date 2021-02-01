import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseWidget,BaseCode, BasePost, BasePopup
from .common import common_images

class EnclosedWidget(ttk.Frame):

    def widget_init(self, tab_name):
        # store tab
        self.tab_name = tab_name
        self.tab = common.postit_tabs[tab_name]
        
        # image
        self.enter_image = common_images['enter_small']

        # frame init
        ttk.Frame.__init__(self, self.tab.frame)

        # main and bottom sub-frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.TOP)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side=tk.TOP)

        #f = font.Font(size=11, weight=font.NORMAL, family='Microsoft JhengHei')
        self.enclosed_left_image = common_images['enclosed_left']
        self.head_decoration_label = tk.Label(self.main_frame, text='',
                                    image=self.enclosed_left_image,
                                            )
        self.head_decoration_label.pack(side=tk.LEFT, anchor='w',padx=0)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        self.postit_button = tk.Button(self.main_frame,  
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
        # 1st row sub-frame
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        
        self.enclosed_right_image = common_images['enclosed_right']
        self.tail_decoration_label = tk.Label(self.main_frame, text='', 
                                            image= self.enclosed_right_image,)
        self.tail_decoration_label.pack(side=tk.LEFT, anchor='w',padx=0)

        self.main_note_label = ttk.Label(self.main_frame, text='',justify='left', )
        self.main_note_label.pack(side=tk.LEFT, anchor='w',padx=5)
        # 2nd row sub-frame
        self.bottom_note_label = ttk.Label(self.bottom_frame, text='',justify='left')
        self.bottom_note_label.pack(side=tk.TOP, anchor='center',padx=5)


class EnclosedCodeMixin:
    def code_init(self, enclosed_head, enclosed_tail, 
                        code_display, note, postfix_enter, long_note=False):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.long_note = long_note

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
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            # insert enclosed and keep cursor between
            editor_text.insert(tk.INSERT, self.enclosed_head)
            stored_index = editor_text.index(tk.INSERT)
            editor_text.insert(tk.INSERT, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            editor_text.mark_set(tk.INSERT, stored_index)
        elif pressing and selecting:
            # enclosed slection
            editor_text.insert(tk.SEL_FIRST, self.enclosed_head)
            stored_index = editor_text.index(tk.SEL_LAST)
            editor_text.insert(tk.SEL_LAST, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            editor_text.mark_set(tk.INSERT, stored_index)
            editor_text.tag_remove(tk.SEL,'0.0', tk.END)
        elif dragging and not hovering:
            # insert enclosed and keep cursor between
            editor_text.insert(tk.INSERT, self.enclosed_head)
            stored_index = editor_text.index(tk.INSERT)
            editor_text.insert(tk.INSERT, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            editor_text.mark_set(tk.INSERT, stored_index)
        elif dragging and hovering:
            # enclosed slection
            editor_text.insert(tk.SEL_FIRST, self.enclosed_head)
            stored_index = editor_text.index(tk.SEL_LAST)
            editor_text.insert(tk.SEL_LAST, self.enclosed_tail)
            #keep insert cursor in the stored_index 
            editor_text.mark_set(tk.INSERT, stored_index)
            editor_text.tag_remove(tk.SEL,'0.0', tk.END)

        if self.var_postfix_enter.get():
            text_widget.event_generate("<Return>")

        # if selecting:
        #     # enclosed slection
        #     text_widget.insert(tk.SEL_FIRST, self.enclosed_head)
        #     stored_index = text_widget.index(tk.SEL_LAST)
        #     text_widget.insert(tk.SEL_LAST, self.enclosed_tail)
        #     #keep insert cursor in the stored_index 
        #     text_widget.mark_set(tk.INSERT, stored_index)
        #     text_widget.tag_remove(tk.SEL,'0.0', tk.END)

        # else: # no selecting    
        #     text_widget.insert(tk.INSERT, self.enclosed_head)
        #     stored_index = text_widget.index(tk.INSERT)
        #     text_widget.insert(tk.INSERT, self.enclosed_tail)
        #     #keep insert cursor in the stored_index 
        #     text_widget.mark_set(tk.INSERT, stored_index)

        # if self.var_postfix_enter.get():
        #     text_widget.event_generate("<Return>")

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

        if pressing and not selecting:
            if shell_text.compare(tk.INSERT, '>=' , 'input_start'):
                # just insert 
                shell_text.insert(tk.INSERT, self.enclosed_head)
                stored_index = shell_text.index(tk.INSERT)
                #keep insert cursor in the middle
                shell_text.insert(tk.INSERT, self.enclosed_tail)
                shell_text.mark_set(tk.INSERT, stored_index)

        elif pressing and selecting:
            # check selection after input_start
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    # enclosed selection(original )
                    shell_text.insert(tk.SEL_FIRST, self.enclosed_head)
                    stored_index = shell_text.index(tk.SEL_LAST)
                    #keep insert cursor in the last of selection
                    shell_text.insert(tk.SEL_LAST, self.enclosed_tail) 
                    shell_text.mark_set(tk.INSERT, stored_index)
                    shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                else: # enclosed selection(truncated )
                    shell_text.insert('input_start', self.enclosed_head)
                    stored_index = shell_text.index(tk.SEL_LAST)
                    #keep insert cursor in the last of selection
                    shell_text.insert(tk.SEL_LAST, self.enclosed_tail) 
                    shell_text.mark_set(tk.INSERT, stored_index)
                    shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)                    

        elif dragging and not hovering:
            if shell_text.compare(tk.INSERT, '>=' , 'input_start'):
                # just insert 
                shell_text.insert(tk.INSERT, self.enclosed_head)
                stored_index = shell_text.index(tk.INSERT)
                #keep insert cursor in the middle
                shell_text.insert(tk.INSERT, self.enclosed_tail)
                shell_text.mark_set(tk.INSERT, stored_index)

        elif dragging and hovering:
            # check selection after input_start
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    # enclosed selection(original )
                    shell_text.insert(tk.SEL_FIRST, self.enclosed_head)
                    stored_index = shell_text.index(tk.SEL_LAST)
                    #keep insert cursor in the last of selection
                    shell_text.insert(tk.SEL_LAST, self.enclosed_tail) 
                    shell_text.mark_set(tk.INSERT, stored_index)
                    shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                else: # enclosed selection(truncated )
                    shell_text.insert('input_start', self.enclosed_head)
                    stored_index = shell_text.index(tk.SEL_LAST)
                    #keep insert cursor in the last of selection
                    shell_text.insert(tk.SEL_LAST, self.enclosed_tail) 
                    shell_text.mark_set(tk.INSERT, stored_index)
                    shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)           
        
        if self.var_postfix_enter.get():
            text_widget.event_generate("<Return>")

        # if shell_text.compare(tk.INSERT, '>=' , 'input_start'):
        #     if selecting:
        #         # enclosed slection
        #         shell_text.insert(tk.SEL_FIRST, self.enclosed_head)
        #         stored_index = shell_text.index(tk.SEL_LAST)
        #         shell_text.insert(tk.SEL_LAST, self.enclosed_tail)
        #         #keep insert cursor in the stored_index 
        #         shell_text.mark_set(tk.INSERT, stored_index)
        #         shell_text.tag_remove(tk.SEL,'0.0', tk.END)

        #     else: # no selecting    
        #         shell_text.insert(tk.INSERT, self.enclosed_head)
        #         stored_index = shell_text.index(tk.INSERT)
        #         shell_text.insert(tk.INSERT, self.enclosed_tail)
        #         #keep insert cursor in the stored_index 
        #         shell_text.mark_set(tk.INSERT, stored_index)
        # else: # insert before input start
        #     if selecting:
        #         pass
        #     else: # not selecting
        #         shell_text.mark_set(tk.INSERT, 'end-1c')

        #         shell_text.insert(tk.INSERT, self.enclosed_head)
        #         stored_index = shell_text.index(tk.INSERT)
        #         shell_text.insert(tk.INSERT, self.enclosed_tail)
        #         #keep insert cursor in the stored_index 
        #         shell_text.mark_set(tk.INSERT, stored_index)






class EnclosedPostit(EnclosedWidget, 
                     EnclosedCodeMixin, BaseCode,
                     EnclosedPostMixin, BasePost, 
                     BasePopup):
    """  enclosed postit linke () [] '' "" {}  only for single line """
    def __init__(self, tab_name, enclosed_head, enclosed_tail,
                    code_display=None, note=None, postfix_enter=False,
                    long_note=False):
        self.widget_init(tab_name)
        # remove newline
        enclosed_head = enclosed_head.replace('\n','')
        enclosed_tail = enclosed_tail.replace('\n','')
        self.code_init(enclosed_head, enclosed_tail, 
                        code_display, note, postfix_enter, long_note)
        self.post_init()
        self.popup_init()

