import tkinter as tk
import tkinter.font as font
from tkinter import ttk, messagebox

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseCode, BasePost
from .dropdown_postit import DropdownWidget,DropdownCodeMixin,DropdownPostMixin, DropdownPopup, CodeListEmpty
from .common import common_images
from . import common


class CodeListEmpty(Exception): pass


class MissingColonOrPass(Exception): pass
# first line end in colon
# second line must be pass


class BlockEnclosedWidget(ttk.Frame):

    def widget_init(self, parent, tab):
        # store tab
        
        self.parent = parent
        self.tab = tab
        
        
        # image
        self.enter_image = common_images['enter_small']
        self.block_enclosed_image = common_images['block_enclosed']
        self.block_enclosed_small_image = common_images['block_enclosed_small']
        self.enter_key_image = common_images['enter_key']
        self.note_image = common_images['note']
        self.paste_postit_image = common_images['paste_postit']

        # frame init
        #ttk.Frame.__init__(self, self.tab.frame)
        ttk.Frame.__init__(self, self.parent)

        # main and bottom sub-frame
        self.main_frame = ttk.Frame(self)
        #self.main_frame.pack(side=tk.TOP, anchor='w')
        self.main_frame.grid(sticky='we', padx=0, pady=0)
        self.bottom_frame = ttk.Frame(self)
        #self.bottom_frame.pack(side=tk.TOP, anchor='w', pady=0)
        self.bottom_frame.grid(sticky='we', padx=0, pady=0)

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
        f = font.Font(size=12, weight=font.NORMAL, family='Consolas')
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
                                        image=self.block_enclosed_image,
                                        padx=0,
                                        pady=0,
                                        #underline = 0, 
                                        state='normal',
                                        command=self.toggle_hide_note,
                                        )
        
        self.enter_label = tk.Label(self.main_frame, text='', image=self.enter_image, compound='center')

        # two notes
        f2 = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        self.main_note_frame = ttk.Frame(self.main_frame)
        #self.main_note_label = tk.Label(self.main_frame, text='',justify='left', font=f2  ) 
        self.main_note_label = tk.Label(self.main_note_frame, text='',justify='left', font=f2  ) 
        self.bottom_note_label = tk.Label(self.bottom_frame, text='',justify='left', font=f2)
        

        # 1st row sub-frame
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        self.enter_label.pack(side=tk.LEFT, anchor='w')
        self.main_note_frame.pack(side=tk.LEFT, anchor='w')
        
        self.main_note_label.grid(sticky='we', padx=2, pady=0)
        # 2nd row sub-frame
        
        self.bottom_note_label.grid(sticky='we', padx=15, pady=0)


class BlockEnclosedCodeMixin:
    def code_init(self, code, code_display=None, note=None, postfix_enter=None,
                     long_note=False, start_hide_note=False):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.long_note = long_note
        self.start_hide_note = start_hide_note
        self.var_hide_note = tk.BooleanVar()
        self.var_hide_note.set(self.start_hide_note)

        if code_display is None:
            code_display = code

        # check colon and pass in code
        if not ':' in code or not '\npass' in code:
            raise MissingColonOrPass

        code_split = code.split('\n', 2)
        #print(code_split)
        if len(code_split) == 2:
            # nothing remains after pass
            self.block_enclosed_colon_part_code = code_split[0]
            self.block_enclosed_after_pass_code = None
        elif len(code_split) == 3:
            # something remains after pass
            self.block_enclosed_colon_part_code = code_split[0]
            self.block_enclosed_after_pass_code = code_split[2]

        display_split = code_display.split('\n', 2)
        #print(display_split)
        if len(display_split) == 2:
            # nothing remains after pass
            self.block_enclosed_colon_part_display = display_split[0]
            self.block_enclosed_after_pass_display = None
        elif len(display_split) == 3:
            # something remains after pass
            self.block_enclosed_colon_part_display = display_split[0]
            self.block_enclosed_after_pass_display = display_split[2]
        
        #print(self.block_enclosed_colon_part)
        #print(self.block_enclosed_after_pass)
        self.code = code
        self.code_display = code_display 
        self.note = note        
        
        if postfix_enter:
            self.var_postfix_enter.set(True)
        
        self.update_postit_code()
        self.update_hide_note()


