
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell


#postit is  a frame with button and label
# class Pie4tSuggestVars:
#     physical_stage = '物理舞台'



class Postit(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)


        bold = font.Font(size=10, weight=font.BOLD)
        #bold = font.Font(size=12)
        self.postit_button = tk.Button(self,  
                                        text='***' , 
                                        #command=self.post, 
                                        fg='white', 
                                        bg='#4a6cd4',
                                        justify='left',
                                        font=bold,
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w')

        self.code = ''   # real code text on post

    # def on_dnd_start(self, event):
    #     ###print('dnd start')

    #     pass

    def on_mouse_drag(self, event):
        ###print('drag ...')
        self.postit_button.configure(cursor="hand2")
        #change insert cursor in text
        x,y = event.widget.winfo_pointerxy()
        ###print(x,y)
        target = event.widget.winfo_containing(x,y)
        
        
        if isinstance(target, CodeViewText):
            target.focus_set()
            #rel_x = event.x_root - target.winfo_rootx()
            #rel_y = event.y_root - target.winfo_rooty()
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

    def set_code_display(self, text):
        
        #lines = text.split('\n')
        #max_width = 0
        #for line in lines:
        #    max_width = len(line) if len(line) > max_width else  max_width
        #width = int(max_width*1.2)
        ###print("set_context: ", text)
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
    

    # def on_modify(self):
    #     print('modify')

    def post(self):
    
        workbench = get_workbench()
        focus_widget = workbench.focus_get()

        if isinstance(focus_widget, CodeViewText):
            #in code view
            self.post_to_editor()
            
        elif isinstance(focus_widget, ShellText):
            #in shell
            self.post_to_shell()
        else:
            # not in code view and not in shell
            pass

    def post_to_editor(self):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()

        text.see('insert')
        
        #check selection
        if len(text.tag_ranges('sel')):
            #replace selection 
            text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
         
        lines = self.code.split('\n')            
        if len(lines) == 1:
            #one line
            text.direct_insert("insert",lines[0])
        else:
            #multi lines
            line_count = len(lines)
            for i, line in enumerate(lines):

                text.direct_insert("insert",line)

                #  generate enter if not last item
                if i < line_count - 1 :
                    text.event_generate("<Return>")
        
    def post_to_shell(self):        
        shell = get_shell()
        #origin_text = shell.text.get('input_start','end-1c')
        #print('---', origin_text, '---')
        shell.submit_python_code( origin_text + self.code)         










        