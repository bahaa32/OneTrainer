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
        
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.title("Compilation Settings")
        self.geometry("600x400")
        self.resizable(True, True)
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)

        components.button(self, 1, 0, "OK", command=self.on_window_close)
        self.main_frame(self.frame)

    def main_frame(self, master):
        row = 0
        
        # Compilation Mode
        components.label(master, row, 0, "Compilation Mode",
                         tooltip="Select the compilation mode to use. NONE disables compilation.")
        components.options(master, row, 1, [mode.value for mode in CompilationMode], 
                          self.ui_state, "compilation_mode",
                          command=self.on_mode_change)
        row += 1

        # Model components to compile
        components.label(master, row, 0, "Compile UNet",
                         tooltip="Enable compilation for the UNet model.")
        components.switch(master, row, 1, self.ui_state, "compile_unet")
        row += 1
        
        components.label(master, row, 0, "Compile Text Encoder",
                         tooltip="Enable compilation for the Text Encoder model.")
        components.switch(master, row, 1, self.ui_state, "compile_text_encoder")
        row += 1
        
        components.label(master, row, 0, "Compile VAE",
                         tooltip="Enable compilation for the VAE model.")
        components.switch(master, row, 1, self.ui_state, "compile_vae")
        row += 1

        # Warning about compilation
        components.label(master, row, 0, "Warning:",
                         tooltip="Important information about model compilation")
        components.label(master, row, 1, "Compilation may not work on all models and can increase startup time. Triton compilation requires Triton to be " +
                             "included in the CUDA requirements. Models must be re-compiled each time they are loaded.")
        row += 1
        
    def on_mode_change(self, choice):
        """
        Called when the compilation mode is changed in the UI.
        Updates the train_config with the selected mode.
        """
        # No need for explicit conversion since we're using string values for the enum
        self.train_config.compilation_mode = CompilationMode(choice)

    def on_window_close(self):
        # Update the train_config with values from UI state
        self.train_config.compile_unet = self.ui_state.get("compile_unet", True)
        self.train_config.compile_text_encoder = self.ui_state.get("compile_text_encoder", False)
        self.train_config.compile_vae = self.ui_state.get("compile_vae", False)
        self.destroy()
