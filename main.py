import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
        self.root.configure(bg="#121212") # Deep dark background

        self.accounts = self.load_vault()
        self.bubbles = {} # To store the label objects for updating

        # --- Header ---
        self.header = tk.Label(root, text="My codes", font=("Segoe UI", 20, "bold"), 
                              fg="#00adb5", bg="#121212", pady=20)
        self.header.pack()

        # --- Scrollable Area ---
        self.container = tk.Frame(root, bg="#121212")
        self.container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(self.container, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Footer Button ---
        self.import_btn = tk.Button(root, text="+ Import QR Screenshot from Website", command=self.import_qr, 
                                   bg="#00adb5", fg="white", font=("Segoe UI", 10, "bold"),
                                   relief="flat", padx=20, pady=10, cursor="hand2")
        self.import_btn.pack(pady=20)

        self.render_bubbles()
        self.update_loop()

    def load_vault(self):
        if VAULT_PATH.exists():
            with open(VAULT_PATH, "r") as f:
                return json.load(f)
        return {}

    def save_vault(self):
        with open(VAULT_PATH, "w") as f:
            json.dump(self.accounts, f, indent=4)

    def render_bubbles(self):
        # Clear existing bubbles
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.bubbles = {}

        for name, data in self.accounts.items():
            # The "Bubble" Container
            bubble = tk.Frame(self.scrollable_frame, bg="#1e1e1e", padx=15, pady=15, 
                              highlightbackground="#333333", highlightthickness=1)
            bubble.pack(fill="x", pady=8, padx=5)

            # Site and Username labels
            info_frame = tk.Frame(bubble, bg="#1e1e1e")
            info_frame.pack(side="left", fill="y")
            
            tk.Label(info_frame, text=name.upper(), font=("Segoe UI", 12, "bold"), 
                     fg="#00adb5", bg="#1e1e1e").pack(anchor="w")
            
            user_text = data.get('user', 'Account')
            tk.Label(info_frame, text=user_text, font=("Segoe UI", 9), 
                     fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w")

            # The Live Code
            code_label = tk.Label(bubble, text="000 000", font=("Consolas", 18, "bold"), 
                                 fg="white", bg="#1e1e1e")
            code_label.pack(side="right")
            
            self.bubbles[name] = code_label

    def import_qr(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not file_path: return

        try:
            img = Image.open(file_path)
            decoded = decode(img)
            if not decoded:
                messagebox.showerror("Error", "No QR code detected.")
                return

            qr_data = decoded[0].data.decode('utf-8')
            parsed = pyotp.parse_uri(qr_data)
            
            issuer = parsed.issuer if parsed.issuer else "Unknown"
            self.accounts[issuer] = {
                "secret": parsed.secret,
                "user": parsed.name
            }
            self.save_vault()
            self.render_bubbles() # Refresh the list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def update_loop(self):
        for name, data in self.accounts.items():
            if name in self.bubbles:
                totp = pyotp.TOTP(data['secret'])
                raw_code = totp.now()
                formatted = f"{raw_code[:3]} {raw_code[3:]}"
                self.bubbles[name].config(text=formatted)
        
        # Every 1 second
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    # A bit of styling for the scrollbar on Linux/Windows
    style = ttk.Style()
    style.theme_use('clam')
    app = Aurauth(root)
    root.mainloop()
