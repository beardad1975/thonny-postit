
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

#postit is  a frame with button and label(note)
class Postit(ttk.Frame):
    def __init__(self, tab_name):
        self.tab_name = tab_name
        self.tab = common_postit_tabs[tab_name]
        self.var_postfix_newline = tk.BooleanVar()
        self.var_postfix_newline.set(False)
        #im = Image.open(Path(__file__).parent / 'images' / 'enter.png')       
        self.enter_image = common_images['enter']
        self.drag_window = None 

        ttk.Frame.__init__(self, self.tab.frame)
        self.gui_init()
        self.code = ''   # real code text on post

        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_checkbutton(label="結尾Enter換行", onvalue=1, offvalue=0, 
                variable=self.var_postfix_newline,
                command=self.toggle_postfix_newline,
                )
        self.postit_button.bind("<Button-3>", self.popup)

    def gui_init(self):
        f = font.Font(size=11, weight=font.NORMAL, family='Microsoft JhengHei')
        #f = font.Font(size=11, weight=font.NORMAL, )
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
        self.update_button_enter_sign()

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)

        #support drag 
        self.mouse_dragging = False

        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        #self.postit_button.configure(cursor="arrow")
        
    def update_button_enter_sign(self):
        if self.var_postfix_newline.get():
            self.postit_button.config(image=self.enter_image)
        else:
            self.postit_button.config(image='')


    def on_mouse_drag(self, event):
        ###print('drag ...')
        #create drag window
        if not self.drag_window:
            self.mouse_dragging = True

            self.drag_window = tk.Toplevel()
            bg = self.postit_button.cget('bg')
            fg = self.postit_button.cget('fg')
            text = self.postit_button.cget('text')
            tk.Label(self.drag_window, text=text, bg=bg, fg=fg).pack()
            self.drag_window.overrideredirect(True)
            self.drag_window.attributes('-topmost', 'true')

        self.drag_window.geometry('+{}+{}'.format(event.x_root+10, event.y_root+10))

        #self.postit_button.configure(cursor="hand2")
        #change insert cursor in text
        #x,y = event.widget.winfo_pointerxy()
        #print(event.x, event.y)
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
            
            #shell = get_shell()
            #shell.focus_set()


    def on_mouse_release(self, event):
        ###print(' drop')
        #self.postit_button.configure(cursor="arrow")
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None

            self.mouse_dragging = False

        x, y = event.x_root, event.y_root
        target = event.widget.winfo_containing(x,y)
        if target is self.postit_button: 
            # press postit button
            self.press_postit()
        elif isinstance(target, CodeViewText):
            # drag to editor
            self.drag_to_editor()
        elif isinstance(target, ShellText):
            # drag to shell
            self.drag_to_shell()

        

    def set_code_display(self, text):
        self.postit_button.config(text=text)

    def set_code(self, text):
        self.code = text


    def set_note(self, help_text):
        self.note_label.config(text=help_text)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()
    
    def toggle_postfix_newline(self):
        r = self.var_postfix_newline.get()
        self.var_postfix_newline.set(r)
        self.update_button_enter_sign()

    def post(self, space_surround_inline=False):
        postfix_newline=self.var_postfix_newline.get()
        workbench = get_workbench()
        focus_widget = workbench.focus_get()

        if isinstance(focus_widget, CodeViewText):
            #in code view
            #self.post_to_editor(space_surround_inline, postfix_newline)
            editor = get_workbench().get_editor_notebook().get_current_editor()
            text = editor.get_text_widget()

            text.see('insert')
            
            #check selection
            if len(text.tag_ranges('sel')) and not self.mouse_dragging:
                #replace selection 
                #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
                text.event_generate("<BackSpace>")
            
            lines = self.code.split('\n')            
            if len(lines) == 1:
                #one line
                if space_surround_inline:
                    text.direct_insert("insert", " "+lines[0]+" ")
                else:
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

            if postfix_newline:
                text.event_generate("<Return>")

        elif isinstance(focus_widget, ShellText):
            #in shell
            #self.post_to_shell(space_surround_inline, postfix_newline)
            shell = get_shell()
            origin_text = shell.text.get('input_start','end-1c')
            #print('---', origin_text, '---')
            
            #need to test multiline in shell
            if space_surround_inline:
                shell.submit_python_code( origin_text + " " + self.code + " ") 
            else:
                if postfix_newline:
                    shell.submit_python_code( origin_text + self.code + '\n')
                else:
                    shell.submit_python_code( origin_text + self.code)

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

        if self.var_postfix_newline.get():
            text.event_generate("<Return>")

    def insert_into_shell(self, content):
        
        shell = get_shell()
        before_insert_text = shell.text.get('input_start','insert')
        after_insert_text = shell.text.get('insert','end-1c')

        s = before_insert_text + content + after_insert_text
        if self.var_postfix_newline.get():
            s += '\n'
        shell.submit_python_code(s)            

    #may be static method
    def press_postit(self):
        workbench = get_workbench()
        focus_widget = workbench.focus_get()

        if isinstance(focus_widget, CodeViewText):
            #in code view
            #self.post_to_editor(space_surround_inline, postfix_newline)
            editor = get_workbench().get_editor_notebook().get_current_editor()
            text = editor.get_text_widget()
            text.see('insert')
            
            #check selection and  delete selection
            if len(text.tag_ranges('sel')) :
                #replace selection 
                #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
                text.event_generate("<BackSpace>")
            
            self.insert_into_editor(self.code)


        elif isinstance(focus_widget, ShellText):
            # in shell view
            text = focus_widget
            #check selection and  delete selection
            if len(text.tag_ranges('sel')) :
                #replace selection 
                #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
                text.event_generate("<BackSpace>")

            self.insert_into_shell(self.code)


    def drag_to_editor(self):
        self.insert_into_editor(self.code)

    def drag_to_shell(self):
        self.insert_into_shell(self.code)
         
class PostitWithCombobox(Postit):
    def __init__(self, master):
        super().__init__(master)
    
    def gui_init(self , master):
        f = font.Font(size=10, weight=font.NORMAL)





        self.postit_button = tk.Button(self,  
                                        text='***' , 
                                        fg='white', 
                                        bg='#4a6cd4',
                                        justify='left',
                                        font=f,
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

        self.postit_combo = ttk.Combobox(self, width=10,justify=tk.CENTER, values=sorted(common_variable_set))
        #i = self.postit.property_list.in   dex(self.postit.property_name)
        self.postit_combo.current(0)
        self.postit_combo.pack(side='left', padx=5)


        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w')

        #support drag 
        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.postit_button.configure(cursor="arrow")
        














        