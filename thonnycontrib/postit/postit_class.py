
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
                                        #command=self.post, 
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
        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.postit_button.configure(cursor="arrow")

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

    def on_mouse_release(self, event):
        ###print('dnd drop')
        self.postit_button.configure(cursor="arrow")

        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x,y)
        if target is self.postit_button or isinstance(target, CodeViewText):
            self.post()

    def set_content(self, text):
        
        #lines = text.split('\n')
        #max_width = 0
        #for line in lines:
        #    max_width = len(line) if len(line) > max_width else  max_width
        #width = int(max_width*1.2)
        ###print("set_context: ", text)
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
            ###print(self.postit_button['text'])
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
    def __init__(self, master, object_name, property_list, 
                    property_name, property_value, assign_flag):
        super().__init__(master)
        self.object_name = object_name
        self.property_list = property_list
        self.property_name = property_name
        self.property_value = property_value
        self.assign_flag = assign_flag
        
        #record default value
        self.default_object_name = object_name
        self.default_property_list = property_list
        self.default_property_name = property_name
        self.default_property_value = property_value
        self.default_assign_flag = assign_flag

        self.set_content(self.assemble_content())
        ###print(self.assemble_content())

    def on_modify(self):
        self.modify_popup = PropertyModifyPopup(self)
        
        #self.popup_win.attributes('-toolwindow', 'true')
        #self.popup_win.deiconify()
        #self.popup_win.grab_set()

    def assemble_content(self):
        if self.assign_flag:
            t = f'{self.object_name}.{self.property_name} = {self.property_value} '
        else:
            t = f'{self.object_name}.{self.property_name} '
        
        #self.postit_button.config(text=t)
        return t
        

class PropertyModifyPopup(tk.Toplevel):
    def __init__(self, postit,  *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("修改 -- ")
        self.postit = postit

        self.pady = 10
        self.padx = 20

        #copy data from postit
        # self.var_object_name = tk.StringVar()
        # self.var_object_name.set(self.postit.object_name + '.')

        self.var_property_name = tk.StringVar()
        self.var_property_name.set(self.postit.property_name)
        self.var_property_name.trace('w', lambda *args:self.update_literal())

        self.var_property_value = tk.StringVar()
        self.var_property_value.set(self.postit.property_value)
        self.var_property_value.trace('w', lambda *args:self.update_literal())

        self.var_assign_flag = tk.BooleanVar()
        self.var_assign_flag.set(self.postit.assign_flag)
        self.var_assign_flag.trace('w', lambda *args: self.update_assign_and_literal())
        

        #self.geometry('500x300')
        self.transient()
        self.grab_set()

        #mode frame (assign or get)
        self.mode_frame = ttk.Frame(self)
        self.mode_frame.pack(pady=self.pady)

        ttk.Radiobutton(self.mode_frame, text='設定值', variable=self.var_assign_flag, \
            value=True).pack(side='left')
        ttk.Radiobutton(self.mode_frame, text='取出值', variable=self.var_assign_flag, \
            value=False).pack(side='left')

        #select and input data frame
        self.select_frame = ttk.Frame(self)
        self.select_frame.pack(pady=self.pady)

        self.object_name_label = ttk.Label(self.select_frame, text=self.postit.object_name+'.')
        self.object_name_label.pack(side='left')

        self.property_name_combo = ttk.Combobox(self.select_frame, width=10, \
                                                textvariable=self.var_property_name,
                                                values=self.postit.property_list)
        #i = self.postit.property_list.index(self.postit.property_name)
        #self.property_name_combo.current(i)
        self.property_name_combo.pack(side='left')
        #self.property_name_combo.bind("<<ComboboxSelected>>", lambda e:self.update_literal())


        self.assign_label = ttk.Label(self.select_frame, text=' = ')
        #self.assign_label.pack(side='left')

        self.property_value_entry = ttk.Entry(self.select_frame, width=15, textvariable=self.var_property_value)
        #self.property_value_entry.pack(side='left')


        #literal frame
        self.literal_frame = ttk.LabelFrame(self, text='程式的寫法')
        self.literal_frame.pack(side='top',pady=self.pady, padx=self.padx, fill='both')

        
        self.literal_label = ttk.Label(self.literal_frame, text='')
        self.literal_label.pack(pady=self.pady, padx=self.padx)

        self.update_assign_and_literal() # also do update_literal

        #bottom frame ( buttons )
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side='bottom', pady=self.pady, anchor='e', fill='x')

        ttk.Button(self.bottom_frame, width=12, text="回復預設值", \
                    command=lambda: self.load_default()).pack(side='left', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="取消", \
                    command=lambda:self.destroy()).pack(side='right', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="套用修改", 
                command=lambda : self.update_postit(),
                ).pack(side='right', padx=5)


        #ttk.Button(self.bottom_frame, text="預設值", ).pack(side='right')
        
        

        #center popup  on screen
        # popup_width = self.winfo_reqwidth()
        # popup_height = self.winfo_reqheight()
        # position_right = int(self.winfo_screenwidth()/2 - popup_width/2)
        # position_down = int(self.winfo_screenheight()/2 - popup_height/2)
        popup_width = int(self.winfo_screenwidth()/3)
        popup_height = int(self.winfo_screenheight()/3)
        position_right =  int(self.winfo_screenwidth()*0.3)
        position_down = int(self.winfo_screenheight()*0.3) 

        self.geometry(f'{popup_width}x{popup_height}+{position_right}+{position_down}')


    def update_assign_and_literal(self):
        flag = self.var_assign_flag.get()
        if flag:
            self.assign_label.pack(side='left')
            self.property_value_entry.pack(side='left')
        else:
            self.assign_label.pack_forget()
            self.property_value_entry.pack_forget()

        self.update_literal()

    def update_literal(self):
        t = self.assemble_literal_content()
        self.literal_label.config(text=t)

    def assemble_literal_content(self):
        object_name = self.postit.object_name
        property_name = self.var_property_name.get()
        property_value = self.var_property_value.get()

        if self.var_assign_flag.get():            
            t = f'{object_name}.{property_name} = {property_value} '
        else:
            t = f'{object_name}.{property_name} '
        
        return t

    def update_postit(self):
        self.postit.property_name = self.var_property_name.get()
        self.postit.assign_flag = self.var_assign_flag.get()
        if self.postit.assign_flag:
            self.postit.property_value = self.var_property_value.get()

        self.postit.set_content(self.postit.assemble_content())
        self.destroy()

    def load_default(self):
        self.var_property_name.set(self.postit.default_property_name)
        self.var_property_value.set(self.postit.default_property_value)
        self.var_assign_flag.set(self.postit.default_assign_flag)
        self.update_assign_and_literal()

        



        