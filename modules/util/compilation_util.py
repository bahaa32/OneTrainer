import torch
from torch import nn
from modules.util.enum.CompilationMode import CompilationMode


def compile_model(model: nn.Module, mode: CompilationMode, model_name: str = None) -> nn.Module:
    """
    Compiles a PyTorch model using torch.compile with the specified backend.
    
    Args:
        model: The PyTorch model to compile
        mode: The compilation mode to use
        model_name: Optional name for the model for logging purposes
        
    Returns:
        The compiled model
    """
    # Return uncompiled model if mode is None or NONE
    if mode is None or mode == CompilationMode.NONE:
        return model
    
    model_desc = f" '{model_name}'" if model_name else ""
    print(f"Compiling model{model_desc} with mode: {mode.name}")
    
    # Dict to store compilation options based on the mode
    compile_options = {
        CompilationMode.DEFAULT: {
            # Default options - let PyTorch choose the best backend
            "fullgraph": False,  # Partial graph compilation for better compatibility
            "dynamic": True,     # Allow for dynamic input shapes (safer for general use)
        },
        CompilationMode.INDUCTOR: {
            "backend": "inductor",
            "fullgraph": False,  # Partial graph compilation for better compatibility
            "dynamic": True,     # Allow for dynamic input shapes (safer for general use)
            "options": {
                "triton.cudagraphs": False,  # Disable Triton CUDA graphs in inductor mode
                "max_autotune": True,        # Enable autotuning for best kernel selection
                "epilogue_fusion": True,     # Fuse pointwise operations for better performance
            }
        },
        CompilationMode.TRITON: {
            "backend": "inductor",           # Inductor is the recommended backend for Triton
            "fullgraph": False,              # Partial graph compilation for better compatibility
            "dynamic": True,                 # Allow for dynamic input shapes (safer for general use)
            "options": {
                "triton.cudagraphs": True,   # Enable Triton CUDA graphs for better performance
                "max_autotune": True,        # Enable autotuning for best kernel selection
                "epilogue_fusion": True,     # Fuse pointwise operations into kernels
                "shape_padding": True,       # Pad tensor shapes for better hardware utilization
            }
        },
        CompilationMode.AOT_EAGER: {
            "backend": "aot_eager",          # Use AOT eager backend
            "fullgraph": False,              # Partial graph compilation for better compatibility 
            "dynamic": True,                 # Allow for dynamic input shapes (safer for general use)
        }
    }
    
    options = compile_options.get(mode, {})
    
    try:
        compiled_model = torch.compile(model, **options)
        print(f"Successfully compiled model{model_desc}")
        return compiled_model
    except Exception as e:
        print(f"Failed to compile model{model_desc}: {str(e)}")
        print("Falling back to uncompiled model")
        return model
