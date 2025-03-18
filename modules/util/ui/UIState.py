import contextlib
import tkinter as tk
from collections.abc import Callable
from enum import Enum
from typing import Any

from modules.util.config.BaseConfig import BaseConfig


class UIState:
    __vars: dict[str, Any]
    __var_traces: dict[str, dict[int, Callable[[], None]]]
    __latest_var_trace_id: int

    def __init__(self, master, obj):
        self.master = master
        self.obj = obj
        self.__vars = self.__create_vars(obj)
        self.__var_traces = {name: {} for name in self.__vars}
        self.__latest_var_trace_id = 0

    def update(self, obj):
        self.obj = obj
        self.__set_vars(obj)

    def get_var(self, name):
        split_name = name.split('.')

        if len(split_name) == 1:
            return self.__vars[split_name[0]]
        else:
            state = self
            for name_part in split_name:
                state = state.get_var(name_part)
            return state

    def add_var_trace(self, name, command: Callable[[], None]) -> int:
        self.__latest_var_trace_id += 1
        self.__var_traces[name][self.__latest_var_trace_id] = command
        return self.__latest_var_trace_id

    def remove_var_trace(self, name, trace_id):
        self.__var_traces[name].pop(trace_id)

    def __call_var_traces(self, name):
        for trace in self.__var_traces[name].values():
            trace()

    def __set_str_var(self, obj, is_dict, name, var, nullable):
        if is_dict:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    obj[name] = None
                else:
                    obj[name] = string_var
                self.__call_var_traces(name)
        else:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    setattr(obj, name, None)
                else:
                    setattr(obj, name, string_var)
                self.__call_var_traces(name)

        return update

    def __set_enum_var(self, obj, is_dict, name, var, var_type, nullable=False):
        if is_dict:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    obj[name] = None
                else:
                    try:
                        # First try to get the enum value directly from the string
                        obj[name] = var_type[string_var]
                    except (KeyError, ValueError):
                        try:
                            # If that fails, try to handle cases like "CompilationMode.NONE"
                            if "." in string_var:
                                enum_name = string_var.split(".")[-1]
                                obj[name] = var_type[enum_name]
                            else:
                                # If all else fails, print error and do nothing
                                print(f"Could not set {name} as {string_var}")
                        except (KeyError, ValueError):
                            print(f"Could not set {name} as {string_var}")
                self.__call_var_traces(name)
        else:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    setattr(obj, name, None)
                else:
                    try:
                        # First try to get the enum value directly from the string
                        setattr(obj, name, var_type[string_var])
                    except (KeyError, ValueError):
                        try:
                            # If that fails, try to handle cases like "CompilationMode.NONE"
                            if "." in string_var:
                                enum_name = string_var.split(".")[-1]
                                setattr(obj, name, var_type[enum_name])
                            else:
                                # If all else fails, print error and do nothing
                                print(f"Could not set {name} as {string_var}")
                        except (KeyError, ValueError):
                            print(f"Could not set {name} as {string_var}")
                self.__call_var_traces(name)

        return update

    def __set_bool_var(self, obj, is_dict, name, var):
        if is_dict:
            def update(_0, _1, _2):
                obj[name] = var.get()
                self.__call_var_traces(name)
        else:
            def update(_0, _1, _2):
                setattr(obj, name, var.get())
                self.__call_var_traces(name)

        return update

    def __set_int_var(self, obj, is_dict, name, var, nullable):
        if is_dict:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    obj[name] = None
                elif string_var == "inf":
                    obj[name] = int("inf")
                elif string_var == "-inf":
                    obj[name] = int("-inf")
                else:
                    with contextlib.suppress(ValueError):
                        obj[name] = int(string_var)
                self.__call_var_traces(name)
        else:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    setattr(obj, name, None)
                elif string_var == "inf":
                    setattr(obj, name, int("inf"))
                elif string_var == "-inf":
                    setattr(obj, name, int("-inf"))
                else:
                    with contextlib.suppress(ValueError):
                        setattr(obj, name, int(string_var))
                self.__call_var_traces(name)

        return update

    def __set_float_var(self, obj, is_dict, name, var, nullable):
        if is_dict:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    obj[name] = None
                elif string_var == "inf":
                    obj[name] = float("inf")
                elif string_var == "-inf":
                    obj[name] = float("-inf")
                else:
                    with contextlib.suppress(ValueError):
                        obj[name] = float(string_var)
                self.__call_var_traces(name)
        else:
            def update(_0, _1, _2):
                string_var = var.get()
                if (string_var == "" or string_var == "None") and nullable:
                    setattr(obj, name, None)
                elif string_var == "inf":
                    setattr(obj, name, float("inf"))
                elif string_var == "-inf":
                    setattr(obj, name, float("-inf"))
                else:
                    with contextlib.suppress(ValueError):
                        setattr(obj, name, float(string_var))
                self.__call_var_traces(name)

        return update

    def __create_vars(self, obj):
        new_vars = {}

        is_dict = isinstance(obj, dict)
        is_config = isinstance(obj, BaseConfig)

        if is_config:
            for name, var_type in obj.types.items():
                obj_var = getattr(obj, name)
                if issubclass(var_type, BaseConfig):
                    var = UIState(self.master, obj_var)
                    new_vars[name] = var
                elif var_type is str:
                    var = tk.StringVar(master=self.master)
                    var.set("" if obj_var is None else obj_var)
                    var.trace_add("write", self.__set_str_var(obj, is_dict, name, var, obj.nullables[name]))
                    new_vars[name] = var
                elif issubclass(var_type, Enum):
                    var = tk.StringVar(master=self.master)
                    var.set("" if obj_var is None else str(obj_var))
                    var.trace_add("write", self.__set_enum_var(obj, is_dict, name, var, var_type, obj.nullables[name]))
                    new_vars[name] = var
                elif var_type is bool:
                    var = tk.BooleanVar(master=self.master)
                    var.set(obj_var or False)
                    var.trace_add("write", self.__set_bool_var(obj, is_dict, name, var))
                    new_vars[name] = var
                elif var_type is int:
                    var = tk.StringVar(master=self.master)
                    var.set("" if obj_var is None else str(obj_var))
                    var.trace_add("write", self.__set_int_var(obj, is_dict, name, var, obj.nullables[name]))
                    new_vars[name] = var
                elif var_type is float:
                    var = tk.StringVar(master=self.master)
                    var.set("" if obj_var is None else str(obj_var))
                    var.trace_add("write", self.__set_float_var(obj, is_dict, name, var, obj.nullables[name]))
                    new_vars[name] = var
        else:
            iterable = obj.items() if is_dict else vars(obj).items()

            for name, obj_var in iterable:
                if isinstance(obj_var, str):
                    var = tk.StringVar(master=self.master)
                    var.set(obj_var)
                    var.trace_add("write", self.__set_str_var(obj, is_dict, name, var, False))
                    new_vars[name] = var
                elif isinstance(obj_var, Enum):
                    var = tk.StringVar(master=self.master)
                    var.set(str(obj_var))
                    var.trace_add("write", self.__set_enum_var(obj, is_dict, name, var, type(obj_var), False))
                    new_vars[name] = var
                elif isinstance(obj_var, bool):
                    var = tk.BooleanVar(master=self.master)
                    var.set(obj_var)
                    var.trace_add("write", self.__set_bool_var(obj, is_dict, name, var))
                    new_vars[name] = var
                elif isinstance(obj_var, int):
                    var = tk.StringVar(master=self.master)
                    var.set(str(obj_var))
                    var.trace_add("write", self.__set_int_var(obj, is_dict, name, var, False))
                    new_vars[name] = var
                elif isinstance(obj_var, float):
                    var = tk.StringVar(master=self.master)
                    var.set(str(obj_var))
                    var.trace_add("write", self.__set_float_var(obj, is_dict, name, var, False))
                    new_vars[name] = var

        return new_vars

    def __set_vars(self, obj):
        is_dict = isinstance(obj, dict)
        is_config = isinstance(obj, BaseConfig)
        iterable = obj.items() if is_dict else vars(obj).items()

        if is_config:
            for name, var_type in obj.types.items():
                obj_var = getattr(obj, name)
                if issubclass(var_type, BaseConfig):
                    var = self.__vars[name]
                    var.__set_vars(obj_var)
                elif var_type is str:
                    var = self.__vars[name]
                    var.set("" if obj_var is None else obj_var)
                elif issubclass(var_type, Enum):
                    var = self.__vars[name]
                    var.set("" if obj_var is None else str(obj_var))
                elif var_type is bool:
                    var = self.__vars[name]
                    var.set(obj_var or False)
                elif var_type in (int, float):
                    var = self.__vars[name]
                    var.set("" if obj_var is None else str(obj_var))
        else:
            for name, obj_var in iterable:
                if isinstance(obj_var, str):
                    var = self.__vars[name]
                    var.set(obj_var)
                elif isinstance(obj_var, Enum):
                    var = self.__vars[name]
                    var.set(str(obj_var))
                elif isinstance(obj_var, bool):
                    var = self.__vars[name]
                    var.set(obj_var)
                elif isinstance(obj_var, int | float):
                    var = self.__vars[name]
                    var.set(str(obj_var))

    def has_var(self, name):
        """Check if a variable exists in the UI state"""
        try:
            self.get_var(name)
            return True
        except KeyError:
            return False
            
    def add_var(self, name, default_value):
        """Add a new variable to the UI state"""
        if name in self.__vars:
            # Variable already exists, just update its value
            var = self.__vars[name]
            if isinstance(var, tk.StringVar):
                var.set(str(default_value))
            elif isinstance(var, tk.BooleanVar):
                var.set(bool(default_value))
            elif isinstance(var, tk.IntVar):
                var.set(int(default_value))
            elif isinstance(var, tk.DoubleVar):
                var.set(float(default_value))
        else:
            # Create a new variable
            if isinstance(default_value, bool):
                self.__vars[name] = tk.BooleanVar(value=default_value)
            elif isinstance(default_value, int):
                self.__vars[name] = tk.IntVar(value=default_value)
            elif isinstance(default_value, float):
                self.__vars[name] = tk.DoubleVar(value=default_value)
            else:
                self.__vars[name] = tk.StringVar(value=str(default_value))
            
            # Initialize the var traces
            self.__var_traces[name] = {}

    def get(self, name, default=None):
        """Get the value of a variable, returning default if it doesn't exist"""
        try:
            var = self.get_var(name)
            return var.get()
        except KeyError:
            return default
