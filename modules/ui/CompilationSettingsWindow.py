from tkinter import TclError

from modules.util.config.TrainConfig import TrainConfig
from modules.util.enum.CompilationMode import CompilationMode
from modules.util.ui import components

import customtkinter as ctk


class CompilationSettingsWindow(ctk.CTkToplevel):
    def __init__(
            self,
            parent,
            train_config: TrainConfig,
            ui_state,
            *args, **kwargs,
    ):
        ctk.CTkToplevel.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.train_config = train_config
        self.ui_state = ui_state
        
        # Initialize the compilation UI state variables if they don't exist
        if not ui_state.has_var("compilation_mode"):
            ui_state.add_var("compilation_mode", "NONE")
        if not ui_state.has_var("compile_unet"):
            ui_state.add_var("compile_unet", True)
        if not ui_state.has_var("compile_text_encoder"):
            ui_state.add_var("compile_text_encoder", False)
        if not ui_state.has_var("compile_vae"):
            ui_state.add_var("compile_vae", False)
        
        self.protocol("WM_DELETE_WINDOW", self.on_ok_clicked)

        self.title("Compilation Settings")
        self.geometry("600x400")
        self.resizable(True, True)
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.__create_content()

    def __create_content(self):
        self.content_frame = ctk.CTkFrame(master=self, corner_radius=5)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)

        row = 0
        
        # Compilation mode explanation
        explanation_text = (
            "Model compilation can significantly speed up training, but may take longer to initialize.\n"
            "• NONE: No compilation (regular PyTorch)\n"
            "• DEFAULT: Best compatibility, moderate speedup\n"
            "• REDUCE_OVERHEAD: Better performance, less compatibility\n"
            "• MAX_AUTOTUNE: Best performance, longest startup, least compatibility"
        )
        label = ctk.CTkLabel(
            master=self.content_frame,
            text=explanation_text,
            justify="left",
            wraplength=400
        )
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w", columnspan=2)
        row += 1
        
        # Compilation mode dropdown
        components.label(self.content_frame, row, 0, "Compilation Mode",
                         tooltip="Select the compilation mode to use for torch.compile")
        self.mode_option = ctk.CTkOptionMenu(
            master=self.content_frame,
            values=[mode.value for mode in CompilationMode],
            command=self.on_mode_change
        )
        # Set the initial value
        current_mode = str(self.train_config.compilation_mode)
        self.mode_option.set(current_mode)
        self.mode_option.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        row += 1
        
        # Quick setup buttons
        components.label(self.content_frame, row, 0, "Quick Setup",
                        tooltip="Apply predefined compilation settings")
        buttons_frame = ctk.CTkFrame(master=self.content_frame)
        buttons_frame.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        # Enable DEFAULT compilation button
        default_button = ctk.CTkButton(
            master=buttons_frame,
            text="Enable DEFAULT",
            command=lambda: self.quick_setup(CompilationMode.DEFAULT)
        )
        default_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        # Enable REDUCE_OVERHEAD compilation button
        reduce_button = ctk.CTkButton(
            master=buttons_frame,
            text="Enable REDUCE_OVERHEAD",
            command=lambda: self.quick_setup(CompilationMode.REDUCE_OVERHEAD)
        )
        reduce_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        # Disable compilation button
        disable_button = ctk.CTkButton(
            master=buttons_frame,
            text="Disable Compilation",
            command=lambda: self.quick_setup(CompilationMode.NONE)
        )
        disable_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        row += 1
        
        # Model components to compile
        components.label(self.content_frame, row, 0, "Compile UNet",
                         tooltip="Enable compilation for the UNet model.")
        components.switch(self.content_frame, row, 1, self.ui_state, "compile_unet")
        row += 1
        
        components.label(self.content_frame, row, 0, "Compile Text Encoder",
                         tooltip="Enable compilation for the Text Encoder model.")
        components.switch(self.content_frame, row, 1, self.ui_state, "compile_text_encoder")
        row += 1
        
        components.label(self.content_frame, row, 0, "Compile VAE",
                         tooltip="Enable compilation for the VAE model.")
        components.switch(self.content_frame, row, 1, self.ui_state, "compile_vae")
        row += 1
        
        # Warning about compilation
        components.label(self.content_frame, row, 0, "Warning:",
                         tooltip="Important information about model compilation")
        components.label(self.content_frame, row, 1, "Compilation may not work on all models and can increase startup time. Triton compilation requires Triton to be " +
                             "included in the CUDA requirements. Models must be re-compiled each time they are loaded.")
        row += 1
        
        self.ok_button = ctk.CTkButton(
            master=self,
            text="OK",
            command=self.on_ok_clicked
        )
        self.ok_button.pack(side="bottom", padx=5, pady=5)

    def on_mode_change(self, choice):
        """
        Called when the compilation mode is changed in the UI.
        Updates the train_config with the selected mode.
        """
        # No need for explicit conversion since we're using string values for the enum
        self.train_config.compilation_mode = CompilationMode(choice)

    def quick_setup(self, mode):
        """Apply quick setup for the selected compilation mode"""
        # Update dropdown
        self.mode_option.set(mode.value)
        
        # Set the train config
        self.train_config.compilation_mode = mode
        
        # Close the window
        self.on_ok_clicked()

    def on_ok_clicked(self):
        # Update the train_config with values from UI state
        self.train_config.compile_unet = self.ui_state.get("compile_unet", True)
        self.train_config.compile_text_encoder = self.ui_state.get("compile_text_encoder", False)
        self.train_config.compile_vae = self.ui_state.get("compile_vae", False)
        self.destroy()
