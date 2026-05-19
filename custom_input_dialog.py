import customtkinter as ctk

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, mode: str = "filter", company_name: str = ""):
        super().__init__()
        self.geometry("1280x640")
        self.attributes("-topmost", True)
        
        self.user_input = None
        self.mode = mode
        self.company_name = company_name
        self.get_value_func = None

        if self.mode == "filter":
            self._setup_filter()
        elif self.mode == "note":
            self._setup_note()


    def _setup_filter(self):
        self.title("Filter Word(s)")
        
        label = ctk.CTkLabel(
            self, text="\n\n(You can add multiple words: senior, lead ...)", 
            font=("Arial", 24, "bold"), wraplength=1200)
        label.pack(pady=(40, 20), padx=20)

        self.entry = ctk.CTkEntry(self, font=("Arial", 24), width=500, height=50)
        self.entry.pack(pady=10)
        self.entry.focus()
        self.get_value_func = self.entry.get

        btn = ctk.CTkButton(self, text="Add to filter", font=("Arial", 20, "bold"), height=50, command=self.submit)
        btn.pack(pady=30)
        self.bind("<Return>", lambda event: self.submit())


    def _setup_note(self):
        self.title("Company Note")
        
        label = ctk.CTkLabel(
            self, text=f"Self-Reminder-Note for '{self.company_name}'", 
            font=("Arial", 24, "bold"), wraplength=1200)
        label.pack(pady=(40, 20), padx=20)

        self.textbox = ctk.CTkTextbox(self, font=("Arial", 24), width=800, height=300)
        self.textbox.pack(pady=10)
        self.textbox.focus()
        # end-1c to prevent CTK linebreak bug.
        self.get_value_func = lambda: self.textbox.get("0.0", "end-1c")
        
        btn = ctk.CTkButton(self, text="Save note", font=("Arial", 20, "bold"), height=50, command=self.submit)
        btn.pack(pady=30)


    def set_company_text(self, text: str) -> None:
        self.textbox.insert("0.0", text)


    def submit(self):
        self.user_input = self.get_value_func()
        self.destroy()


    def get_input(self):
        self.wait_window()
        return self.user_input