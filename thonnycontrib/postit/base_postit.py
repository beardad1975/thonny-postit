import tkinter as tk
import tkinter.font as font
from tkinter import ttk
#from pathlib import Path
#from PIL import Image, ImageTk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell


from .common import common_images

class BaseWidget(ttk.Frame):

    def widget_init(self, tab_name):
        """ 
            frame structure(2 row sub-frame)

            main_frame (postit_button + main_note)
            bottom_frame(bottom_note)

            either main_note or bottom_note according to long_note flag  
        """
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
        
        # button and label
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
                                        padx=5,
                                        pady=5, 
                                        state='normal',
                                        )

        self.main_note_label = ttk.Label(self.main_frame, text='' ) 
        self.bottom_note_label = ttk.Label(self.bottom_frame, text='')

        # 1st row sub-frame
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        self.main_note_label.pack(side=tk.LEFT, anchor='w',padx=5)
        # 2nd row sub-frame
        
        self.bottom_note_label.pack(side=tk.TOP, anchor='center',padx=5)



class BaseCode:
    def code_init(self, code, code_display=None, note=None, postfix_enter=None,
                     long_note=False):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.long_note = long_note

        if code_display is None:
            code_display = code
        self.code = code
        self.code_display = code_display 
        self.note = note
        if postfix_enter:
            self.var_postfix_enter.set(True)
        
        self.update_postit_code()

    def update_button_enter_sign(self):
        if self.var_postfix_enter.get():
            self.postit_button.config(image=self.enter_image)
        else:
            self.postit_button.config(image='')

    def toggle_postfix_enter(self):
        r = self.var_postfix_enter.get()
        self.var_postfix_enter.set(r)
        self.update_button_enter_sign()
        

    def set_code_display(self, text):
        self.postit_button.config(text=text)

    def set_code(self, text):
        pass

    def set_note(self, help_text):
        if not self.long_note:
            # use main note
            self.main_note_label.config(text=help_text)
            self.bottom_note_label.config(text='')
            self.bottom_note_label.pack_forget()
        else: # bottom note
            self.main_note_label.config(text='')
            self.bottom_note_label.pack(side=tk.LEFT,padx=15)
            self.bottom_note_label.config(text=help_text) 

    def update_postit_code(self):
        #self.set_code(self.code)
        self.set_code_display(self.code_display)
        self.set_note(self.note)
        self.update_button_enter_sign()

class BasePost:
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.postit_button.config(cursor='arrow')

    def on_mouse_drag(self, event):
        ###print('drag ...')
        #create drag window
        if not self.drag_window: 
            self.create_drag_window()
            self.postit_button.config(cursor='hand2')

        x_root, y_root = event.x_root, event.y_root

        self.drag_window.geometry('+{}+{}'.format(x_root+5, y_root+5))

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
                    #self.drag_button.config(text='【取代】'+self.hover_text_backup)
                    
                else:
                    self.drag_hover_selection = False
                    #self.drag_button.config(text=self.hover_text_backup)
                    
                    
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
                        #self.drag_button.config(text='【取代】'+self.hover_text_backup)
                        
                    else:
                        self.drag_hover_selection = False
                        #self.drag_button.config(text=self.hover_text_backup)
                        

    def create_drag_window(self):
            self.drag_window = tk.Toplevel()
            # clone postit_button in drag window
            image = self.postit_button.cget('image')
            compound = self.postit_button.cget('compound')
            font = self.postit_button.cget('font')
            bg = self.postit_button.cget('bg')
            fg = self.postit_button.cget('fg')
            text = '  ' + self.postit_button.cget('text')
            #self.hover_text_backup = text
            justify = self.postit_button.cget('justify')
            self.drag_button = tk.Button(self.drag_window, text=text, bg=bg, 
                        fg=fg,font=font, compound=compound, image=image,
                        relief='solid', justify=justify, bd=0 )
            self.drag_button.pack()
            self.drag_window.overrideredirect(True)
            self.drag_window.attributes('-topmost', 'true')

    def on_mouse_release(self, event):
        #check and destroy drag window        
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None
            self.postit_button.config(cursor='arrow')
            
        # restore mouse cursor 

        # find out post type and target   
        x_root, y_root = event.x_root, event.y_root
        hover_widget = event.widget.winfo_containing(x_root,y_root)
        self.determine_post_place_and_type(hover_widget)
        #reset hover state 
        self.drag_hover_selection = False

    def determine_post_place_and_type(self, hover_widget):
        """
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
            # postit button pressed
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
            editor_text.event_generate("<BackSpace>")
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")

    def content_insert(self, text_widget, content):

        lines = content.split('\n')  
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
                    



    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            if shell_text.compare(tk.INSERT, '>=', 'input_start'):
                # cursor after input_start
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")
            else: # cursor before input_start
                # append last line
                shell_text.mark_set(tk.INSERT, 'end-1c')
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")
        elif pressing and selecting:
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    shell_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    self.content_insert(shell_text, self.code)
                    if self.var_postfix_enter.get():
                        shell_text.event_generate("<Return>")
                else: # input_start among selection
                    shell_text.delete('input_start', tk.SEL_LAST)
                    shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                    self.content_insert(shell_text, self.code)
                    if self.var_postfix_enter.get():
                        shell_text.event_generate("<Return>")
                
        elif dragging and not hovering:
            if shell_text.tag_ranges(tk.SEL):
                shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)

            if shell_text.compare(tk.INSERT, '>=', 'input_start'):
                # cursor after input_start
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")

        elif dragging and hovering:
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    shell_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    self.content_insert(shell_text, self.code)
                    if self.var_postfix_enter.get():
                        shell_text.event_generate("<Return>")
                else: # input_start among selection
                    shell_text.delete('input_start', tk.SEL_LAST)
                    shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                    self.content_insert(shell_text, self.code)
                    if self.var_postfix_enter.get():
                        shell_text.event_generate("<Return>")

        


class BasePopup:
    def popup_init(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_checkbutton(label="加上Enter換行", onvalue=1, offvalue=0, 
                variable=self.var_postfix_enter,
                command=self.toggle_postfix_enter,
                )
        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)



class BasePostit(BaseWidget, BaseCode, BasePost, BasePopup):
    """ composite and mixin approach base function postit"""
    def __init__(self,  tab_name, code, code_display=None, note=None, 
                    postfix_enter=False, long_note=False):
        self.widget_init(tab_name)
        self.code_init(code, code_display, note, postfix_enter, long_note)
        self.post_init()
        self.popup_init()
        


    
