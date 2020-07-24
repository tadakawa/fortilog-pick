import tkinter.ttk as ttk
import tkinter as tk


class ScrolledListbox(tk.Listbox):
    ''' Listbox with vertical scroll bar '''
    def __init__(self, master, *args, **kwargs):
        ''' Initialise a new object.

        Args:
            master: master widget
        '''
        self.frame = tk.Frame(master)
        self.yscroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.yview)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        super().__init__(self.frame, yscrollcommand=self.yscroll.set, *args, **kwargs)
        super().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)


class ItemSelectionListbox(tk.Frame):
    ''' 2-pane item selection Listbox '''
    def __init__(self, master, items, selected_items=None, *args, **kwargs):
        ''' Initialise a new object.

        Args:
            master: master widget
            items: (list), A list of items to select.
            selected_items: (list),: A list of selected items.
        '''
        class Listbox(ScrolledListbox):
            def __init__(self, master, *args, **kwargs):
                self.var = tk.StringVar()
                super().__init__(master=master, listvariable=self.var, *args, **kwargs)
                self.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        class Frame(tk.Frame):
            def __init__(self, master, *args, **kwargs):
                super().__init__(master=master, *args, **kwargs)
                self.pack(side=tk.LEFT, fill=tk.Y)

        class Button(ttk.Button):
            def __init__(self, master, text, command, *args, **kwargs):
                super().__init__(master=master, text=text, command=command, *args, **kwargs)
                self.bind('<Return>', command)
                self.pack()

        if selected_items is None:
            selected_items = []
        # Checking argument types
        if type(items) not in [list, tuple]:
            raise TypeError("'items' must be of type list or tuple")
        if type(selected_items) not in [list, tuple]:
            raise TypeError("'selected_items' must be of type list or tuple")

        # Removing duplicate elements from items
        self.items = sorted(set(items), key=items.index)
        # Removing duplicate elements from selected_items and elements not in items
        self.selected_items = sorted(set(selected_items), key=selected_items.index)
        self.selected_items = [i for i in self.selected_items if i in self.items]
        # Save the initial values of items and selected_items
        self.init_items = self.items.copy()
        self.init_selected_items = self.selected_items.copy()
        # Remove selected items from items
        self.items = [i for i in self.items if i not in self.selected_items]

        # Create Widgets
        super().__init__(master=master, *args, **kwargs)
        self.left_pane = Listbox(master=self)   # left pane
        self.fr1 = Frame(master=self)           # Frame for buttons that select the item
        self.right_pane = Listbox(master=self)  # right pane
        self.fr2 = Frame(master=self)           # Frame for buttons that move the selected item

        # Create buttons that select the item
        Button(self.fr1, "ALL >>", self.__move_right_all)
        Button(self.fr1, ">", self.__move_right)
        Button(self.fr1, "<", self.__move_left)
        Button(self.fr1, "<< ALL", self.__move_left_all)
        Button(self.fr1, "init", self.__initialize)
        # Create buttons that move the selected item
        Button(self.fr2, "TOP", self.__move_top)
        Button(self.fr2, "^", self.__move_up)
        Button(self.fr2, "v", self.__move_down)
        Button(self.fr2, "BOTTOM", self.__move_bottom)

        # key bind
        key_bind = [
            (self.left_pane, ('<Double-Button-1>', '<Return>', '<space>'), self.__move_right),
            (self.left_pane, ('<Right>',), self.__set_focus_to_right),
            (self.right_pane, ('<Double-Button-1>', '<Return>', '<space>'), self.__move_left),
            (self.right_pane, ('<Left>',), self.__set_focus_to_left),
            (self.right_pane, ('<Alt-Key-Up>',), self.__move_up),
            (self.right_pane, ('<Alt-Key-Down>',), self.__move_down),
        ]
        for w, keys, command in key_bind:
            for k in keys:
                w.bind(k, command)

        self.__set_var()

    def __move_to(self, src_index, dst_index):
        ''' Move the selected item in the right pane.

        Args:
            src_index: (int), source index
            dst_index: (int), distination index
        '''
        if not (0 <= src_index <= len(self.selected_items) - 1):
            return
        if not (0 <= dst_index <= len(self.selected_items) - 1):
            return
        if src_index == dst_index:
            return
        item = self.right_pane.get(src_index)
        self.selected_items.remove(item)
        self.selected_items.insert(dst_index, item)
        self.__set_var()
        self.right_pane.selection_clear(src_index)
        self.right_pane.selection_set(dst_index)
        self.right_pane.see(dst_index)

    def __move_top(self, event=None):
        ''' Move the selected item in the right pane to the top. '''
        for i in self.right_pane.curselection():
            self.__move_to(i, 0)

    def __move_up(self, event=None):
        ''' Move the selected item in the right pane up one line. '''
        for i in self.right_pane.curselection():
            self.__move_to(i, i - 1)

    def __move_down(self, event=None):
        ''' Move the selected item in the right pane down one line. '''
        for i in self.right_pane.curselection():
            self.__move_to(i, i + 1)

    def __move_bottom(self, event=None):
        ''' Move the selected item in the right pane to the bottom. '''
        for i in self.right_pane.curselection():
            self.__move_to(i, len(self.selected_items) - 1)

    def __move_right(self, event=None):
        ''' Move the selected item in the left pane to the right pane.
            Add it to the bottom.
        '''
        for i in self.left_pane.curselection():
            item = self.left_pane.get(i)
            self.selected_items.append(item)
            self.items = [i for i in self.init_items if i not in self.selected_items]
            self.__set_var()
            self.__activate(self.right_pane, tk.END)

    def __move_left(self, event=None):
        ''' Move the selected item in the right pane to the left pane.
            Move back to the original position.
        '''
        for i in self.right_pane.curselection():
            item = self.right_pane.get(i)
            self.selected_items.remove(item)
            self.items = [i for i in self.init_items if i not in self.selected_items]
            self.__set_var()
            self.__activate(self.left_pane, self.items.index(item))

    def __move_right_all(self, event=None):
        ''' Move all items in the left pane to the right pane.
            Add them to the bottom.
        '''
        self.selected_items.extend(self.items)
        self.items = []
        self.__set_var()

    def __move_left_all(self, event=None):
        ''' Move all items in the right pane to the left pane.
            Move back to the original position.
        '''
        self.selected_items = []
        self.items = self.init_items.copy()
        self.__set_var()
        self.__activate(self.left_pane, 0)

    def __initialize(self, event=None):
        ''' Restore the selected items to their initial values. '''
        self.selected_items = self.init_selected_items.copy()
        self.items = [i for i in self.init_items if i not in self.selected_items]
        self.__set_var()
        self.__activate(self.left_pane, 0)
        self.__activate(self.right_pane, 0)

    def __set_focus_to_right(self, event=None):
        ''' Set the focus to the right pane '''
        self.left_pane.selection_clear(0, tk.END)
        self.right_pane.focus_set()

    def __set_focus_to_left(self, event=None):
        ''' Set the focus to the left pane '''
        self.right_pane.selection_clear(0, tk.END)
        self.left_pane.focus_set()

    def __set_var(self):
        ''' Set the focus to the left pane '''
        self.left_pane.var.set(value=self.items)
        self.right_pane.var.set(value=self.selected_items)

    def __activate(self, listbox, index):
        ''' Activate the specified index '''
        listbox.selection_clear(0, tk.END)
        listbox.activate(index)
        listbox.see(index)

    def get_var(self):
        return self.selected_items

    def print(self):
        print(self.selected_items)


if __name__ == '__main__':
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    select = ['Feb', 'Apr', 'Jun', 'Sep', 'Nov']

    root = tk.Tk()
    s = ItemSelectionListbox(root, month, select)
    s.pack(fill=tk.BOTH, expand=1)
    ttk.Button(root, text='print', command=s.print).pack()

    s = ItemSelectionListbox(root, tuple(range(100)) + tuple(range(100)), tuple(range(0, 200, 3)))
    s.pack(fill=tk.BOTH, expand=1)
    ttk.Button(root, text='print', command=s.print).pack()
    root.mainloop()
