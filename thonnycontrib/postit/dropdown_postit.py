import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseWidget,BaseCode, BasePost, BasePopup
from .common import common_images
from . import common

class CodeListEmpty(Exception): pass

class DropdownWidget(ttk.Frame):

    def widget_init(self, parent, tab):
        # store tab
        
        self.parent = parent
        self.tab = tab
        
        
        # image
        self.enter_image = common_images['enter_small']
        self.enter_key_image = common_images['enter_key']
        
        self.paste_postit_image = common_images['paste_postit']
        self.info_image = common_images['info']
        

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
                                        #image=self.enter_image,
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
        self.main_note_label = tk.Label(self.main_note_frame, text='',
                                        justify='left', font=f2,
                                        image=self.info_image,compound='left',
                                        ) 
        self.bottom_note_label = tk.Label(self.bottom_frame, text='',
                                        justify='left', font=f2,
                                        image=self.info_image,compound='left',
                                        )
        

        # 1st row sub-frame
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        self.enter_label.pack(side=tk.LEFT, anchor='w')
        self.main_note_frame.pack(side=tk.LEFT, anchor='w')

        self.main_note_label.grid(sticky='we', padx=7, pady=0)
        # 2nd row sub-frame
        
        self.bottom_note_label.grid(sticky='we', padx=15, pady=0)


class DropdownCodeMixin:
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
        self.code = code
        self.code_display = code_display 
        self.note = note
        if postfix_enter:
            self.var_postfix_enter.set(True)
        
        self.update_postit_code()

        self.bottom_frame.grid_remove()
        self.main_note_label.grid_remove()
        self.update_hide_note()

    def update_button_enter_sign(self):
        if self.var_postfix_enter.get():
            self.enter_label.config(image=self.enter_image)
        else:
            self.enter_label.config(image='')

    # def toggle_button_enter_sign(self, event=None):
    #     is_enter = self.var_postfix_enter.get()
    #     self.var_postfix_enter.set(not is_enter)
    #     self.update_button_enter_sign()

    def set_note(self, help_text):

        if not self.long_note:
            # use main note
            self.main_note_label.config(text=help_text)
            self.bottom_note_label.config(text='')
            #self.bottom_note_label.grid_forget()
            self.bottom_frame.grid_remove()
        else: # bottom note
            self.main_note_label.config(text='')
            #self.bottom_note_label.grid(side=tk.LEFT,padx=15)
            self.bottom_note_label.config(text=help_text) 

    def update_hide_note(self):
        hide_note = self.var_hide_note.get()
        if not self.long_note:
            # use main note
            if not hide_note :
                self.main_note_label.grid()
                
            else:
                self.main_note_label.grid_remove()

        else: # bottom note
            if not hide_note :
                #self.bottom_note_label.grid()
                self.bottom_frame.grid()
                
            else:
                #self.bottom_note_label.grid_remove()
                self.bottom_frame.grid_remove()

    def toggle_hide_note(self, event=None):
        hide_note = self.var_hide_note.get()
        self.var_hide_note.set(not hide_note)
        self.update_hide_note() 

class DropdownPostMixin:
    # def post_init(self):
    #     self.drag_window = None
    #     self.drag_button = None
    #     self.drag_hover_selection = False
    #     self.hover_text_backup = ''
    #     #self.mouse_dragging = False
    #     # drag and press event
    #     self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
    #     self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
    #     self.postit_button.bind("<Double-Button-1>", self.toggle_button_enter_sign)
    #     self.postit_button.config(cursor='arrow')


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
                    self.drag_hover_selection = True
                    self.drag_button.config(text=' 【取代成】\n'+self.hover_text_backup)
                    
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
                        

    def create_drag_window(self):
            self.drag_window = tk.Toplevel()
            # clone postit_button in drag window
            image = self.postit_button.cget('image')
            compound = self.postit_button.cget('compound')
            font = self.postit_button.cget('font')
            bg = self.postit_button.cget('bg')
            fg = self.postit_button.cget('fg')
            text = '  ' + self.postit_button.cget('text')
            self.hover_text_backup = text
            justify = self.postit_button.cget('justify')
            self.drag_button = tk.Button(self.drag_window, text=text, bg=bg, 
                        fg=fg,font=font, compound=compound, image=image,
                        relief='solid', justify=justify, bd=0 )
            self.drag_button.pack()
            self.drag_window.overrideredirect(True)
            self.drag_window.attributes('-topmost', 'true')

    def determine_post_place_and_type(self, hover_widget):
        """
        disable all pressing (test)

      post hover_widget:
        (1)postit_button : press button
        (2)editor_text : drag to editor
        (3)shell_text  : drag to shell

      post type:
        (1)press postit insert (pressing=True, selecting=False)
        (2)press postit insert with selection
                                (pressing=True, selecting=True)
        (3)drag postit insert (dragging=True, hovering=False)
        (4)drag postit insert hovering over selection
                                (dragging=True, hovering=True) 
         """        
        if hover_widget is self.postit_button: 
            pass
        elif isinstance(hover_widget, CodeViewText):
            # drag to editor 
            editor_text = hover_widget
            
            if self.drag_hover_selection:
                # drag_hover_selection
                self.insert_into_editor(editor_text, 
                                    dragging=True, hovering=True)
                
            else:# not drag_hover_selection
                self.insert_into_editor(editor_text, 
                                    dragging=True, hovering=False)
        elif isinstance(hover_widget, ShellText):
            # drag to shell
            shell_text = hover_widget
            
            if self.drag_hover_selection:
                # drag_hover_selection
                self.insert_into_shell(shell_text, 
                                    dragging=True, hovering=True)
            else:# no drag_hover_selection
                self.insert_into_shell(shell_text, 
                                    dragging=True, hovering=False)





class DropdownPopup:
    def popup_init(self):
        # button popup menu
        f2 = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        self.popup_menu = tk.Menu(self, tearoff=0, font=f2)
        self.popup_menu.add_command(label="貼上便利貼 ", 
                                    image=self.paste_postit_image,
                                    compound='right',
                                    command=self.post_hover_button)
        self.popup_menu.add_separator()

        self.popup_menu.add_checkbutton(label="切換 說明文字(左鍵點擊) ", onvalue=0, offvalue=1, 
                variable=self.var_hide_note,
                command=self.update_hide_note,
                image=self.info_image,
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

    def post_hover_button(self, event=None):
        # postit button double clicked (paste code)
        workbench = get_workbench()
        focus_widget = workbench.focus_get()
        if isinstance(focus_widget, CodeViewText):
            # cursor in editor
            editor_text = focus_widget 
            if editor_text.tag_ranges(tk.SEL)  :
                # has selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=False)
        elif isinstance(focus_widget, ShellText):
            # cusor in shell
            shell_text = focus_widget
            if shell_text.tag_ranges(tk.SEL):
                # has selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=False)

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

        self.bottom_frame.grid_remove()
        self.main_note_label.grid_remove()
        self.update_hide_note()

class DropdownPostit( DropdownWidget, 
                      DropdownCodeMixin, BaseCode, 
                      DropdownPostMixin, BasePost, 
                      DropdownPopup):
    """   """
    def __init__(self, parent, tab, code_list, postfix_enter=False, start_hide_note=False):
        # store code name tuple list

        if not  code_list:
            raise CodeListEmpty

        self.code_list = code_list

        self.widget_init(parent, tab)
        # use first item as default code
        _, code, code_display, note, long_note = self.code_list[0]

        self.code_init(code, code_display, note, postfix_enter, long_note, start_hide_note )
        
        self.post_init()
        self.popup_init()