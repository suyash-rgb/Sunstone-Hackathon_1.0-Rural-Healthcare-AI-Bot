# Indic Language Support Strategy: Core LLM & Multimodal Voice Pipeline

This document defines the language capabilities, pipeline architecture, and fallback strategies for the **ArogyaMitra Rural Healthcare AI Bot**. It outlines how the system achieves pan-India language coverage while running under strict hardware constraints (4GB VRAM GPU) by combining local models with targeted cloud API fallbacks.

---

## 🎙️ Multimodal Voice Pipeline Architecture

For voice-based interactions (receiving and responding via audio notes), the system processes requests through a sequential, modular pipeline:

```
[ User Sends Voice Note ]
           │
           ▼
[ Step 1: Audio Language Identification (LID) ]
     (VoxLingua / Fast Audio-LID)
           │
           ├── Detected: language_id = "hi"
           └── Saved to: user_session["lang"]
           │
           ▼
[ Step 2: Speech-to-Text (ASR) via IndicConformer ]
   `IndicConformer(audio, language_id="hi")`
           │
           ▼
     Transcribed Text: "छाती में बहुत तेज दर्द हो रहा है"
           │
           ▼
[ Step 3: Fast Intent Router (~5ms) ]
     (Checks for EMERGENCY_FIRST_AID, LOCATE, etc.)
           │
           ▼
[ Step 4: Translation to English (NMT) ]
   `IndicTrans2-200M` (Hindi ➔ English)
           │
           ▼
[ Step 5: Core RAG + Qwen 3.5 2B Engine ]
   (Zvec Medical Search + Qwen Contextual Generation)
           │
           ▼
     English Response: "1. Sit down immediately. 2. Take aspirin if..."
           │
           ▼
[ Step 6: Translation back to Hindi (NMT) ]
   `IndicTrans2-200M` (English ➔ Hindi)
           │
           ▼
[ Step 7: Voice Synthesis (TTS) Router ]
     (Checks if language has voice synthesis support)
           │
           ├── YES: Generate Audio via Indic Parler-TTS or Piper
           └── NO (Fallback): Respond with Text-Only response
           │
           ▼
[ User Receives Native Text (+ Voice Output if supported) ]
```

---

## 📊 End-to-End Pipeline Support Matrix

The pipeline leverages models primarily developed by **AI4Bharat** for optimized Indic script handling, alongside Qwen 3.5 for reasoning:

| Pipeline Component | Model | Supported Languages |
| :--- | :--- | :--- |
| **1. Audio-LID** | `AI4Bharat/IndicLID` | **22 Scheduled Languages** + English + Romanized scripts |
| **2. ASR (Speech-to-Text)** | `indic-conformer-600m-multilingual` | **22 Scheduled Languages** |
| **3. NMT (Translation)** | `indictrans2-200M` | **22 Scheduled Languages** + English |
| **4. LLM Reasoning** | `Qwen/Qwen3.5-2B` | **200+ Languages** (Includes all 22 Indic) |
| **5. TTS (Text-to-Speech)** | `indic-parler-tts` | **21 Languages** (20 Indic + English) |

---

## 🎛️ App Dropdown Configurations & Voice Support

The frontend dropdown contains **24 languages**. Since the local TTS model (`indic-parler-tts`) supports **21 languages**, we implement a strict distinction between **Voice-Enabled** and **Text-Fallback** languages.

### 1. Full-Pipeline Voice Languages (21 Languages)
These languages have complete end-to-end support (LID ➔ ASR ➔ NMT ➔ LLM ➔ NMT ➔ TTS):
* **Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Konkani, Maithili, Malayalam, Manipuri (Meitei), Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu, and English.**

### 2. Text-Fallback Languages (3 Languages)
If a user selects these languages, they will receive full text translation and reasoning, but the voice note synthesis will be skipped:
* **Bhojpuri (`bho`)**: Supported in LID/ASR/NMT/LLM but lacks natural voice models in standard local TTS.
* **Kashmiri (`ks`)**: Supported in LID/ASR/NMT/LLM but has no voice synthesis model in Indic Parler-TTS.
* **Gondi / Tribal Dialects**: Standardized to text fallback.

