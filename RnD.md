I decided on a hybrid approach for the VisionService due to the low VRAM hardware constraint:

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

# Nearby Hospitals (CHCs, PHCs etc) finding functionality via External APIs

Call it from the **Server-Side (FastAPI)**, executed **asynchronously in parallel** with your voice pipeline.

While calling an API directly from React Native often feels like it would save a network hop, in AarogyaMitra's architecture, server-side execution is actually faster, more reliable, and completely eliminates perceptual latency.

---

### Why Server-Side Wins for Low Latency

When the user taps the emergency button and speaks, React Native sends both the **audio snippet** and the user's **GPS coordinates** `(lat, lon)` in a single POST request or WebSocket frame to FastAPI.

Because STT and translation take ~400ms to 800ms, FastAPI can fetch hospitals **in the background concurrently**:

```
Client sends: [Audio Data + Lat/Lon]
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[ Task 1: Audio Pipeline ]   [ Task 2: Hospital Fetch ]
IndicConformer STT (~400ms)  Ola Maps / Cache (~60ms - 150ms)
IndicTrans2 NMT    (~200ms)               │
       │                                  │
       ▼                                  ▼
[ Both ready! Hospital data is already cached in memory ]
                     │
                     ▼
[ LLM & TTS: "I found City Hospital 1.2km away. First aid steps: ..." ]

```

* **Perceived Hospital Latency = 0 ms:** The hospital query finishes *long before* STT and translation are done. You pay zero extra waiting time.
* **Server-to-Server Network Speed:** Cloud servers communicate with Ola Maps and OSM backbones over low-latency datacenter pipes, which is significantly faster and more stable than a mobile device on fluctuating 4G/5G in India.

---

### Comparison: Client-Side vs. Server-Side

| Factor | Client-Side (React Native) | Server-Side (FastAPI) |
| --- | --- | --- |
| **Perceived Latency** | Sequential or separate stream; mobile radio latency | **0 ms added latency** (runs parallel to STT) |
| **API Key Security** | ❌ **High Risk:** Ola Maps key is compiled into the APK and easily extracted via reverse engineering | 🟢 **100% Secure:** S

By doing this on the server, React Native only needs to manage **one clean request/response cycle**, the API keys remain protected, and the emergency data arrives fully synchronized with the voice instructions.

# Olamaps Krutrim Cloud API - Quick Reference

### 1. Difference: `nearbysearch` vs. `nearbysearch/advanced`

Both endpoints take the same core parameters (`location`, `radius`, `types`), but they differ in payload depth and network efficiency:

* **Standard `nearbysearch` (Lightweight):**
* Returns basic spatial identifiers: `name`, `place_id`, `distance_meters`, `geometry` (coordinates), and `structured_formatting`.
* Excludes contact info, desk numbers, or opening hours. To obtain a facility's phone number, you would need to make a second HTTP call to `/places/v1/details` using the `place_id`.


* **`nearbysearch/advanced` (Enriched):**
* Returns the same spatial fields plus enriched business metadata: `formatted_phone_number`, `international_phone_number`, `opening_hours`, and user ratings in the initial response.
* Eliminates the need for a secondary `/places/v1/details` call when contact numbers are available in Ola's database.



---

### 2. Understanding The Healthcare Hierarchy

In India, public healthcare follows a defined referral hierarchy:

```
[ Tier 1: Sub-Centre / Ayushman Arogya Mandir ] ──► Village level (3,000–5,000 pop.)
                     │
[ Tier 2: Primary Health Centre (PHC) ]          ──► Gram Panchayat (20,000–30,000 pop.)
                     │                               Basic OPD, 4–6 beds, 1 MO doctor
[ Tier 3: Community Health Centre (CHC) ]        ──► Block / Tehsil level (80,000–120,000 pop.)
                     │                               30 beds, basic surgery, emergency
[ Tier 4: Sub-District / Civil Hospital ]        ──► Sub-division headquarters
                     │
[ Tier 5: District Hospital (e.g., Bhoj Hospital) ]──► District Headquarters (Apex facility)
                                                     100–500 beds, 24/7 trauma, ICU, 
                                                     blood bank, and specialist surgeons

```

