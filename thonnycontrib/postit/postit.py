
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .common import common_variable_set

#postit is  a frame with button and label(note)
class Postit(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.gui_init(master)
        self.code = ''   # real code text on post

    def gui_init(self, master):
        f = font.Font(size=12, weight=font.NORMAL)
        self.postit_button = tk.Button(self,  
                                        text='***' , 
                                        fg='white', 
                                        bg='#4a6cd4',
                                        justify='left',
                                        font=f,
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w')

        #support drag 
        self.mouse_dragging = False

        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.postit_button.configure(cursor="arrow")
        


    def on_mouse_drag(self, event):
        ###print('drag ...')
        self.postit_button.configure(cursor="hand2")
        #change insert cursor in text
        x,y = event.widget.winfo_pointerxy()
        ###print(x,y)
        target = event.widget.winfo_containing(x,y)
        self.mouse_dragging = True
        
        if isinstance(target, CodeViewText):
            target.focus_set()
            rel_x = x - target.winfo_rootx()
            rel_y = y - target.winfo_rooty()

            ###print(rel_x ,rel_y )
            target.mark_set('insert', f"@{rel_x},{rel_y}")
            ###print(index)
        elif isinstance(target, ShellText):
            shell = get_shell()
            shell.focus_set()


    def on_mouse_release(self, event):
        ###print('dnd drop')
        self.postit_button.configure(cursor="arrow")

        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x,y)
        if target is self.postit_button or isinstance(target, CodeViewText) \
                or isinstance(target, ShellText):
            self.post()

        self.mouse_dragging = False

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
    

    def post(self, space_surround_inline=False, postfix_newline=False):
    
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
                text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
            
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
        














        