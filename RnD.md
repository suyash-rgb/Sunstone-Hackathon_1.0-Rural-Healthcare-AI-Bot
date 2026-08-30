we decided on a hybrid approach due to your 4GB VRAM hardware constraint:

EasyOCR (Local CPU): Used for reading text off of documents, prescriptions, and handwritten notes.

Gemini Flash (Cloud via google-generativeai): Used when the user uploads an actual photograph (like a picture of a skin rash, an injury, or an X-ray).

# What is NMT (Neural Machine Translation)?
NMT stands for Neural Machine Translation. It is the modern deep-learning approach to translating text between languages using neural network architectures (specifically Transformers).

Here is how it differs from older translation methods:

Old Way (Statistical / Rule-Based Translation): Translated text phrase-by-phrase or word-by-word. This frequently resulted in broken grammar, literal mistakes, and awkward phrasing—especially in Indian languages where sentence structure is Subject-Object-Verb (SOV) compared to English's Subject-Verb-Object (SVO).

NMT Way (Neural Networks): An NMT model (like IndicTrans2 or NLLB-200) reads the entire input sentence, converts its meaning into an abstract mathematical representation (vector space), and then generates a completely natural sentence in the target language while maintaining context, grammar, and idioms.

# RAM Usage Estimation 

### Option 1: "All-In PyTorch" (Unoptimized Baseline)

Loading all models into memory using standard PyTorch (`float32` or `float16`) causes memory usage to quickly multiply. Every model loads its full weight tensors, PyTorch CUDA/CPU execution context, and activation buffers simultaneously.

| Pipeline Step | Model / Framework | PyTorch Precision | Concurrent RAM / VRAM |
| --- | --- | --- | --- |
| **1. Audio-LID** | `IndicLID` (PyTorch) | FP32 | **~50 MB** |
| **2. STT (Speech-to-Text)** | `IndicConformer-600M` (PyTorch) | FP16 / FP32 | **~1.8 GB** |
| **3. Translation (NMT)** | `IndicTrans2-200M` (Indic $\rightarrow$ EN) | FP32 | **~800 MB** |
| **4. Translation (NMT)** | `IndicTrans2-200M` (EN $\rightarrow$ Indic) | FP32 | **~800 MB** |
| **5. Vector Embeddings** | `BGE-small-en-v1.5` (PyTorch) | FP32 | **~300 MB** |
| **6. Core LLM** | `Qwen 3.5 2B` (PyTorch) | FP16 | **~4.5 GB** |
| **7. TTS (Text-to-Speech)** | `Indic Parler-TTS` (PyTorch) | FP16 | **~2.2 GB** |
| **8. App Overhead** | FastAPI + PyTorch Context buffers | — | **~1.0 GB** |
| **TOTAL PEAK RAM** | — | — | **~11.45 GB – 13.0 GB** |

*Running the pure PyTorch stack requires at least 16 GB of system RAM or a dedicated 16 GB GPU to avoid out-of-memory (OOM) crashes.*

---

### Option 2: The Optimized Runtimes Stack (`CTranslate2` + `ONNX` + `FastEmbed`)

Switching away from native PyTorch to C++ optimized inference engines (`CTranslate2`, `ONNX Runtime`) and 4-bit / 8-bit quantization drastically shrinks the memory footprint.

| Pipeline Step | Model | Optimized Framework & Precision | Concurrent RAM / VRAM |
| --- | --- | --- | --- |
| **1. Audio-LID** | `IndicLID` | Lightweight Python | **~30 MB** |
| **2. STT (Speech-to-Text)** | `Faster-Whisper` / `IndicConformer` | `CTranslate2` (INT8) | **~500 MB** |
| **3. Translation (NMT)** | `IndicTrans2-200M` (Both directions) | `CTranslate2` (INT8 shared) | **~300 MB** |
| **4. Vector Embeddings** | `BGE-small-en-v1.5` | `FastEmbed` (ONNX) | **~130 MB** |
| **5. Core LLM** | `Qwen 3.5 2B` | `ONNX Runtime` / `GGUF` (INT4) | **~1.6 GB** |
| **6. TTS (Text-to-Speech)** | `Piper TTS` *(or Indic Parler-TTS INT4)* | `ONNX` CPU engine | **~100 MB** *(or ~500 MB)* |
| **7. App Overhead** | FastAPI + Uvicorn | Native Python | **~300 MB** |
| **TOTAL PEAK RAM** | — | — | **~2.96 GB – 3.46 GB** |

