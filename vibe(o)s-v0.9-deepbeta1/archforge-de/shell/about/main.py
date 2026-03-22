import customtkinter as ctk

class AboutWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("About vibe(O)s")
        self.geometry("450x300")
        ctk.set_appearance_mode("Dark")
        
        # Main Container
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title
        lbl_title = ctk.CTkLabel(frame, text="vibe(O)s", font=("Inter", 42, "bold"), text_color="#a371f7")
        lbl_title.pack(pady=(10, 5))
        
        lbl_subtitle = ctk.CTkLabel(frame, text="The Next-Gen Wayland Desktop Environment", font=("Inter", 14, "italic"), text_color="gray")
        lbl_subtitle.pack(pady=(0, 20))
        
        # Credits
        credits_box = ctk.CTkFrame(frame, corner_radius=10)
        credits_box.pack(fill="x", pady=10, ipady=10)
        
        lbl_credits1 = ctk.CTkLabel(credits_box, text="Made by Gemini 3.1 Pro (so far)", font=("Inter", 16, "bold"))
        lbl_credits1.pack(pady=5)
        
        lbl_credits2 = ctk.CTkLabel(credits_box, text="Prompted by ray0ffire/minerofthesoal", font=("Inter", 14))
        lbl_credits2.pack(pady=5)
        
        # Close Button
        btn_close = ctk.CTkButton(frame, text="Awesome", width=120, command=self.destroy)
        btn_close.pack(pady=(20, 0))

if __name__ == "__main__":
    app = AboutWindow()
    app.mainloop()
