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
        model_desc = f" '{model_name}'" if model_name else ""
        print(f"⚠️ Skipping compilation for model{model_desc} - compilation mode is {mode}")
        return model
    
    model_desc = f" '{model_name}'" if model_name else ""
    print(f"🔧 Compiling model{model_desc} with mode: {mode}")
    
    try:
        if mode == CompilationMode.DEFAULT:
            compiled_model = torch.compile(model)
        elif mode == CompilationMode.REDUCE_OVERHEAD:
            compiled_model = torch.compile(model, backend="triton", mode="reduce-overhead")
        elif mode == CompilationMode.MAX_AUTOTUNE:
            compiled_model = torch.compile(model, backend="triton", mode="max-autotune")
        elif mode == CompilationMode.INDUCTOR:
            compiled_model = torch.compile(model, backend="inductor")
        elif mode == CompilationMode.TRITON:
            compiled_model = torch.compile(model, backend="triton")
        elif mode == CompilationMode.AOT_EAGER:
            compiled_model = torch.compile(model, backend="aot_eager")
        else:
            print(f"⚠️ Unsupported compilation mode: {mode}. Using uncompiled model.")
            return model
            
        print(f"✅ Successfully compiled model{model_desc}")
        return compiled_model
    except Exception as e:
        print(f"❌ Error compiling model{model_desc}: {e}")
        print(f"⚠️ Proceeding with uncompiled model")
        return model
