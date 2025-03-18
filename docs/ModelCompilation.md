# Model Compilation

Model compilation is a technique for accelerating PyTorch models during training by using `torch.compile`. This feature in OneTrainer can significantly improve training speed, especially for longer training runs.

## Introduction

PyTorch's `torch.compile` feature, introduced in PyTorch 2.0, optimizes PyTorch code by analyzing it and generating more efficient, specialized implementations of the operations for the specific hardware being used. In OneTrainer, model compilation can be applied to UNet, text encoder, and VAE components.

Compilation is done at runtime, which means the first few training iterations after loading the model will be slower as the compilation takes place. However, after this initial overhead, subsequent iterations will run significantly faster.

## Supported Backends

OneTrainer provides support for several compilation backends:

1. **DEFAULT**: Uses PyTorch's default backend (typically 'inductor')
2. **INDUCTOR**: Explicit use of PyTorch's inductor backend
3. **TRITON**: Uses Triton-accelerated operations for further speedups on NVIDIA GPUs
4. **AOT_EAGER**: Ahead-of-time compilation with eager mode execution

The TRITON backend requires the Triton package, which is included in the CUDA requirements.

### Compilation Backends Comparison

| Backend | Description | Performance | Overhead | Memory Usage | Best Use Case |
|---------|-------------|-------------|----------|--------------|---------------|
| **NONE** | No compilation | Baseline | None | Baseline | Short training runs or debugging |
| **DEFAULT** | PyTorch's default compiler backend | Good | Medium | Medium | General use, default choice |
| **INDUCTOR** | PyTorch's graph-based compiler | Better | Medium-High | Medium-High | Long training runs on modern hardware |
| **TRITON** | GPU kernel fusion with Triton | Best | High | High | Long training on NVIDIA GPUs |
| **AOT_EAGER** | Ahead-of-time with eager execution | Good | Low | Low | When you need more stability |

### Implementation Details

OneTrainer configures each backend with the following settings:

1. **DEFAULT**: Uses PyTorch's default backend selection with dynamic shapes enabled
   - Allows the PyTorch compiler to choose the most appropriate backend
   - Safest option for most models

2. **INDUCTOR**: Explicitly uses PyTorch's Inductor backend
   - Enables autotuning for optimal kernel selection
   - Enables epilogue fusion for better performance
   - Disables CUDA graphs to avoid potential issues

3. **TRITON**: Uses Inductor backend with Triton acceleration
   - Enables CUDA graphs for reduced Python overhead
   - Enables shape padding for better GPU utilization
   - Enables autotuning and epilogue fusion for maximum performance
   - Best for modern NVIDIA GPUs with longer training runs

4. **AOT_EAGER**: Uses ahead-of-time compilation with eager mode
   - More stable option with less aggressive optimizations
   - Supports dynamic input shapes for flexibility
   - Lower memory requirements than other modes

All backends use partial graph compilation (`fullgraph=False`) for better compatibility with complex models, and support dynamic shapes for flexible input sizes during training.

### About AOT_EAGER Mode

AOT_EAGER (Ahead-of-Time Eager) mode is a hybrid approach that:

- Pre-compiles operations before they are needed ("ahead of time")
- Executes using PyTorch's standard eager execution mode
- Uses PyTorch primitives rather than custom kernels
- Provides more deterministic performance with less compilation overhead
- Is a good middle ground when TRITON or INDUCTOR cause issues

AOT_EAGER mode is part of the PyTorch ecosystem rather than using external compiler technologies like Triton. It's a good fallback option if you encounter issues with the more aggressive optimization backends.

## When to Use

Model compilation is most beneficial in the following scenarios:

- Long training runs where the initial compilation overhead is offset by faster iterations
- Training on modern NVIDIA GPUs that support Triton
- When working with larger models or batch sizes

It may not be beneficial for very short training runs where the compilation overhead can outweigh the speedup from compilation.

## Configuration

To enable model compilation:

1. Open the model compilation settings from the Advanced Options section in the Training tab
2. Select your desired compilation mode (NONE disables compilation)
3. Choose which model components to compile:
   - UNet (on by default, provides the most significant speedup)
   - Text Encoder (optional)
   - VAE (optional, less impact on training speed)

For most use cases, compiling just the UNet with the TRITON backend yields the best results.

## Cloud Training Compatibility

Model compilation is fully compatible with cloud training. When you push your changes to a git repository and run training in the cloud, the compilation settings will be applied there as well.

Models must be re-compiled each time they are loaded, so the compilation overhead will occur at the start of each training session, whether local or in the cloud.

## Notes and Limitations

- The first few iterations will be slower as the compilation process takes place
- Compilation requires additional memory during the compilation phase
- Certain very complex model architectures might not be fully compatible with compilation
- For optimal results with the TRITON backend, ensure your GPU drivers are up to date

By default, only the UNet is compiled as it provides the most significant performance improvement while minimizing compilation overhead.

## Troubleshooting

If you encounter issues with model compilation, try these solutions:

### Compilation Fails or Errors

- **Switch to a different backend**: If one backend fails, try another. AOT_EAGER is usually the most reliable.
- **Disable compilation for problematic components**: If compilation fails for specific components (e.g., text encoder), disable compilation for those components only.
- **Update PyTorch and CUDA**: Make sure you're using compatible versions of PyTorch 2.0+ and the latest CUDA drivers.
- **Check VRAM availability**: Compilation can temporarily require more memory. If you're close to VRAM limits, try reducing batch size or disabling compilation.

### Performance Issues

- **First iterations are slow**: This is normal and expected. The compilation process adds overhead to the first few iterations. Subsequent iterations will be faster.
- **Expected speedup not achieved**: Try different backends. The optimal backend depends on your specific hardware and model.
- **Memory errors during compilation**: Try using AOT_EAGER which typically has lower memory requirements, or disable compilation for some components.

### General Tips

- Benchmark your specific setup with different compilation options to find the optimal configuration
- For short training runs (< 1000 steps), compilation overhead might outweigh the benefits
- The more complex and larger your model, the more likely you'll see significant benefits from compilation
- Use `NONE` mode when debugging issues to rule out compilation as a source of problems

If problems persist after trying these solutions, compilation may not be compatible with your specific model architecture or training setup. In this case, reverting to standard training (NONE mode) is recommended.
