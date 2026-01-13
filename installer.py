#!/usr/bin/env python3
import os
import shutil
import stat
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class GraphicalInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Binly Installer")
        self.root.geometry("500x380")
        self.root.resizable(False, False)

        # Configurações de destino
        self.app_name = "binly"
        self.target_dir = os.path.expanduser("~/.local/bin")
        self.target_path = os.path.join(self.target_dir, self.app_name)

        # Lógica de detecção 2 em 1
        if hasattr(sys, '_MEIPASS'):
            # MODO BINÁRIO: O instalador é um executável gerado pelo PyInstaller
            # Ele procura o binário 'binly' empacotado junto com ele
            self.source_path = os.path.join(sys._MEIPASS, "binly")
            self.mode = "BINARY"
        else:
            # MODO SOURCE: O instalador está rodando como .py
            # Ele procura o 'binly.py' no mesmo diretório
            self.source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binly.py")
            self.mode = "SOURCE"

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Binly", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Installing to {self.target_dir}", font=("Arial", 10)).pack()

        self.log_box = tk.Text(self.root, height=8, width=55, bg="#1e1e1e", fg="#00ff00", font=("Monospace", 9))
        self.log_box.pack(pady=15, padx=20)
        self.log_box.insert(tk.END, f"System ready. Detection mode: {self.mode}\n")
        self.log_box.config(state=tk.DISABLED)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=5)

        self.btn_install = tk.Button(self.root, text="Install Now", bg="#28a745", fg="white", 
                                     font=("Arial", 10, "bold"), width=20, command=self.confirm_and_install)
        self.btn_install.pack(pady=10)

    def log(self, message):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, f"> {message}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def confirm_and_install(self):
        answer = messagebox.askyesno("Confirmation", f"Install '{self.app_name}' to {self.target_dir}?")
        if answer:
            self.btn_install.config(state=tk.DISABLED)
            threading.Thread(target=self.run_install_logic).start()

    def run_install_logic(self):
        try:
            self.log(f"Checking source: {os.path.basename(self.source_path)}...")
            self.progress['value'] = 20
            
            if not os.path.exists(self.source_path):
                raise FileNotFoundError(f"Source file not found: {self.source_path}")

            os.makedirs(self.target_dir, exist_ok=True)
            self.progress['value'] = 40

            if self.mode == "BINARY":
                self.log("Copying native binary...")
                shutil.copy2(self.source_path, self.target_path)
            else:
                self.log("Installing as Python script...")
                # Copia o binly.py para o destino mantendo a extensão para clareza interna
                internal_py = os.path.join(self.target_dir, ".binly_source.py")
                shutil.copy2(self.source_path, internal_py)
                
                # Cria o script "wrapper" sem extensão (estilo .sh mas limpo)
                self.log("Creating executable wrapper...")
                with open(self.target_path, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f'python3 "{internal_py}" "$@"\n')

            self.progress['value'] = 80
            self.log("Setting execution permissions (chmod +x)...")
            for path in [self.target_path]:
                st = os.stat(path)
                os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            self.progress['value'] = 100
            self.log("Installation successful!")
            messagebox.showinfo("Success", "Binly is now installed!\nType 'binly' in your terminal.")
            self.root.destroy()

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Installation Failed", str(e))
            self.btn_install.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicalInstaller(root)
    root.mainloop()