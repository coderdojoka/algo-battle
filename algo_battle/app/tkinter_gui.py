import tkinter as tk


def start_gui():
    root = tk.Tk()
    root.title("Algo-Battle")

    initial_width = 900
    initial_height = 1000
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry("{}x{}+{}+{}".format(
        initial_width, initial_height,
        (screen_width - initial_width) // 2,
        (screen_height - initial_height) // 2
    ))

    app = Application(root)
    app.mainloop()
    root.destroy()


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