---

### Why the Optimized Runtimes Save ~75% RAM

1. **Model Weights Compression (Quantization):** Converting PyTorch 16-bit floats to 4-bit or 8-bit integers (`INT4`/`INT8`) reduces model weight size by 4x without noticeable loss in translation or transcription accuracy.
2. **Zero PyTorch Context Overhead:** CTranslate2 and ONNX Runtime run directly on compiled C++ binaries. They do not load heavy PyTorch autograd engine graphs or CUDA memory pools into RAM.
3. **Shared Runtimes:** In `CTranslate2`, the single C++ engine handles both `Indic $\rightarrow$ EN` and `EN $\rightarrow$ Indic` translation models in a shared memory pool rather than instantiating two distinct PyTorch model objects.

---

### Sequential Execution Strategy (Zero Extra Hardware Required)

Because an audio request flows sequentially (STT finishes *before* Translation starts, and Translation finishes *before* LLM generation starts), you can run this entire pipeline smoothly on a basic **4 GB RAM server or CPU** by letting each optimized C++ runtime execute sequentially.

When 10 people are using your app during testing, **the AI model weights are loaded into RAM only ONCE.** You do not load 10 copies of Qwen or 10 copies of IndicTrans2.

The total RAM usage is split into two categories:

1. **Static Base RAM:** The fixed memory used to hold the model weights in RAM/VRAM at server startup (never changes).
2. **Dynamic RAM (Per-User Overhead):** The extra temporary memory allocated per active user request (KV Cache for LLM text context, STT audio buffers, and request context).

---

### Peak RAM Breakdown for 10 Concurrent Users

#### Scenario A: The Optimized Stack (`CTranslate2` + `ONNX INT4` + `FastEmbed`)

* **Static Base Model Weights (Loaded Once):** **~3.0 GB**
* Qwen 3.5 2B (INT4): ~1.6 GB
* Faster-Whisper / IndicConformer (INT8): ~500 MB
* IndicTrans2 (INT8 shared): ~300 MB
* FastEmbed (ONNX) + Zvec: ~130 MB
* Lightweight TTS Engine + FastAPI base: ~400 MB


* **Dynamic Overhead per Active User:** **~120 MB – 150 MB**
* Audio buffer per voice recording: ~30 MB
* LLM Key-Value (KV) Cache per chat context (1K–2K tokens): ~80 MB – 100 MB
* FastAPI request context: ~10 MB


* **Total Peak RAM Calculation:**

$$\text{Total RAM} = \text{Static Base (3.0 GB)} + (10 \times 150\text{ MB})$$


$$\text{Total RAM} = 3.0\text{ GB} + 1.5\text{ GB} = \mathbf{4.5\text{ GB}}$$



---

#### Scenario B: The Unoptimized Pure PyTorch Stack (FP16)

* **Static Base Model Weights (Loaded Once):** **~11.0 GB**
* **Dynamic Overhead per Active User (PyTorch activations & unquantized KV Cache):** **~350 MB**
* **Total Peak RAM Calculation:**

$$\text{Total RAM} = 11.0\text{ GB} + (10 \times 350\text{ MB}) = \mathbf{14.5\text{ GB}}$$



---

### Real-World Testing Behavior: Staggered vs. Exact-Simultaneous Hits

* **Real-World Staggered Usage (10 Test Users):**
Even with 10 people actively testing the app, they won't all hit the "Send" button at the exact same millisecond. While User 1 is reading the output, User 2 is recording a voice note.
* *Actual Peak RAM:* **~3.2 GB – 3.8 GB** on the optimized stack.


* **Synthetic Stress Test (10 Simultaneous Requests):**
If 10 people click "Send" at the exact same second, your backend holds 10 active KV cache slots and processes queue batches simultaneously.
* *Actual Peak RAM:* **~4.5 GB** on the optimized stack.
