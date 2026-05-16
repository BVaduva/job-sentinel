import customtkinter as ctk

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, title, text):
        super().__init__()
        self.title(title)
        self.geometry("1280x640")
        self.attributes("-topmost", True)
        
        self.user_input = None

        label = ctk.CTkLabel(self, text=text, font=("Arial", 24, "bold"), wraplength=1200)
        label.pack(pady=(40, 20), padx=20)

        self.entry = ctk.CTkEntry(self, font=("Arial", 24), width=500, height=50)
        self.entry.pack(pady=10)
        self.entry.focus()

        btn = ctk.CTkButton(self, text="Add to filter", font=("Arial", 20, "bold"), height=50, command=self.submit)
        btn.pack(pady=30)

        self.bind("<Return>", lambda event: self.submit())

    def submit(self):
        self.user_input = self.entry.get()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.user_input