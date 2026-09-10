import customtkinter as ctk


def main():
    app = ctk.CTk()

    app.title("AI Coding Agent")
    app.geometry("700x450")
    app.minsize(500, 350)

    title_label = ctk.CTkLabel(
        app,
        text="AI Coding Agent",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.pack(pady=(120, 20))

    status_label = ctk.CTkLabel(
        app,
        text="Project not opened",
        font=ctk.CTkFont(size=16)
    )
    status_label.pack()

    app.mainloop()


if __name__ == "__main__":
    main()
