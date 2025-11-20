<div align="center">
<h1> Ovi: Twin Backbone Cross-Modal Fusion for Audio-Video Generation </h1>

<a href="https://arxiv.org/abs/2510.01284"><img src="https://img.shields.io/badge/arXiv%20paper-2510.01284-b31b1b.svg"></a>
<a href="https://aaxwaz.github.io/Ovi/"><img src="https://img.shields.io/badge/Project_page-More_visualizations-green"></a>
<a href="https://huggingface.co/chetwinlow1/Ovi"><img src="https://img.shields.io/static/v1?label=%F0%9F%A4%97%20Hugging%20Face&message=Model&color=orange"></a>

[Chetwin Low](https://www.linkedin.com/in/chetwin-low-061975193/)<sup> * 1 </sup>, [Weimin Wang](https://www.linkedin.com/in/weimin-wang-will/)<sup> * &dagger; 1 </sup>, [Calder Katyal](https://www.linkedin.com/in/calder-katyal-a8a9b3225/)<sup> 2 </sup><br>
<sup> * </sup>Equal contribution, <sup> &dagger; </sup>Project Lead<br>
<sup> 1 </sup>Character AI, <sup> 2 </sup>Yale University
</div>

---

## 🎥 Video Demo

### 🆕 Ovi 1.1 10-Second Demo
<div align="center">
  <video src="https://github.com/user-attachments/assets/191f51fb-ef5a-4197-b26f-a5369dc2c007"
         width="70%" controls playsinline preload="metadata"></video>
  <p><em>Ovi 1.1 – 10-second temporally consistent video generation (960 × 960 resolution)</em></p>
</div>

### 🎬 Original 5-Second Demo
<div align="center">
  <video src="https://github.com/user-attachments/assets/351bd707-8637-4412-ab53-5e85935309e3" width="70%" poster=""> </video>
</div>

---

# 🆕 Ovi 1.1 Update (10 November 2025)
- **Key Feature:** Enables *temporal-consistent 10-second video generation* at **960 × 960 resolution**  
- **Training Improvements:**  
  - Trained natively on 960×960 resolution videos  
  - Dataset includes **100% more videos** for greater diversity
  - 
- **Prompt Format Update:**  
  - Audio descriptions should now be written as  
    ```
    Audio: ...
    ```  
    instead of using  
    ```
    <AUDCAP> ... <ENDAUDCAP>
    ```

## 🌟 Key Features
Ovi is a veo-3-like, **video + audio generation model** that simultaneously generates both video and audio content from text or text + image inputs.
- **🎬 Video+Audio Generation**: Generate synchronized video and audio content simultaneously
  - **🎵 High-Quality Audio Branch**: We designed and pretrained our 5B audio branch from scratch using our high quality in-house audio datasets
- **📝 Flexible Input**: Supports text-only or text+image conditioning
- **⏱️ 10-second (or 5-second) Videos**: Generates 10-second or 5-second videos at 24 FPS, resolution of 960x960p, at various aspect ratios (9:16, 16:9, 1:1, etc)
- **🔧 ComfyUI Integration**: ComfyUI support is now available via [ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper), related [PR](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1343#issuecomment-3382969479).
- **🎬 Create videos now on wavespeed.ai**: https://wavespeed.ai/models/character-ai/ovi/image-to-video & https://wavespeed.ai/models/character-ai/ovi/text-to-video
- **🎬 Create videos now on HuggingFace**: https://huggingface.co/spaces/akhaliq/Ovi

### 🆕 Advanced Features (New!)
- **🌐 Modern Web Interface**: Beautiful Open WebUI-inspired interface with real-time queue management
- **⚡ Optimized Multi-GPU**: Enhanced sequence parallel and FSDP sharded inference for Ampere GPUs (RTX 3090)
- **🔄 Unlimited Queue System**: Progressive video generation with automated queue processing
- **🚀 LoRA Lightning**: Fast inference with LoRA adapters for custom styles
- **📊 Real-time Progress**: Live WebSocket updates for generation progress
- **🎯 Prompt Templates**: Pre-made templates for quick video creation

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for detailed documentation.

### 🎯 10-second examples

<div align="center"><table><tr>
<td width="20%">
<video src="https://github.com/user-attachments/assets/c7e75ef8-adf9-4612-a279-56e4cf7ce146" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/025f5936-883e-4851-bf35-1a809769ba97" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/9e5bf0df-74d6-4e04-a7d0-e5b64616afa9" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/499cefde-c5f8-4afc-b77a-6cd9293b8ac6" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/73390370-afa7-4604-97b6-80995b615d43" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/e11c6f2d-6098-41bb-9bca-a99796a58424" width="100%" controls playsinline preload="metadata"></video>
</td>
</tr></table>
<p>Click the ⛶ button on any video to view full screen.</p>
</div>

### 🎯 5-second examples

<div align="center"><table><tr>
<td width="20%">
<video src="https://github.com/user-attachments/assets/c6b35565-df00-4494-b38a-7dcae90f63e5" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/2ce6ff72-eadd-4cf4-b343-b465f0624571" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/7c1dbbea-dfb7-44d7-a4a1-d70a2e00f51a" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/4e41d1b3-7d39-49a8-ab71-e910088f29ee" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/4ad3ad70-1fea-4a2d-9201-808f4746c55e" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/60792c08-12de-49c3-860f-12ac94730940" width="100%" controls playsinline preload="metadata"></video>
</td>
<td width="20%">
<video src="https://github.com/user-attachments/assets/0f3a318b-ac74-43c4-81a5-503f06c65e99" width="100%" controls playsinline preload="metadata"></video>
</td>
</tr></table>
<p>Click the ⛶ button on any video to view full screen.</p>
</div>


---
## 📋 Todo List

- [x] Release research paper and [website for demos](https://aaxwaz.github.io/Ovi)
- [x] Checkpoint of 11B model
- [x] Inference Codes
  - [x] Text or Text+Image as input
  - [x] Gradio application code
  - [x] Multi-GPU inference with or without the support of sequence parallel
  - [x] fp8 weights and improved memory efficiency (credits to [@rkfg](https://github.com/rkfg))
  - [x] qint8 quantization thanks to [@gluttony-10](https://github.com/character-ai/Ovi/commits?author=gluttony-10)
  - [x] **Improve efficiency of Sequence Parallel implementation** ✨
  - [x] **Implement Sharded inference with FSDP** ✨
  - [x] **Modern Web Interface (Open WebUI-inspired)** ✨
  - [x] **Queue System with Unlimited Length** ✨
  - [x] **LoRA Lightning Support for Fast Inference** ✨
  - [x] **Optimizations for Ampere GPUs (RTX 3090)** ✨
- [x] Video creation example prompts and format
- [x] Finetune model with higher resolution data, and RL for performance improvement. 
- [x] Longer video generation (10s)
- [ ] Reference voice condition
- [ ] Distilled model for faster inference
- [ ] Training scripts

---

## 🎨 An Easy Way to Create

We provide example prompts to help you get started with Ovi:
- **Text-to-Audio-Video (T2AV) 10s**: [`example_prompts/gpt_examples_t2v.csv`](example_prompts/gpt_examples_10s_t2v.csv)
- **Image-to-Audio-Video (I2AV) 10s**: [`example_prompts/gpt_examples_i2v.csv`](example_prompts/gpt_examples_10s_i2v.csv)
- **Text-to-Audio-Video (T2AV)**: [`example_prompts/gpt_examples_t2v.csv`](example_prompts/gpt_examples_t2v.csv)
- **Image-to-Audio-Video (I2AV)**: [`example_prompts/gpt_examples_i2v.csv`](example_prompts/gpt_examples_i2v.csv)

### 📝 Prompt Format

Our prompts use special tags to control speech and audio:
- **Speech**: `<S>Your speech content here<E>` - Text enclosed in these tags will be converted to speech
- **Audio Description**: `Audio: YOUR AUDIO DESCRIPTION` - Describes the audio or sound effects present in the video **at the end of prompt!**

---


## 📦 Installation

### Step-by-Step Installation

```bash
# Clone the repository
git clone https://github.com/character-ai/Ovi.git

cd Ovi

# Create and activate virtual environment
virtualenv ovi-env
source ovi-env/bin/activate

# Install PyTorch first
pip install torch==2.6.0 torchvision torchaudio

# Install other dependencies
pip install -r requirements.txt

# Install Flash Attention
pip install flash_attn --no-build-isolation
```

### Alternative Flash Attention Installation (Optional)
If the above flash_attn installation fails, you can try the Flash Attention 3 method:
```bash
git clone https://github.com/Dao-AILab/flash-attention.git
cd flash-attention/hopper
python setup.py install
cd ../..  # Return to Ovi directory
```

## Download Weights
To download our main Ovi checkpoint, as well as T5 and vae decoder from Wan, and audio vae from MMAudio

```
# Default is downloaded to ./ckpts, and the inference yaml is set to ./ckpts so no change required
# Default installs all versions of Ovi models, 720x720_5s, 960x960_5s, 960x960_10s
python3 download_weights.py
# For qint8 also ues python3 download_weights.py

OR

# Optional can specific --output-dir to download to a specific directory
# but if a custom directory is used, the inference yaml has to be updated with the custom directory
python3 download_weights.py --output-dir <custom_dir>

# Optional can specific --models to download selective versions of Ovi instead of all of them
# but if a custom directory is used, the inference yaml has to be updated with the custom directory
python3 download_weights.py --models 960x960_10s # ["720x720_5s", "960x960_5s", "960x960_10s"]

# Additionally, if you only have ~ 24Gb of GPU vram, please download the fp8 quantized version of the model, and follow the following instructions in sections below to run with fp8
wget -O "./ckpts/Ovi/model_fp8_e4m3fn.safetensors" "https://huggingface.co/rkfg/Ovi-fp8_quantized/resolve/main/model_fp8_e4m3fn.safetensors"
```

## 🚀 Run Examples

### ⚙️ Configure Ovi

Ovi's behavior and output can be customized by modifying [ovi/configs/inference/inference_fusion.yaml](ovi/configs/inference/inference_fusion.yaml) configuration file.
The following parameters control generation quality, video resolution, and how text, image, and audio inputs are balanced:

```yaml
# Output and Model Configuration
model_name: "960x960_10s" # ["720x720_5s", "960x960_5s", "960x960_10s"]
output_dir: "/path/to/save/your/videos"                    # Directory to save generated videos
ckpt_dir: "/path/to/your/ckpts/dir"                        # Path to model checkpoints

# Generation Quality Settings
sample_steps: 50                             # Number of denoising steps. Lower (30-40) = faster generation
solver_name: "unipc"                     # Sampling algorithm for denoising process
shift: 5.0                               # Timestep shift factor for sampling scheduler
seed: 100                                # Random seed for reproducible results

# Guidance Strength Control
audio_guidance_scale: 3.0                # Strength of audio conditioning. Higher = better audio-text sync
video_guidance_scale: 4.0                # Strength of video conditioning. Higher = better video-text adherence
slg_layer: 11                            # Layer for applying SLG (Skip Layer Guidance) technique - feel free to try different layers!

# Multi-GPU and Performance
sp_size: 1                               # Sequence parallelism size. Set equal to number of GPUs used
cpu_offload: False                       # CPU offload, will largely reduce peak GPU VRAM but increase end to end runtime by ~20 seconds
fp8: False                               # load fp8 version of model, will have quality degradation and will not have speed up in inference time as it still uses bf16 matmuls, but can be paired with cpu_offload=True, to run model with 24Gb of GPU vram

# Input Configuration
text_prompt: "/path/to/csv" or "your prompt here"          # Text prompt OR path to CSV/TSV file with prompts
mode: ['i2v', 't2v', 't2i2v']                          # Generate t2v, i2v or t2i2v; if t2i2v, it will use flux krea to generate starting image and then will follow with i2v
video_frame_height_width: [704, 1280]    # Video dimensions [height, width] for T2V mode only
each_example_n_times: 1                  # Number of times to generate each prompt

# Quality Control (Negative Prompts)
video_negative_prompt: "jitter, bad hands, blur, distortion"  # Artifacts to avoid in video
audio_negative_prompt: "robotic, muffled, echo, distorted"    # Artifacts to avoid in audio
```

### 🎬 Running Inference

#### **Single GPU** (Simple Setup)
```bash
python3 inference.py --config-file ovi/configs/inference/inference_fusion.yaml
```
*Use this for single GPU setups. The `text_prompt` can be a single string or path to a CSV file.*

#### **Multi-GPU** (Parallel Processing)
```bash
torchrun --nnodes 1 --nproc_per_node 8 inference.py --config-file ovi/configs/inference/inference_fusion.yaml
```
*Use this to run samples in parallel across multiple GPUs for faster processing.*

### Memory & Performance Requirements

Below are approximate GPU memory requirements for different configurations. We now support multiple **Low VRAM modes** to make Ovi accessible on a wider range of GPUs.

#### Low VRAM Optimization Modes

| VRAM Mode | VRAM Required | Speed | Quality | Best For |
|-----------|---------------|-------|---------|----------|
| **Standard** | 32GB+ | Fastest | Best | High-end GPUs (A100, H100) |
| **FP8 Optimized** | ~24GB | Fast | Excellent | RTX 3090, RTX 4090 |
| **FP8 + CPU Offload** | 16-24GB | Medium | Good | Mid-range GPUs |
| **Ultra Low VRAM** | 8-16GB | Slower | Fair | Budget GPUs |

💡 **New Features:**
- 🧠 **One-Click VRAM Selection**: Choose your VRAM mode from a dropdown in the web interface or Gradio
- ⚡ **LoRA Support**: Enable LoRA for additional VRAM reduction with minimal quality impact
- 🚀 **Smart GPU Allocation**: Automatically distribute workloads across multiple GPUs (perfect for multi-3090 setups)

#### Sequence Parallel Performance

All End-to-End time calculated based on a 121 frame, 720x720 video, using 50 denoising steps.

| Sequence Parallel Size | FlashAttention-3 Enabled | CPU Offload | With Image Gen Model | Peak VRAM Required | End-to-End Time |
|-------------------------|---------------------------|-------------|-----------------------|---------------|-----------------|
| 1                       | Yes                        | No          | No                    | ~80 GB        | ~83s         |
| 1                       | No                        | No          | No                    | ~80 GB        | ~96s         |
| 1                       | Yes                        | Yes          | No                    | ~80 GB        | ~105s         |
| 1                       | No                        | Yes          | No                    | ~32 GB        | ~118s         |
| **1**                       | **Yes**                        | **Yes**          | **Yes**                    | **~32 GB**        | **~140s**         |
| 4                       | Yes                        | No          | No                    | ~80 GB        | ~55s         |
| 8                       | Yes                        | No          | No                    | ~80 GB        | ~40s         |

#### Multi-GPU Allocation Strategies

When you have multiple GPUs (especially multi-RTX 3090 setups), Ovi can automatically distribute the workload:

- **Auto**: Automatically detects and uses available GPUs
- **Sequence Parallel (2/4/8 GPUs)**: Splits the sequence across multiple GPUs for faster processing
- **FSDP Sharded**: Memory-efficient model sharding for maximum VRAM savings
### Gradio
We provide a simple script to run our model in a gradio UI with **built-in Low VRAM mode selection**. It uses the `ckpt_dir` in `ovi/configs/inference/inference_fusion.yaml` to initialize the model

```bash
# Basic usage - Low VRAM options available in the UI
python3 gradio_app.py

OR

# To enable cpu offload to save GPU VRAM, will slow down end to end inference by ~20 seconds
python3 gradio_app.py --cpu_offload

OR

# To enable an additional image generation model to generate first frames for I2V, cpu_offload is automatically enabled if image generation model is enabled
python3 gradio_app.py --use_image_gen

OR

# To run model with 24Gb GPU vram. No need to download additional models.
python3 gradio_app.py --cpu_offload --qint8

# To run model with 24Gb GPU vram
python3 gradio_app.py --cpu_offload --fp8

```

**✨ New in Gradio UI:**
- 🧠 **VRAM Mode Dropdown**: Select from Standard, FP8, FP8+Offload, or Ultra Low VRAM modes
- ⚡ **LoRA Toggle**: Enable LoRA for additional VRAM savings
- 🚀 **GPU Allocation**: Choose single GPU, multi-GPU sequence parallel, or FSDP sharding

### 🌐 Modern Web Interface (New!)

We now provide a beautiful, modern web interface inspired by Open WebUI with real-time queue management:

```bash
# Easy one-command startup
./start_web_interface.sh
```

This will start both the API server and frontend. Visit `http://localhost:3000` to use the interface.

**Features:**
- 🎨 Beautiful dark-themed UI with smooth animations
- 📱 Responsive design for mobile and desktop
- 🔄 Real-time queue management with WebSocket updates
- 📝 Prompt templates for quick start
- ⚙️ Full control over all generation parameters
- 📊 Live progress tracking

**Manual Startup:**

```bash
# Terminal 1: Start API server
pip install -r requirements_api.txt
python3 api_server.py

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

**Advanced Multi-GPU with Web Interface:**

The web interface automatically uses your configured multi-GPU setup. Edit `ovi/configs/inference/inference_fusion.yaml`:

```yaml
# Enable FSDP for memory-efficient multi-GPU
use_fsdp: true
fsdp_sharding_strategy: "FULL_SHARD"  # or "SHARD_GRAD_OP"

# Enable optimized communications
use_optimized_comms: true

# Sequence parallel (if not using FSDP)
sp_size: 4  # Number of GPUs
```

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for detailed configuration.

---

## 🙏 Acknowledgements

We would like to thank the following projects:

- **[Wan2.2](https://github.com/Wan-Video/Wan2.2)**: Our video branch is initialized from the Wan2.2 repository
- **[MMAudio](https://github.com/hkchengrex/MMAudio)**: We reused MMAudio's audio vae. 

---

## 🤝 Collaboration

We welcome all types of collaboration! Whether you have feedback, want to contribute, or have any questions, please feel free to reach out.

**Contact**: [Weimin Wang](https://linkedin.com/in/weimin-wang-will) for any issues or feedback.


## ⭐ Citation

If Ovi is helpful, please help to ⭐ the repo.

If you find this project useful for your research, please consider citing our [paper](https://arxiv.org/abs/2510.01284).


### BibTeX
```bibtex
@misc{low2025ovitwinbackbonecrossmodal,
      title={Ovi: Twin Backbone Cross-Modal Fusion for Audio-Video Generation}, 
      author={Chetwin Low and Weimin Wang and Calder Katyal},
      year={2025},
      eprint={2510.01284},
      archivePrefix={arXiv},
      primaryClass={cs.MM},
      url={https://arxiv.org/abs/2510.01284}, 
}
```
