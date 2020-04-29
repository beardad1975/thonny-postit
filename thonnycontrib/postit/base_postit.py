import tkinter as tk
import tkinter.font as font
from tkinter import ttk
#from pathlib import Path
#from PIL import Image, ImageTk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .common import common_variable_set
from .common import common_postit_tabs, common_images

class BaseWidget(ttk.Frame):

    def widget_init(self, tab_name):
        # store tab
        self.tab_name = tab_name
        self.tab = common_postit_tabs[tab_name]
        # image
        self.enter_image = common_images['enter']

        ttk.Frame.__init__(self, self.tab.frame)
        f = font.Font(size=11, weight=font.NORMAL, family='Microsoft JhengHei')
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
                                        padx=5,
                                        pady=5, 
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)




class BaseCode:
    def code_init(self, code, code_display=None, note=None, postfix_enter=None):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

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
        self.code = text

    def set_note(self, help_text):
        self.note_label.config(text=help_text)

    def update_postit_code(self):
        self.set_code(self.code)
        self.set_code_display(self.code_display)
        self.set_note(self.note)
        self.update_button_enter_sign()

class BasePost:
    def post_init(self):
        self.drag_window = None
        #self.mouse_dragging = False
        # drag and press event
        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_drag(self, event):
        ###print('drag ...')
        #create drag window
        if not self.drag_window: 
            self.drag_window = tk.Toplevel()
            # clone postit_button in drag window
            image = self.postit_button.cget('image')
            compound = self.postit_button.cget('compound')
            font = self.postit_button.cget('font')
            bg = self.postit_button.cget('bg')
            fg = self.postit_button.cget('fg')
            text = self.postit_button.cget('text')
            tk.Button(self.drag_window, text=text, bg=bg, fg=fg,
                        font=font, compound=compound, image=image,
                        ).pack()
            self.drag_window.overrideredirect(True)
            self.drag_window.attributes('-topmost', 'true')

        self.drag_window.geometry('+{}+{}'.format(event.x_root+10, event.y_root+10))

        #change insert cursor in editor and shell
        x, y = event.x_root, event.y_root
        target = event.widget.winfo_containing(x, y)
                
        if isinstance(target, CodeViewText):
            target.focus_set()
            rel_x = x - target.winfo_rootx()
            rel_y = y - target.winfo_rooty()
            target.mark_set('insert', f"@{rel_x},{rel_y}")
            ###print(index)
        elif isinstance(target, ShellText):
           
            target.focus_set()
            rel_x = x - target.winfo_rootx()
            rel_y = y - target.winfo_rooty()
            mouse_index = target.index(f"@{rel_x},{rel_y}")

            input_start_index = target.index('input_start')
            # insert can't not over input_start
            final_index = input_start_index.split('.')[0] + '.'
            mouse_column = mouse_index.split('.')[1]
            input_start_column = input_start_index.split('.')[1]
            if int(mouse_column) >= int(input_start_column):
                final_index += mouse_column
            else:
                final_index += input_start_column

            #print(mouse_index, input_start_index, final_index)
            #print(rel_x, rel_y, target.index('input_start'), target.index(f"@{rel_x},{rel_y}")    )
            target.mark_set('insert', final_index)
            
    def on_mouse_release(self, event):
        #check and destroy drag window        
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None

        # find out post type and target   
        x, y = event.x_root, event.y_root
        target = event.widget.winfo_containing(x,y)
        self.determine_post_target_and_type(target)

    def determine_post_target_and_type(self, target):        
        if target is self.postit_button: 
            # postit button pressed
            workbench = get_workbench()
            focus_widget = workbench.focus_get()
            if isinstance(focus_widget, CodeViewText):
                #focus  inside code editor
                editor = get_workbench().get_editor_notebook().get_current_editor()
                text = editor.get_text_widget()
                text.see('insert')
            
                #check selection and  delete selection
                if len(text.tag_ranges('sel')) :
                    #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
                    print("selection insert to editor")
                    self.selection_insert('EDITOR',text)
                else:
                    print("inster to editor")
                    self.insert_into_editor(self.code)
            elif isinstance(focus_widget, ShellText):
                # focus inside shell view
                text = focus_widget
                #check selection and  delete selection
                if len(text.tag_ranges('sel')) :
                    #replace selection 
                    #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
                    print("selection insert to shell")
                    self.selection_insert('SHELL',text)
                else:
                    print("insert to shell")
                    self.insert_into_shell(self.code)
                #self.direct_post()
        elif isinstance(target, CodeViewText):
            print("drag to editor")
            self.drag_to_editor()
        elif isinstance(target, ShellText):
            print("drag to shell")
            self.drag_to_shell()

    def selection_insert(self,target_type,  text):
        text.event_generate("<BackSpace>")
        if target_type == 'EDITOR':
            self.insert_into_editor(self.code)
        elif target_type == 'SHELL':
            self.insert_into_shell(self.code)


    def insert_into_editor(self, content):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()
        text.see('insert')

        lines = content.split('\n')            
        if len(lines) == 1:
            #one line
                text.direct_insert("insert",lines[0])
        else:
            #multi lines
            line_count = len(lines)
            for i, line in enumerate(lines):

                #if else else , need to add a extra backspack
                if line[:4] == 'else' or line[:4] == 'elif' :
                    text.event_generate("<BackSpace>")

                text.direct_insert("insert",line)

                #  generate enter if not last item
                if i < line_count - 1 :
                    text.event_generate("<Return>")

        if self.var_postfix_enter.get():
            text.event_generate("<Return>")

    def insert_into_shell(self, content):
        
        shell = get_shell()
        s = ''
            
        #check insert after input_start
        input_start_index = shell.text.index('input_start')
        insert_index = shell.text.index('insert')
 
        if shell.text.compare(insert_index, '>=' , input_start_index): 
            # insert after input_start
            before_insert_text = shell.text.get('input_start','insert')
            after_insert_text = shell.text.get('insert','end-1c')
            s = before_insert_text + content + after_insert_text
        else: # insert before input_start
            print(' In shell : insert before input_start')
            s = shell.text.get('input_start','end-1c') + content

        if self.var_postfix_enter.get():
            s += '\n'
        shell.submit_python_code(s)            

    def drag_to_editor(self):
        self.insert_into_editor(self.code)

    def drag_to_shell(self):
        self.insert_into_shell(self.code)


class BasePopup:
    def popup_init(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_checkbutton(label="結尾Enter換行", onvalue=1, offvalue=0, 
                variable=self.var_postfix_enter,
                command=self.toggle_postfix_enter,
                )
        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()


class BasePostit(BaseWidget, BaseCode, BasePost, BasePopup):
    """ composite and mixin approach base function postit"""
    def __init__(self,  tab_name, code, code_display=None, note=None, postfix_enter=False):
        self.widget_init(tab_name)
        self.code_init(code, code_display, note, postfix_enter)
        self.post_init()
        self.popup_init()
        


    