class BlockEnclosedPostMixin:
    def on_mouse_drag(self, event):
        ###print('drag ...')
        #create drag window
        if not self.drag_window: 
            self.create_drag_window()
            self.postit_button.config(cursor='hand2')

        x_root, y_root = event.x_root, event.y_root
        
        self.drag_window.geometry('+{}+{}'.format(x_root-10, y_root+2))

        #change insert over editor or shell (but not postit button)
        
        hover_widget = event.widget.winfo_containing(x_root, y_root)
        
        if isinstance(hover_widget, CodeViewText):
            # hover editor
            editor_text = hover_widget
            relative_x = x_root - editor_text.winfo_rootx()
            relative_y =  y_root - editor_text.winfo_rooty()
            mouse_index = editor_text.index(f"@{relative_x},{relative_y}")
            # set cursor in editor
            editor_text.focus_set()
            editor_text.mark_set(tk.INSERT, mouse_index)

            if editor_text.tag_ranges(tk.SEL):
                #check darg hover selection
                if editor_text.compare(tk.SEL_FIRST, "<=", mouse_index) and \
                    editor_text.compare(mouse_index, "<=", tk.SEL_LAST):

                    block_text = editor_text.get("sel.first linestart", "sel.last lineend")
                    
                    block_enclosed_text = self.enclosed_in_drag(block_text)

                    self.drag_hover_selection = True
                    self.drag_button.config(text=' 【包含區塊】\n'+ block_enclosed_text)
                    
                else:
                    self.drag_hover_selection = False
                    self.drag_button.config(text=self.hover_text_backup)
                    
                    
        elif isinstance(hover_widget, ShellText):
            # hover shell 
            shell_text = hover_widget
            relative_x = x_root - shell_text.winfo_rootx()
            relative_y = y_root - shell_text.winfo_rooty()
            # set cursor in shell
            shell_text.focus_set()
            mouse_index = shell_text.index(f"@{relative_x},{relative_y}")
            input_start_index = shell_text.index('input_start')
            if shell_text.compare(mouse_index, '>=', input_start_index):
                shell_text.mark_set(tk.INSERT, mouse_index)

                if shell_text.tag_ranges(tk.SEL):
                    #check darg hover selection
                    if shell_text.compare(tk.SEL_FIRST, "<=", mouse_index) and \
                        shell_text.compare(mouse_index, "<=", tk.SEL_LAST):
                        self.drag_hover_selection = True
                        self.drag_button.config(text=' 【取代成】\n'+self.hover_text_backup)
                        
                    else:
                        self.drag_hover_selection = False
                        self.drag_button.config(text=self.hover_text_backup)

    def enclosed_in_drag(self, block_text):
        lines = block_text.split('\n')

        # count leading spaces in first line
        first_spaces_num = len(lines[0]) - len(lines[0].lstrip(' '))

        block_enclosed_text = ' ' * first_spaces_num + self.block_enclosed_colon_part_display + '\n'
        block_enclosed_text += '    ' + lines[0] + '\n'

        is_block_end =  False
        for line in lines[1:]:
            temp_spaces_num = len(line) - len(line.lstrip(' '))
            if not is_block_end and temp_spaces_num >= first_spaces_num: 
                # indent block when necessary
                block_enclosed_text += '    ' + line + '\n'
            else:
                # no indent
                is_block_end = True
                block_enclosed_text += line + '\n'

        if self.block_enclosed_after_pass_display:
            lines = self.block_enclosed_after_pass_display.split('\n')
            for line in lines:
                block_enclosed_text += ' ' * first_spaces_num + line + '\n'

        return block_enclosed_text

    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")

        elif pressing and selecting:
            
            editor_text.event_generate("<BackSpace>")
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")

        elif dragging and not hovering:
            # cancel selection
 
            if editor_text.tag_ranges(tk.SEL):
                ori_sel_first = editor_text.index(tk.SEL_FIRST)
                ori_sel_last = editor_text.index(tk.SEL_LAST)
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")



        elif dragging and hovering:
            #editor_text.event_generate("<BackSpace>")
            #self.content_insert(editor_text, self.code)
            
            self.block_enclosed_content_insert(editor_text)
            
            #if self.var_postfix_enter.get():
            #    editor_text.event_generate("<Return>")


    def block_enclosed_content_insert(self, text_widget):
        #print('block_enclosed insert')
        #text_widget.event_generate("<BackSpace>")

        # get block_text in selection

        index1 = text_widget.index("sel.first linestart")
        index2 = text_widget.index("sel.last lineend")

        block_text = text_widget.get(index1, index2)
        #print(block_text)
        # delete all selection lines
        text_widget.tag_add(tk.SEL, index1, index2)
        text_widget.event_generate("<BackSpace>")
        
        lines = block_text.split('\n')

        # count leading spaces in first line
        first_spaces_num = len(lines[0]) - len(lines[0].lstrip(' '))

        temp_text = ' ' * first_spaces_num + self.block_enclosed_colon_part_code
        text_widget.insert(tk.INSERT,temp_text)
        text_widget.event_generate("<Return>")
        

        
        temp_text = '    ' + lines[0] 
        text_widget.event_generate("<Home>")
        text_widget.insert(tk.INSERT,temp_text)
        text_widget.event_generate("<Return>")
        

        is_block_end =  False
        for line in lines[1:]:
            temp_spaces_num = len(line) - len(line.lstrip(' '))
            if not is_block_end and temp_spaces_num >= first_spaces_num: 
                # indent block when necessary
                temp_text = '    ' + line
                text_widget.event_generate("<Home>")
                text_widget.insert(tk.INSERT,temp_text)
                text_widget.event_generate("<Return>")
                
            else:
                # no indent
                is_block_end = True
                temp_text = line
                text_widget.event_generate("<Home>")
                text_widget.insert(tk.INSERT,temp_text)
                text_widget.event_generate("<Return>")
                
        if self.block_enclosed_after_pass_code:
            text_widget.event_generate("<BackSpace>")
            lines = self.block_enclosed_after_pass_code.split('\n')
            #print(lines)
            line_num = len(lines)          
            if line_num == 1 :
                # one line (no newline)
                    #print('co chi')
                    text_widget.insert(tk.INSERT,lines[0])
            elif line_num > 1 :
                #multi lines 
                line_count = len(lines)
                for i, line in enumerate(lines):

                    #if else else and except, need to add a extra backspack
                    # pass is special case
                    #if not line.startswith('pass'):
                    
                    #if line[:4] in ('else', 'elif', 'exce')  :
                    #    text_widget.event_generate("<BackSpace>")

                    text_widget.insert(tk.INSERT,line)

                    #  generate enter if not last item
                    if i < line_count - 1 :
                        text_widget.event_generate("<Return>")