District Bhoj Hospital is the **District Hospital (जिला चिकित्सालय)** for Dhar. For critical trauma or severe emergencies, it provides higher capabilities than a PHC or CHC.

---

### 3. How to Specifically Surface Rural CHCs & PHCs

In the previous test, CHCs and PHCs were omitted for two structural reasons:

1. **Category Tagging:** Small rural health clinics and PHCs are frequently indexed under **`types=clinic`**, while only large facilities receive the `types=hospital` classification.
2. **Geographical Distribution:** CHCs and PHCs are spaced across rural blocks and sub-districts (e.g., Tirla, Nalchha). Searching within a 5 km radius around Dhar municipal center targets urban facilities. Expanding the query to **10 km – 15 km** (`radius=15000`) captures surrounding block centers.

To ensure both large district facilities and rural centers are retrieved:

* Query both `types=hospital` and `types=clinic` in parallel, or rely on the combined Overpass OSM query (`amenity=hospital` + `amenity=clinic` + `healthcare=centre`).

---

### 4. Background Government-First Prioritization Logic

To rank government facilities at the top of the React Native carousel while retaining proximity-based ordering within each tier, implement a **weighted classification pipeline** in FastAPI.

```
[ Incoming Facilities List from Ola / OSM ]
                    │
                    ▼
       [ Government Classifier ]
   (Keyword regex + OSM Operator Tags)
                    │
                    ▼
          [ Dual-Key Sort ]
  Key: (0 if Govt else 1, distance_meters)
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
 [ Tier 1: Govt Facilities ]   [ Tier 2: Private Facilities ]
 (Sorted by nearest first)     (Sorted by nearest first)

```

# OpenStreetMap - Overpass QL (Query Langugage)

OpenStreetMap does not use standard relational tables (like PostgreSQL/MySQL). Instead, the entire planet's map is stored as a massive spatial graph made of only three primitive elements:

1. **`node`**: A single point on earth with a specific `lat` and `lon` (e.g., a tree, an ATM, or a small clinic pin).
2. **`way`**: An ordered sequence of nodes forming a line or polygon (e.g., a road, a river, or a hospital building footprint).
3. **`relation`**: A group of nodes and ways combined together (e.g., a large hospital campus with multiple buildings and entry gates).

Because buildings are often stored as polygon boundaries (`ways`) rather than single points (`nodes`), standard SQL queries would be overly complex. Overpass QL was designed to filter this graph spatially in a single pass.

---

### Anatomy of an Overpass QL Query

Here is the breakdown of how the query works piece by piece:

```text
// 1. Settings Header: Return JSON and halt if it takes more than 10s
[out:json][timeout:10];

// 2. Union Block: Parentheses act like an "OR" / union of multiple searches
(
  // Find all point markers tagged amenity=hospital within 5000m of (lat, lon)
  node["amenity"="hospital"](around:5000, 22.6057, 75.3201);

  // Find all hospital building outlines within 5000m
  way["amenity"="hospital"](around:5000, 22.6057, 75.3201);

  // Find all clinics and PHCs
  node["amenity"="clinic"](around:5000, 22.6057, 75.3201);
  way["healthcare"="centre"](around:5000, 22.6057, 75.3201);
);

// 3. Output Directive: Print results, and calculate the center point for building outlines
out center;

```

---

### The 4 Symbols You Need to Know

| Syntax | What It Means | Example |
| --- | --- | --- |
| `[...]` | **Execution settings or tag filters** | `[out:json]` (return JSON), `["amenity"="hospital"]` (filter tag) |
| `(...)` | **Union (OR)** or **Spatial bounds** | `(around:5000, lat, lon)` (search radius), `( node...; way...; );` (combine results) |
| `;` | **End of statement** | Every command in Overpass QL **must** end with a semicolon `;` |
| `out center;` | **Output modifier** | Computes the center `lat`/`lon` for building shapes so your app doesn't have to parse raw polygon boundary nodes |


