
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny import get_workbench, get_shell


#postit is  a frame with button and label
class SuggestVars:
    physical_stage = '物理舞台'



class Postit(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)


        bold = font.Font(size=10, weight=font.BOLD)
        #bold = font.Font(size=12)
        self.postit_button = tk.Button(self,  
                                        text='***' , 
                                        command=self.post, 
                                        fg='white', 
                                        bg='#4a6cd4',
                                        justify='left',
                                        font=bold,
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

        self.help_label = ttk.Label(self, text='' )
        self.help_label.pack(side=tk.LEFT, anchor='w')

        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="修改", command=self.on_modify)
        self.postit_button.bind("<Button-3>", self.popup)

        #dnd
        #self.postit_button.bind("<ButtonPress-1>", self.on_dnd_start)
        self.postit_button.bind("<B1-Motion>", self.on_dnd_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_dnd_drop)
        self.postit_button.configure(cursor="arrow")

    # def on_dnd_start(self, event):
    #     ###print('dnd start')

    #     pass

    def on_dnd_drag(self, event):
        ###print('drag ...')
        self.postit_button.configure(cursor="hand2")
        #change insert cursor in text
        x,y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x,y)
        
        
        if isinstance(target, CodeViewText):
            target.focus_set()
            rel_x = event.x_root - target.winfo_rootx()
            rel_y = event.y_root - target.winfo_rooty()
            ###print(rel_x ,rel_y )
            target.mark_set('insert', f"@{rel_x},{rel_y}")
            ###print(index)

    def on_dnd_drop(self, event):
        ###print('dnd drop')
        self.postit_button.configure(cursor="arrow")
        #x, y = event.widget.winfo_pointerxy()
        #target = event.widget.winfo_containing(x,y)
        self.post()

    def set_content(self, text):
        
        #lines = text.split('\n')
        #max_width = 0
        #for line in lines:
        #    max_width = len(line) if len(line) > max_width else  max_width
        #width = int(max_width*1.2)

        self.postit_button.config(text=text)
        

    def set_help_label(self, help_text):
        self.help_label.config(text=help_text)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()
    

    def on_modify(self):
        print('modify')

    def post(self):
        #shell = get_shell()
        #shell.submit_python_code(self.ent.get()+ '\n') 
        #shell.focus_set()
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()
        
        text.see('insert')
        #check selection

        if len(text.tag_ranges('sel')):
            #replace selection 
            text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
            text.direct_insert("insert", self.postit_button['text']) 


        else:
            #just insert
            #text.direct_insert("insert", self.postit_button['text'])
            lines = self.postit_button['text'].split('\n\t')
            ###print(lines)
            if len(lines) == 1:
                #one line
                text.direct_insert("insert",lines[0])
            else:
                #multi lines

                #handle last )
                is_parentheses_last = False
                temp_last = lines[-1]
                if temp_last[-2:] == '\n)':
                    is_parentheses_last = True
                    ###print('parentheses_last')
                    #remove \n) on last element
                    lines[-1] = temp_last[:-2]

                ###print(lines)
                for line in lines:
                    text.direct_insert("insert",line)
                    text.event_generate("<Return>")
                
                #print last ) if needed
                if is_parentheses_last:
                    text.event_generate("<BackSpace>")
                    text.direct_insert('insert', ')' )
                    text.event_generate("<Return>")

            # text.direct_insert("insert",'abc:')
            # text.event_generate("<Return>")
            # text.direct_insert("insert",'def')

class CallerPostit(Postit):
    pass

class PropertyPostit(Postit):
    def __init__(self, master):
        super().__init__(master)

    def on_modify(self):
        self.modify_popup = PropertyModifyPopup()
        
        #self.popup_win.attributes('-toolwindow', 'true')
        #self.popup_win.deiconify()
        #self.popup_win.grab_set()

        

class PropertyModifyPopup(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("修改")
        self.transient()
        self.grab_set()
        tk.Button(self, text="abc").pack()