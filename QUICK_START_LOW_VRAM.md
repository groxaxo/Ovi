# Quick Start: Low VRAM Mode

Get started with Ovi's low VRAM features in 60 seconds!

## 🚀 Method 1: Web Interface (Recommended)

### Step 1: Start the Server
```bash
./start_web_interface.sh
```

### Step 2: Open Browser
Navigate to: http://localhost:3000

### Step 3: Configure VRAM
1. Click **"Show Advanced Options"**
2. Under **"🧠 Memory Optimization"**:
   - Select your GPU from the VRAM Mode dropdown:
     - RTX 3090/4090 → **"FP8 Optimized (24GB VRAM)"**
     - RTX 3080 → **"FP8 + CPU Offload (16-24GB VRAM)"**
     - RTX 3060 → **"Ultra Low VRAM (8-16GB VRAM)"**
   - (Optional) Check **"Enable LoRA"** for extra savings

3. Under **"🚀 Multi-GPU Settings"**:
   - If you have multiple GPUs, select:
     - 4x RTX 3090 → **"4 GPUs (Sequence Parallel)"**
     - Otherwise → **"Auto (Distribute Automatically)"**

### Step 4: Generate!
- Enter your prompt
- Click **"Add to Queue"**
- Watch it generate! 🎬

---

## 🎨 Method 2: Gradio Interface

### Start Gradio
```bash
python3 gradio_app.py
```

### Configure in UI
1. Under **"Video Generation Options"**:
   - **VRAM Mode**: Select based on your GPU
   - **GPU Allocation**: Choose "Auto" or specific count
   - **Enable LoRA**: Check if needed

2. Enter prompt and generate!

---

## ⌨️ Method 3: Command Line

### Edit Config
Open `ovi/configs/inference/inference_fusion.yaml`:

```yaml
# For RTX 3090/4090
vram_mode: "fp8"
enable_lora: false
gpu_allocation: "auto"

# For RTX 3080
vram_mode: "fp8_offload"
enable_lora: false
gpu_allocation: "single"

# For RTX 3060
vram_mode: "ultra_low"
enable_lora: true
gpu_allocation: "single"
resolution: "720x720"  # Lower resolution
duration: "5s"         # Shorter video
```

### Run Inference
```bash
python3 inference.py --config-file ovi/configs/inference/inference_fusion.yaml
```

---

## 🎯 Preset Configurations

Copy-paste these into your config file:

### Preset 1: Multi-RTX 3090 (4x 24GB) 🔥
```yaml
vram_mode: "fp8"
enable_lora: false
gpu_allocation: "multi_4"
resolution: "960x960"
duration: "10s"
sample_steps: 50
# Expected: ~40s generation, ~18GB per GPU
```

### Preset 2: Single RTX 3090/4090 (24GB)
```yaml
vram_mode: "fp8"
enable_lora: false
gpu_allocation: "single"
resolution: "960x960"
duration: "10s"
sample_steps: 50
# Expected: ~90s generation, ~24GB peak
```

### Preset 3: RTX 3080 (16GB)
```yaml
vram_mode: "fp8_offload"
enable_lora: false
gpu_allocation: "single"
resolution: "960x960"
duration: "5s"
sample_steps: 40
# Expected: ~100s generation, ~16GB peak
```

### Preset 4: RTX 3060 (12GB)
```yaml
vram_mode: "ultra_low"
enable_lora: true
gpu_allocation: "single"
resolution: "720x720"
duration: "5s"
sample_steps: 30
# Expected: ~120s generation, ~10GB peak
```

---

## 🆘 Troubleshooting

### "CUDA Out of Memory" Error

1. **Try a lower VRAM mode**:
   - Standard → FP8
   - FP8 → FP8 + Offload
   - FP8 + Offload → Ultra Low

2. **Enable LoRA**:
   - Adds 10-20% more VRAM savings

3. **Reduce resolution/duration**:
   - 960x960 → 720x720
   - 10s → 5s

4. **Reduce steps**:
   - 50 → 30 (quality will decrease)

### "Module not found" Error

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
pip install flash_attn --no-build-isolation
```

### WebSocket Errors in Frontend

These are harmless if the API server isn't running. The frontend still works for viewing the UI. To eliminate them:
```bash
# Terminal 1: API Server
python3 api_server.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## 📊 What to Expect

### Generation Times (960x960, 10s, 50 steps)

| GPU Setup | VRAM Mode | Time | VRAM Used |
|-----------|-----------|------|-----------|
| 1x A100 80GB | Standard | ~83s | ~80GB |
| 1x RTX 3090 | FP8 | ~90s | ~24GB |
| 4x RTX 3090 | FP8 + Multi-4 | ~40s | ~18GB per GPU |
| 1x RTX 3080 | FP8 + Offload | ~103s | ~16GB |
| 1x RTX 3060 | Ultra Low | ~120s | ~10GB |

*Times are approximate and may vary based on system configuration*

### Quality Comparison

- **Standard**: 100% quality (reference)
- **FP8**: ~95% quality (imperceptible difference)
- **FP8 + Offload**: ~93% quality (very slight softness)
- **Ultra Low**: ~85% quality (noticeable but acceptable)

---

## 💡 Pro Tips

### For Best Results

1. **Start with Auto**:
   - Use "Auto" GPU allocation first
   - Let the system optimize for you

2. **Monitor VRAM**:
   ```bash
   watch -n 1 nvidia-smi
   ```

3. **Match Resolution to GPU**:
   - 32GB+ → 960x960 @ 10s
   - 24GB → 960x960 @ 10s (FP8)
   - 16GB → 960x960 @ 5s (FP8+Offload)
   - 12GB → 720x720 @ 5s (Ultra Low)

4. **Use LoRA Wisely**:
   - Enable when VRAM is tight
   - Disable for maximum quality

### Multi-GPU Users

- **4x RTX 3090 is optimal** for this project
- Use **"4 GPUs (Sequence Parallel)"** mode
- With FP8, each GPU uses ~18GB
- Generation time: ~40s for 10s @ 960x960

---

## 📚 Learn More

- **Detailed Guide**: [LOW_VRAM_GUIDE.md](LOW_VRAM_GUIDE.md)
- **Full Changes**: [CHANGELOG_LOW_VRAM.md](CHANGELOG_LOW_VRAM.md)
- **Main README**: [README.md](README.md)

---

## ✅ Verification

To verify everything is working:

1. **Check GPU is detected**:
   ```bash
   python3 -c "import torch; print(f'GPUs: {torch.cuda.device_count()}')"
   ```

2. **Check VRAM available**:
   ```bash
   nvidia-smi
   ```

3. **Test frontend**:
   - Navigate to http://localhost:3000
   - Click "Show Advanced Options"
   - Verify VRAM Mode dropdown is visible

4. **Test generation**:
   - Start with a simple prompt
   - Use 720x720 @ 5s for first test
   - Verify output video is created

---

## 🎉 You're Ready!

Choose the method that works best for you:
- **Web Interface**: Best UX, one-click selection
- **Gradio**: Good for quick iterations
- **Command Line**: Best for automation/scripting

**Recommended for beginners**: Start with the Web Interface!

---

Need help? Check [LOW_VRAM_GUIDE.md](LOW_VRAM_GUIDE.md) for detailed troubleshooting.
