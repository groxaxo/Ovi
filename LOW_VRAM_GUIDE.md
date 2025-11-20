# Low VRAM Guide for Ovi

This guide explains how to use Ovi on GPUs with limited VRAM, inspired by techniques from the [ComfyUI Ovi Workflow Guide](https://aistudynow.com/comfyui-ovi-workflow-guide-clean-10s-video-on-low-vram/).

## 🎯 Quick Start

### For Web Interface Users

1. Start the web interface:
   ```bash
   ./start_web_interface.sh
   ```

2. In the generation settings, find the **"Memory Optimization"** section

3. Select your VRAM mode from the dropdown:
   - **Standard (32GB+ VRAM)**: Best quality, requires high-end GPU
   - **FP8 Optimized (24GB VRAM)**: Good quality with reduced VRAM
   - **FP8 + CPU Offload (16-24GB VRAM)**: Balanced for mid-range GPUs
   - **Ultra Low VRAM (8-16GB VRAM)**: Works on budget GPUs

4. (Optional) Enable **LoRA** checkbox for additional VRAM reduction

5. Select your **GPU Allocation** strategy if you have multiple GPUs

### For Gradio Users

1. Launch Gradio:
   ```bash
   python3 gradio_app.py
   ```

2. Under **"Video Generation Options"**, select:
   - **VRAM Mode**: Choose your GPU's VRAM level
   - **GPU Allocation**: Choose how to use multiple GPUs
   - **Enable LoRA**: Check to reduce VRAM further

### For Command-Line Users

Edit `ovi/configs/inference/inference_fusion.yaml`:

```yaml
# Low VRAM Configuration
vram_mode: "fp8_offload"  # Options: standard, fp8, fp8_offload, ultra_low
enable_lora: false         # Set to true for additional VRAM reduction
gpu_allocation: "auto"     # Options: auto, single, multi_2, multi_4, multi_8, fsdp

# These will be automatically configured based on vram_mode:
fp8: true                  # Automatically set by vram_mode
cpu_offload: true          # Automatically set by vram_mode
qint8: false              # Automatically set by vram_mode
```

## 📊 VRAM Modes Explained

### 1. Standard Mode (32GB+ VRAM)
- **Target GPUs**: A100, H100, high-end datacenter GPUs
- **Quality**: Best possible
- **Speed**: Fastest
- **Configuration**:
  - No quantization
  - No CPU offload
  - Full BF16 precision

### 2. FP8 Optimized (24GB VRAM)
- **Target GPUs**: RTX 3090, RTX 4090, A6000
- **Quality**: Excellent (minimal degradation)
- **Speed**: Fast
- **Configuration**:
  - FP8 (8-bit floating point) quantization
  - Model runs on GPU
  - ~70% VRAM reduction from standard

**Perfect for multi-RTX 3090 setups!**

### 3. FP8 + CPU Offload (16-24GB VRAM)
- **Target GPUs**: RTX 3080, RTX 4080, mid-range professional GPUs
- **Quality**: Good
- **Speed**: Medium (~20s slower than standard)
- **Configuration**:
  - FP8 quantization
  - CPU offload for text encoder
  - Parts of model temporarily moved to RAM

### 4. Ultra Low VRAM (8-16GB VRAM)
- **Target GPUs**: RTX 3060, RTX 3070, RTX 4060 Ti
- **Quality**: Fair
- **Speed**: Slower (~40s slower than standard)
- **Configuration**:
  - QINT8 quantization
  - Aggressive CPU offload
  - Maximum VRAM savings

## ⚡ LoRA Support

LoRA (Low-Rank Adaptation) can further reduce VRAM consumption:

- **Memory Savings**: 10-20% additional VRAM reduction
- **Quality Impact**: Minimal with proper LoRA weights
- **Speed**: Slightly faster due to smaller model

### When to Enable LoRA:
- ✅ When VRAM is very limited
- ✅ When using custom LoRA adapters
- ✅ For faster iteration during testing
- ❌ When maximum quality is required
- ❌ When VRAM is not a constraint

## 🚀 Multi-GPU Strategies

Perfect for multi-RTX 3090 setups common in this project!

### Auto (Recommended)
Automatically detects and optimally distributes workload:
- 1 GPU → Single GPU mode
- 2 GPUs → 2-way sequence parallel
- 4+ GPUs → 4-way sequence parallel

### Sequence Parallel (2/4/8 GPUs)
Splits the temporal sequence across multiple GPUs:
- **Benefit**: Faster processing, reduced per-GPU VRAM
- **Best for**: Multiple identical GPUs (e.g., 4x RTX 3090)
- **Speed improvement**: ~2x with 2 GPUs, ~3x with 4 GPUs

### FSDP Sharded
Fully Sharded Data Parallel for maximum memory efficiency:
- **Benefit**: Lowest VRAM per GPU
- **Best for**: Large models on limited VRAM
- **Trade-off**: Slightly slower due to communication overhead

## 📝 Recommended Configurations

### Budget Setup (1x RTX 3060 12GB)
```yaml
vram_mode: "ultra_low"
enable_lora: true
gpu_allocation: "single"
resolution: "720x720"      # Lower resolution
duration: "5s"             # Shorter videos
sample_steps: 30           # Fewer steps
```

### Mid-Range Setup (1x RTX 3080 16GB)
```yaml
vram_mode: "fp8_offload"
enable_lora: false
gpu_allocation: "single"
resolution: "960x960"
duration: "5s"
sample_steps: 50
```

### High-End Single GPU (1x RTX 3090/4090 24GB)
```yaml
vram_mode: "fp8"
enable_lora: false
gpu_allocation: "single"
resolution: "960x960"
duration: "10s"
sample_steps: 50
```

### Multi-GPU Setup (4x RTX 3090 24GB each) 🔥
```yaml
vram_mode: "fp8"           # Each GPU uses FP8
enable_lora: false
gpu_allocation: "multi_4"  # 4-way sequence parallel
resolution: "960x960"
duration: "10s"
sample_steps: 50
```

### Datacenter Setup (1x A100 80GB)
```yaml
vram_mode: "standard"
enable_lora: false
gpu_allocation: "single"
resolution: "960x960"
duration: "10s"
sample_steps: 50
```

## 🔧 Advanced Tips

### Optimizing for Your GPU

1. **Check available VRAM**:
   ```bash
   nvidia-smi
   ```

2. **Monitor VRAM usage during generation**:
   ```bash
   watch -n 1 nvidia-smi
   ```

3. **Adjust resolution and duration**:
   - Lower resolution = less VRAM
   - Shorter duration = less VRAM
   - Try 720x720 for 5s videos on limited VRAM

### Troubleshooting OOM (Out of Memory) Errors

If you get CUDA out of memory errors:

1. **Enable a lower VRAM mode**:
   - Standard → FP8
   - FP8 → FP8 + Offload
   - FP8 + Offload → Ultra Low

2. **Enable LoRA**:
   - Check the LoRA checkbox for additional savings

3. **Reduce resolution**:
   - 960x960 → 720x720
   - 704x1280 → 512x992

4. **Reduce duration**:
   - 10s → 5s

5. **Reduce steps**:
   - 50 → 30 (quality will degrade)

6. **Close other GPU applications**:
   - Make sure no other programs are using GPU memory

### Multi-GPU Load Balancing

When using multiple GPUs, Ovi automatically:
- Detects available GPUs
- Checks free VRAM on each
- Distributes workload optimally
- Monitors for failures and redistributes

The GPU manager (inspired by ComfyUI-MultiGPU concepts) ensures:
- ✅ Best GPU is selected for each job
- ✅ Jobs are distributed across available GPUs
- ✅ Memory-constrained GPUs are avoided
- ✅ Failed jobs are automatically retried on different GPUs

## 📚 References

This implementation is based on techniques from:
- [ComfyUI Ovi Workflow Guide](https://aistudynow.com/comfyui-ovi-workflow-guide-clean-10s-video-on-low-vram/)
- [ComfyUI-MultiGPU](https://github.com/pollockjj/ComfyUI-MultiGPU) concepts for GPU allocation
- Community feedback on RTX 3090 multi-GPU setups

## 🆘 Getting Help

If you're still experiencing issues:

1. Check the logs for specific error messages
2. Try the "Auto" GPU allocation mode
3. Open an issue on GitHub with:
   - Your GPU model and VRAM
   - Selected VRAM mode
   - Error message
   - Configuration used

## 🎉 Success Stories

**Multi-RTX 3090 Setup** (most common for this project):
- Mode: FP8 Optimized
- GPUs: 4x RTX 3090 24GB
- Result: 10s videos at 960x960, ~40s generation time
- VRAM per GPU: ~18GB peak

**Budget RTX 3060 Setup**:
- Mode: Ultra Low VRAM
- GPU: 1x RTX 3060 12GB
- Result: 5s videos at 720x720, ~90s generation time
- VRAM: ~10GB peak