---

## 🔌 Extensible Fallback Architecture (Backend)

To ensure the backend doesn't need a rewrite if we add Bhashini APIs, Sarvam APIs, or newer offline TTS engines (like Piper) in the future, we isolate the Voice Synthesis step behind a standard router interface.

```python
# app/services/tts_router.py

class TTSRouterService:
    SUPPORTED_LOCAL_TTS = {
        "en", "hi", "bn", "mr", "te", "ta", "gu", "kn", "ml", "or", 
        "pa", "as", "brx", "doi", "gom", "mai", "mni", "ne", "sa", "sat", "sd", "ur"
    }
    
    def __init__(self):
        # Initialize local models lazily to save startup VRAM
        self.local_tts_model = None

    def should_synthesize_voice(self, lang_code: str) -> bool:
        """
        Determines if voice output is possible. 
        Easily extensible to support external APIs.
        """
        # Check if local engine supports it
        if lang_code in self.SUPPORTED_LOCAL_TTS:
            return True
            
        # Elif condition for Bhashini/Sarvam API integration in the future
        # elif self.has_external_api_tts(lang_code):
        #     return True
            
        return False

    async def generate_speech(self, text: str, lang_code: str) -> str:
        """
        Routes synthesis request to local engine or external API.
        """
        if not self.should_synthesize_voice(lang_code):
            return None # Skip voice note generation, fallback to text-only

        # 1. Local TTS Engine
        if lang_code in self.SUPPORTED_LOCAL_TTS:
            return await self._synthesize_local(text, lang_code)
            
        # 2. Elif condition: Fallback to Bhashini/Sarvam API
        # elif lang_code in EXTERNAL_API_TTS_LANGUAGES:
        #     return await self._synthesize_via_api(text, lang_code)

        return None
```

---

## 📱 Frontend Dropdown Configuration Snippet

For the mobile app frontend (`App/src/constants/translations.js`), this configuration maps language selection options with their voice support flags:

```javascript
export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English", voiceSupported: true },
  { code: "hi", name: "हिन्दी (Hindi)", voiceSupported: true },
  { code: "bn", name: "বাংলা (Bengali)", voiceSupported: true },
  { code: "mr", name: "मराठी (Marathi)", voiceSupported: true },
  { code: "te", name: "తెలుగు (Telugu)", voiceSupported: true },
  { code: "ta", name: "தமிழ் (Tamil)", voiceSupported: true },
  { code: "gu", name: "ગુજરાતી (Gujarati)", voiceSupported: true },
  { code: "kn", name: "ಕನ್ನಡ (Kannada)", voiceSupported: true },
  { code: "ml", name: "മലയാളം (Malayalam)", voiceSupported: true },
  { code: "or", name: "ଓଡ଼ିଆ (Odia)", voiceSupported: true },
  { code: "pa", name: "ਪੰਜਾਬੀ (Punjabi)", voiceSupported: true },
  { code: "as", name: "অসমীয়া (Assamese)", voiceSupported: true },
  { code: "brx", name: "बड़ो (Bodo)", voiceSupported: true },
  { code: "doi", name: "डोगरी (Dogri)", voiceSupported: true },
  { code: "gom", name: "कोंकणी (Konkani)", voiceSupported: true },
  { code: "mai", name: "मैथिली (Maithili)", voiceSupported: true },
  { code: "mni", name: "মৈতৈলোন্ (Manipuri)", voiceSupported: true },
  { code: "ne", name: "नेपाली (Nepali)", voiceSupported: true },
  { code: "sa", name: "संस्कृतम् (Sanskrit)", voiceSupported: true },
  { code: "sat", name: "ᱥᱟᱱᱛᱟᱲᱤ (Santali)", voiceSupported: true },
  { code: "sd", name: "سنڌي (Sindhi)", voiceSupported: true },
  { code: "ur", name: "اردو (Urdu)", voiceSupported: true },
  { code: "bho", name: "भोजपुरी (Bhojpuri)", voiceSupported: false }, // Text fallback
  { code: "ks", name: "کأشُر (Kashmiri)", voiceSupported: false }  // Text fallback
];
```
