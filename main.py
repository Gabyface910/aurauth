import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pyotp
import json
from pathlib import Path
from PIL import Image
from pyzbar.pyzbar import decode

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
VAULT_PATH = BASE_DIR / "secrets.json"

class Aurauth:
    def __init__(self, root):
        self.root = root
        self.root.title("Aurauth")
        self.root.geometry("400x600")
        self.root.configure(bg="#121212")

        self.accounts = self.load_vault()
        self.bubbles = {}

        # Header
        tk.Label(root, text="AURAUTH", font=("Segoe UI", 20, "bold"), 
                 fg="#00adb5", bg="#121212", pady=20).pack()

        # Scrollable Area
        self.container = tk.Frame(root, bg="#121212")
        self.container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(self.container, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Import Button
        tk.Button(root, text="+ Import QR", command=self.import_qr, 
                  bg="#00adb5", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", pady=10).pack(fill="x", padx=10, pady=10)

        self.render_bubbles()
        self.update_loop()

    def load_vault(self):
        if VAULT_PATH.exists():
            with open(VAULT_PATH, "r") as f: return json.load(f)
        return {}

    def save_vault(self):
        with open(VAULT_PATH, "w") as f: json.dump(self.accounts, f, indent=4)

    def copy_code(self, code_text, button_widget):
        clean = code_text.replace(" ", "").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(clean)
        self.root.update()
        
        # Flash the button color to show it worked
        button_widget.config(fg="#00adb5") # Turn cyan
        self.root.after(200, lambda: button_widget.config(fg="white")) # Switch back
    def delete_account(self, name):
        if messagebox.askyesno("Delete", f"Remove {name}?"):
            del self.accounts[name]
            self.save_vault()
            self.render_bubbles()

    def render_bubbles(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.bubbles = {}

        for name, data in self.accounts.items():
            bubble = tk.Frame(self.scrollable_frame, bg="#1e1e1e", padx=10, pady=10, 
                              highlightbackground="#333333", highlightthickness=1)
            bubble.pack(fill="x", pady=5, padx=5)

            # Info
            info = tk.Frame(bubble, bg="#1e1e1e")
            info.pack(side="left")
            tk.Label(info, text=name.upper(), font=("Segoe UI", 11, "bold"), fg="#00adb5", bg="#1e1e1e").pack(anchor="w")
            tk.Label(info, text=data.get('user', 'Account'), font=("Segoe UI", 8), fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w")

            # Actions
            btn_frame = tk.Frame(bubble, bg="#1e1e1e")
            btn_frame.pack(side="right")
            
            # Code Button (Click to Copy)
            # The Live Code Button
            # We pass the current label object (lbl) explicitly to the lambda
            # 1. Create the label/button first
            lbl = tk.Button(btn_frame, text="000 000", font=("Consolas", 18, "bold"), 
                            fg="white", bg="#1e1e1e", relief="flat", cursor="hand2")
            lbl.pack(side="left", padx=10)

            # 2. Assign the command AFTER the variable exists
            # We use the lambda to capture the specific instance of 'lbl'
            lbl.config(command=lambda current_lbl=lbl: self.copy_code(current_lbl.cget("text"), current_lbl))
            
            # 3. Update copy_code to accept the button widget (for the color flash)
            self.bubbles[name] = lbl
            
            # Delete Button
            tk.Button(btn_frame, text="✕", fg="#ff5555", bg="#1e1e1e", relief="flat",
                      command=lambda n=name: self.delete_account(n)).pack(side="right")
            
            self.bubbles[name] = lbl

    def import_qr(self):
        path = filedialog.askopenfilename()
        if not path: return
        try:
            img = Image.open(path)
            decoded = decode(img)
            qr_data = decoded[0].data.decode('utf-8')
            parsed = pyotp.parse_uri(qr_data)
            self.accounts[parsed.issuer or "Unknown"] = {"secret": parsed.secret, "user": parsed.name}
            self.save_vault()
            self.render_bubbles()
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_loop(self):
        for name, data in self.accounts.items():
            if name in self.bubbles:
                code = pyotp.TOTP(data['secret']).now()
                self.bubbles[name].config(text=f"{code[:3]} {code[3:]}")
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aurauth(root)
    root.mainloop()