class BlockEnclosedPopupMixin:
    def popup_init(self):
        # button popup menu
        f2 = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        self.popup_menu = tk.Menu(self, tearoff=0, font=f2)
        self.popup_menu.add_command(label="包含區塊 (需選取文字) ",
                                    command=self.block_enclosed_hover_button,
                                    image=self.block_enclosed_small_image,
                                    compound='right',
                                    )
        self.popup_menu.add_command(label="貼上便利貼 ", 
                                    image=self.paste_postit_image,
                                    compound='right',
                                    command=self.post_hover_button)
        
        self.popup_menu.add_separator()

        self.popup_menu.add_checkbutton(label="切換 說明文字 ", onvalue=0, offvalue=1, 
                variable=self.var_hide_note,
                command=self.update_hide_note,
                image=self.note_image,
                compound='right',
                )

        self.popup_menu.add_checkbutton(label="切換 便利貼換行 ", onvalue=1, offvalue=0, 
                variable=self.var_postfix_enter,
                command=self.update_button_enter_sign,
                image=self.enter_key_image,
                compound='right',
                )

        self.postit_button.bind("<Button-3>", self.popup)

        # dropdown popup menu
        if len(self.code_list) > 1:
            self.dropdown_menu = tk.Menu(self, tearoff=0, font=f2)
            for i, code_item in enumerate(self.code_list):
                text = code_item.menu_display
                f = lambda index=i: self.switch_postit(index)
                self.dropdown_menu.add_command(label=text, command=f)
            self.dropdown_button.bind("<Button-1>", self.dropdown_popup)


    def block_enclosed_hover_button(self, event=None):
        workbench = get_workbench()
        focus_widget = workbench.focus_get()
        if isinstance(focus_widget, CodeViewText):
            # cursor in editor
            editor_text = focus_widget 
            if editor_text.tag_ranges(tk.SEL)  :
                # has selection
                self.block_enclosed_content_insert(editor_text)
            else:# no selection
                messagebox.showinfo('無選取範圍','請先在編輯區選取文字，才能包含區塊', master=get_workbench())
        elif isinstance(focus_widget, ShellText):
            messagebox.showinfo('限在文字編輯區','包含區塊只限在文字編輯區，無法在互動環境下使用', master=get_workbench())

    def switch_postit(self, code_index):
        code_item = self.code_list[code_index]

        # check colon and pass in code
        if not ':' in code_item.code or not '\npass' in code_item.code:
            raise MissingColonOrPass

        code_split = code_item.code.split('\n', 2)
        #print(code_split)
        if len(code_split) == 2:
            # nothing remains after pass
            self.block_enclosed_colon_part_code = code_split[0]
            self.block_enclosed_after_pass_code = None
        elif len(code_split) == 3:
            # something remains after pass
            self.block_enclosed_colon_part_code = code_split[0]
            self.block_enclosed_after_pass_code = code_split[2]

        display_split = code_item.code_display.split('\n', 2)
        #print(display_split)
        if len(display_split) == 2:
            # nothing remains after pass
            self.block_enclosed_colon_part_display = display_split[0]
            self.block_enclosed_after_pass_display = None
        elif len(display_split) == 3:
            # something remains after pass
            self.block_enclosed_colon_part_display = display_split[0]
            self.block_enclosed_after_pass_display = display_split[2]

        self.code = code_item.code
        self.code_display = code_item.code_display
        self.note = code_item.note
        self.long_note = code_item.long_note

        self.set_code_display(self.code_display)
        self.set_note(self.note)
        self.update_button_enter_sign()
        self.update_hide_note()

class BlockEnclosedPostit( BlockEnclosedWidget, 
                      BlockEnclosedCodeMixin, DropdownCodeMixin, BaseCode, 
                      BlockEnclosedPostMixin, DropdownPostMixin, BasePost, 
                      BlockEnclosedPopupMixin, DropdownPopup):
    """   """
    def __init__(self, parent, tab, code_list, postfix_enter=False, start_hide_note=False):
        # store code name tuple list
        #print('block enclosed postit')
        if not  code_list:
            raise CodeListEmpty

        self.code_list = code_list

        self.widget_init(parent, tab)
        # use first item as default code
        _, code, code_display, note, long_note = self.code_list[0]
        self.code_init(code, code_display, note, postfix_enter, long_note, start_hide_note)
        
        self.post_init()
        self.popup_init()