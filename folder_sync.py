import sys

if sys.version_info[0] < 3:
    sys.stderr.write("You need Python 3 or later to run this script!\n")
    sys.exit(1)

import os
import dirsync
import tkinter as tk
from tkinter import messagebox, filedialog

# GUI приложение
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.directory_source = None
        self.directory_destination = None
        self.dialog_window = None
        self.password = None
        self.source = "1"
        self.destination = "2"
        self.label_first = tk.Label(text="missing folder", fg="red")
        self.label_first.grid(row=0, column=2, sticky="nsew")
        self.label_second = tk.Label(text="missing folder", fg="red")
        self.label_second.grid(row=1, column=2, sticky="nsew")
        self.list_box = tk.Listbox(selectmode=tk.EXTENDED, height=2)
        self.list_box.grid(row=2, columnspan=3, sticky="nsew")
        self.button_source_local = tk.Button(text="Source local", activeforeground="blue", bg="#4e9a06",
                                             command=lambda: self.open_folder(self.source))
        self.button_source_local.grid(row=0, column=0, sticky="nsew")
        self.button_source_network = tk.Button(text="Source network", activeforeground="blue", bg="#4e9a06",
                                               command=lambda: self.network_configuration(self.source))
        self.button_source_network.grid(row=0, column=1, sticky="nsew")
        self.button_source_destination = tk.Button(text="Destination", activeforeground="blue", bg="#ffff00",
                                                   command=lambda: self.open_folder(self.destination))
        self.button_source_destination.grid(row=1, column=0, sticky="nsew")
        self.button_sync = tk.Button(text="sync", activeforeground="blue", bg="#ffb841", command=lambda: self.sync())
        self.button_sync.grid(row=3, column=0, sticky="nsew")
        self.button_delete = tk.Button(text="Delete", activeforeground="blue", bg="#ff496c",
                                       command=lambda: self.delete_folder())
        self.button_delete.grid(row=3, column=1, sticky="nsew")
        self.button_exit = tk.Button(text="Exit", activeforeground="blue", bg="#42aaff",
                                     command=lambda: self.exit())
        self.button_exit.grid(row=3, column=2, sticky="nsew")
        self.update_clock()
        self.master.bind('<Delete>', self.delete_folder)
        self.master.bind('<Escape>', self.exit)

    def dialog_window_setup(self):
        self.dialog_window = tk.Toplevel(self.master)
        # Сделать только второе окно активным
        self.dialog_window.grab_set()
        # Расположение по оси y
        x = self.dialog_window.winfo_screenwidth() // 2 - 150
        # Расположение по оси x
        y = self.dialog_window.winfo_screenheight() // 2 - 150
        self.dialog_window.title("Enter password for sudo")
        # Размеры GUI приложения
        self.dialog_window.geometry("260x50+{}+{}".format(x, y))
        # Масштабирование
        self.dialog_window.grid_columnconfigure(0, weight=1)
        self.dialog_window.grid_rowconfigure(0, weight=1)
        self.dialog_window.grid_rowconfigure(1, weight=1)
        self.password = tk.StringVar()
        entry_password = tk.Entry(self.dialog_window, textvariable=self.password, show='*')
        entry_password.grid(row=0, columnspan=3, sticky="nsew")
        button_password = tk.Button(self.dialog_window, text="Password entry", activeforeground="blue", bg="#4e9a06",
                                    command=self.close_dialog_window)
        button_password.grid(row=1, columnspan=3, sticky="nsew")
        self.dialog_window.bind('<Return>', self.close_dialog_window)
        self.dialog_window.mainloop()

    # Загрузка папки
    def open_folder(self, directory_selection):
        directory = tk.filedialog.askdirectory()
        # Проверка пути к папке на пустоту и на совпадение ранее загруженной папки с таким же именем
        if len(directory) and not directory == self.directory_source and not directory == self.directory_destination:
            """
            Если загружается папка-источник, то он добавляется в начало списка и удаляется ранее добавленный
            файл.
            Если загружается папка-назначение, то он добавляется в конец списка и удаляется ранее добавленный
            файл.
            """
            if directory_selection == self.source:
                if self.directory_source:
                    self.list_box.delete(0)
                self.list_box.insert(0, directory)
                self.directory_source = directory
            elif directory_selection == self.destination:
                if self.directory_destination:
                    self.list_box.delete(tk.END)
                self.list_box.insert(tk.END, directory)
                self.directory_destination = directory
            print(directory + " LOADED")

    # Закрыть второе окно
    def close_dialog_window(self, event=None):
        self.dialog_window.destroy()
        self.dialog_window.quit()

    # Настройка сетевой папки
    def network_configuration(self, directory_selection):
        self.dialog_window_setup()
        # Ввод команды с паролем в терминал
        command = "sudo mount -a"
        no_access = os.system('echo %s | sudo -S %s' % (self.password.get(), command))
        # Проверка на пароль
        if no_access:
            self.network_configuration(directory_selection)
        else:
            self.open_folder(directory_selection)

    def sync(self, event=None):
        """
        Синхронизация папок.
        Все файлы из папки источника будут скопированы в папку назначение.
        Совпадающие элементы будут пропущены.
        Лишние элементы в папке назначения будут удалены.
        """
        dirsync.sync(self.directory_source, self.directory_destination, 'sync', purge=True)
        self.button_sync["text"] = "Success",

    # Удаление папки(ок) при нажатии или выделении через shift
    def delete_folder(self, event=None):
        select = list(self.list_box.curselection())
        select.reverse()
        for i in select:
            directory = self.list_box.get(i)
            if directory == self.directory_source:
                self.directory_source = None
            elif directory == self.directory_destination:
                self.directory_destination = None
            self.list_box.delete(i)
            print(directory + " DELETED")

    # Выход из программы
    def exit(self, event=None):
        ask = messagebox.askquestion(title="Exit", message="Are you sure to quit?")
        if ask == "yes":
            self.master.destroy()
            self.master.quit()

    def update_clock(self):
        """
        Таймер, который проверяет через каждые (несколько) миллисекунд на наличие двух загруженных папок.
        Если обе папки не загружены, то кнопка button_sync недоступна.
        """
        if self.directory_source:
            self.label_first.config(text=os.path.basename(self.directory_source) + "\nLOADED", fg="blue")
        else:
            self.label_first.config(text="missing folder", fg="red")

        if self.directory_destination:
            self.label_second.config(text=os.path.basename(self.directory_destination) + "\nLOADED", fg="blue")
        else:
            self.label_second.config(text="missing folder", fg="red")

        if self.list_box.size() == 2:
            self.button_sync.config(state=tk.ACTIVE, bg="#ffb841")
            self.master.bind('<s>', self.sync)
        else:
            self.button_sync.config(state=tk.DISABLED, bg="white")
            self.master.unbind('<s>')
        self.after(100, self.update_clock)

def main():
    root = tk.Tk()
    # Ширина экрана
    width = root.winfo_screenwidth()
    # Высота экрана
    height = root.winfo_screenheight()
    # Середина экрана
    width = width // 2
    height = height // 2
    # Смещение от середины
    width = width - 200
    height = height - 200
    root.title("Choose Folders")
    # Размеры GUI приложения
    root.geometry("400x200+{}+{}".format(width, height))
    # Масштабирование
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    Application(master=root)
    root.mainloop()

if __name__ == "__main__":
    main()



