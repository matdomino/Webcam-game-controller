import customtkinter as ctk
import keyboard
from .config_handler import save_config, restore_to_default, read_config

class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, command, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = ctk.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, value):
        label = ctk.CTkLabel(self, text=item, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text=value, width=100, height=24, fg_color="transparent",
                                border_width=2,)
        button.configure(command=lambda: self.command(item, value))

        label.grid(row=len(self.label_list) + 2, column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list) + 2, column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

def controlls_menu(menu_gui, root):
    new_config = menu_gui.config.copy()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    controlls = ctk.CTkFrame(master=root)
    controlls.pack(pady=0, padx=0, fil="both", expand=True)

    def close_controlls_cb():
        menu_gui.config = read_config()
        menu_gui.open_menu(controlls, menu_gui, root)

    def restore_controls():
        restore_to_default()
        close_controlls_cb()

    def save_current_config():
        save_config(new_config)
        close_controlls_cb()

    def change_bind(item, value):
        for button, label in zip(controls_list.button_list, controls_list.label_list):
            if button.cget("text") == value and label.cget("text") == item:
                button.configure(fg_color="#144870")
                button.configure(text="Enter a key: ")

                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    key_name = event.name
                    button.configure(text=key_name)
                    button.configure(command=lambda: controls_list.command(item, key_name))
                    button.configure(fg_color="transparent")
                    new_config["keyboard"][item] = key_name

                break

    def slider_event(value):
        normalized_value = float(value) / 100
        sensitivity_val_label.configure(text=f"{normalized_value:.2f}")

        new_config["mouse"]["mouse-sensitivity"] = round(value)

    def change_refresh_rate(value):
        new_config["mouse"]["pointer-refresh-rate"] = int(value)

    go_back = ctk.CTkButton(master=controlls, text="← Go back", fg_color="transparent",
                            border_width=2, command=close_controlls_cb)
    go_back.place(relx=0.04, rely=0.04, anchor="nw")

    header_label = ctk.CTkLabel(master=controlls, text="Controls",
                                font=ctk.CTkFont(size=24, weight="bold"))
    header_label.place(relx=0.04, rely=0.15, anchor="nw")

    controls_list = ScrollableLabelButtonFrame(master=controlls, width=537, height=235,
                                                command=change_bind, corner_radius=0,
                                                fg_color="transparent")
    controls_list.grid(row=0, column=2, padx=24, pady=100, sticky="nsew")

    for key, val in new_config["keyboard"].items():
        controls_list.add_item(key, val)

    sensitivity_label = ctk.CTkLabel(master=controls_list, text="Mouse Sensitivity", anchor="w")
    sensitivity_label.grid(row=0, column=0, pady=(10, 0), padx=5, sticky="w")

    sensitivity_slider = ctk.CTkSlider(master=controls_list, from_=0, to=100, command=slider_event, width=140)
    sensitivity_slider.set(new_config["mouse"]["mouse-sensitivity"])
    sensitivity_slider.grid(row=0, column=1, pady=(10, 0), sticky="ew")

    sensitivity_val_label = ctk.CTkLabel(master=controls_list, text=f"{(sensitivity_slider.get() / 100):.2f}", anchor="w")
    sensitivity_val_label.grid(row=0, column=2, pady=(10, 0), padx=(0, 10), sticky="w")

    pointer_rate_label = ctk.CTkLabel(master=controls_list, text="Pointer Refresh Rate [Hz]", anchor="w")
    pointer_rate_label.grid(row=1, column=0, pady=(10, 10), padx=5, sticky="w")

    refresh_rate_option = ctk.CTkOptionMenu(master=controls_list,
                                            values=["30", "60", "75", "85", "100", "120", "144", "165", "240", "360"],
                                            command=change_refresh_rate)
    refresh_rate_option.set(new_config["mouse"]["pointer-refresh-rate"])
    refresh_rate_option.grid(row=1, column=1, pady=(10, 10), sticky="ew")

    for key, val in new_config["keyboard"].items():
        controls_list.add_item(key, val)

    restore_settings = ctk.CTkButton(master=controlls, text="Restore default",
                                    fg_color="transparent", border_width=2,
                                    command=restore_controls)
    restore_settings.place(relx=0.04, rely=0.96, anchor="sw")

    save = ctk.CTkButton(master=controlls, text="Save", command=save_current_config)
    save.place(relx=0.96, rely=0.96, anchor="se")

    root.mainloop()
