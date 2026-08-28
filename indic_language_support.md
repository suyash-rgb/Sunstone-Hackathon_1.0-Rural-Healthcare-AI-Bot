# Indic Language Support Strategy: Qwen vs. Bhashini / Sarvam

This document summarizes the proficiency of the **Qwen** model across various Indian (Indic) languages based on your research, and outlines when we can rely on Qwen natively versus when we must integrate specialized APIs like **Bhashini** or **Sarvam**.

---

## 📋 Summary of Qwen's Indic Language Capabilities

Qwen exhibits strong performance on major languages with massive web corpora (the "Core Indian Languages"), but its accuracy degrades rapidly (falling to 60-70%) on minor regional languages and localized dialects, where it often hallucinates or falls back to generic Hindi/Devanagari.

### 1. Natively Supported by Qwen (90%+ Accuracy)
For these languages, we can rely **entirely on Qwen** for translation, summarization, and direct conversation generation.

* **Hindi & Urdu:** Extremely strong support; Urdu uses its native script with high precision, while Hindi supports most core medical contexts.
* **Tamil, Telugu, Malayalam, Kannada:** High precision and native script support.
* **Bengali, Gujarati, Odia:** Strong native support with accurate script output.
* **Punjabi, Assamese:** Medium/High support, though Assamese is sometimes confused with Bengali in output.

---

### 2. Requires Bhashini / Sarvam API Integration (Fallback Needed)
For these minor, regional, or highly-localized languages, Qwen's native training data is too sparse. It lacks granular phonetic and grammatical understanding, often returning generic Devanagari/Hindi. We must use **Bhashini** or **Sarvam** to translate them to/from Hindi or English before passing them to Qwen.

* **High-Divergence Script Languages:**
  * **Kashmiri** (Diverges significantly from core Urdu/Hindi; Qwen returns generic mix)
  * **Manipuri / Meitei** (Sparse native training data in Qwen)
* **Devanagari-based Regional Dialects/Languages:**
  * **Dogri, Bhojpuri, Gondi, Bihari, Sindhi**
  * *Why:* Although they use the Devanagari script, their grammar and vocabulary are unique. Qwen gets confused by the script overlap and outputs standard Hindi instead of the actual dialect.
* **Ultra-Local/Himalayan Languages:**
  * **Sikkimese, Khalsi** (Virtually unsupported in Qwen)

---

## 🗺️ Indic Language Decision Matrix

| Language | Script | Strategy | API / Tool |
| :--- | :--- | :--- | :--- |
| **Hindi** | Devanagari | **Direct Qwen** | None (Native) |
| **Urdu** | Urdu | **Direct Qwen** | None (Native) |
| **Tamil** | Tamil | **Direct Qwen** | None (Native) |
| **Telugu** | Telugu | **Direct Qwen** | None (Native) |
| **Malayalam** | Malayalam | **Direct Qwen** | None (Native) |
| **Kannada** | Kannada | **Direct Qwen** | None (Native) |
| **Bengali** | Bangla | **Direct Qwen** | None (Native) |
| **Gujarati** | Gujarati | **Direct Qwen** | None (Native) |
| **Odia** | Odia | **Direct Qwen** (Medium) | None (Native) |
| **Assamese** | Assamese | **Direct Qwen** (Medium) | Fallback to Bhashini if confused |
| **Punjabi** | Devanagari / Gurmukhi | **Direct Qwen** (Medium) | None (Native) |
| **Bhojpuri** | Devanagari | **API Translation** | Bhashini / Sarvam API |
| **Dogri** | Devanagari | **API Translation** | Bhashini / Sarvam API |
| **Sindhi** | Devanagari / Arabic | **API Translation** | Bhashini / Sarvam API |
| **Gondi** | Devanagari | **API Translation** | Bhashini / Sarvam API |
| **Kashmiri** | Kashmiri (Perso-Arabic) | **API Translation** | Bhashini / Sarvam API |
| **Manipuri** | Manipuri (Meitei Mayek) | **API Translation** | Bhashini / Sarvam API |
| **Sikkimese** | Sikkim | **API Translation** | Bhashini API |
| **Khalsi** | Khalsi | **API Translation** | Bhashini API |
| **Hinglish** | Latin (English) | **Direct Qwen** | None (Native) |

---

## 🔄 App Simulation Translation Flow for Outliers

To support lower-priority/outlier languages at a **95%+ accuracy level**, the FastAPI backend should execute a **trans-pipelining flow**:

```
                       ┌─────────────────────────┐
                       │   User Regional Text    │
                       │ (e.g. Kashmiri/Bhojpuri)│
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │      Bhashini API       │
                       │ (Translate to English)  │
                       └────────────┬────────────┘
                                    │ English Text
                                    ▼
                       ┌─────────────────────────┐
                       │     Qwen 2.5 LLM        │
                       │    (Process Logic)      │
                       └────────────┬────────────┘
                                    │ English Response
                                    ▼
                       ┌─────────────────────────┐
                       │      Bhashini API       │
                       │ (Translate to Regional) │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  User Receives Native   │
                       │   Response + Speech     │
                       └─────────────────────────┘
```
