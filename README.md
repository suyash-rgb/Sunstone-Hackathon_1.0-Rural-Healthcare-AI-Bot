<div align="center">

# ➕ **आरोग्यमित्र** | AarogyaMitra | **Aarogya** मित्र
### *AI Rural Healthcare Chatbot • ग्रामीण स्वास्थ्य और चिकित्सा सहायक चैटबॉट* 

[![India DPI](https://img.shields.io/badge/%F0%9F%87%AE%F0%9F%87%B3_India-Healthcare_DPI-orange?style=for-the-badge)](https://abdm.gov.in/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005587?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-000000?style=for-the-badge&logo=expo&logoColor=white)](https://expo.dev/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*Bridging the healthcare divide in rural and semi-urban India through AI-driven voice guidance, smart triage, government-first healthcare discovery, and zero-cost telemedicine integration.*

---

</div>

## 🌟 Motivation & Vision

In rural India, reaching a medical professional is often a race against distance, language barriers, and critical infrastructure shortfalls. While state-of-the-art diagnostic AI models exist, they remain inaccessible to non-literate or low-bandwidth populations who need simple, empathetic, and immediate guidance in their native dialect.

**AarogyaMitra (आरोग्यमित्र)** was conceived with a clear vision: **Democratize healthcare access for every Indian citizen by turning everyday mobile devices into intelligent, multi-lingual medical companions.** By combining Indic voice interfaces, automated clinical triage, government-first healthcare facility discovery, and deep-linked telemedicine gateways, AarogyaMitra acts as a trusted digital paramedic for rural families and ASHA workers alike.

---

## 📖 Case Story

According to the *Health Dynamics of India* report released by the **Ministry of Health and Family Welfare (MoHFW)**, there is an **80% shortfall in Community Health Centres (CHCs)** across rural India.

In **Tier-2, Tier-3, and remote rural villages**, access to quality healthcare is severely constrained by:
* 👨‍⚕️ **Severe Doctor-to-Patient Ratios:** Overburdened district civil hospitals and Primary Health Centres (PHCs).
* ⏳ **Critical Waiting Delays:** Hours spent travelling over unpaved routes for basic consultation or initial triage.
* 🗣️ **Language & Literacy Barriers:** Complex health forms and English-centric health apps that alienate rural users.

Meanwhile, mobile connectivity has transformed rural communication. As of **2023**, India boasts:
* 📱 Over **700 Million** smartphone users nationwide.
* 🌾 **425 Million+** active internet users in rural areas alone.

> 💡 **The Core Opportunity:** What if essential healthcare guidance, first-aid triage, and emergency hospital routing could be delivered directly to rural patients and ASHA workers through intuitive, voice-enabled interfaces on platforms they already rely on?

---

## 🎯 Core Challenge

Design a resilient, low-latency, and accessible solution leveraging **AI, voice interfaces, and conversational messaging** to eliminate healthcare access bottlenecks in Tier 2/3 and rural regions.

### Essential Solution Pillars:
1. 🩺 **Verified First-Aid & Symptom Triage:** Provide instant, clinically sound guidance and emergency prioritization.
2. 🏥 **Government-First Healthcare Routing:** Connect patients with nearby CHCs, PHCs, and Civil Hospitals while prioritizing free public healthcare options.
3. 📞 **Zero-Cost Telemedicine Gateways:** Seamlessly bridge users to free government doctor consultations via eSanjeevani and state 104 helplines.
4. 🌐 **Indic Voice & Multilingual Architecture:** Native support for local languages and low-bandwidth rural networks.

---

## 💡 Goal

Empower rural communities with accessible, reliable, empathetic, and scalable healthcare support — delivered directly on their mobile devices without technical or financial barriers.

---

## 🏗️ Architecture & Core Features

```mermaid
graph TD
    A[📱 Mobile Client - React Native / Expo] -->|Voice / Text / Vitals| B[⚡ FastAPI AI & Routing Engine]
    B -->|Indic NMT / STT / TTS| C[🗣️ Multilingual Voice Pipeline]
    B -->|Spatial Search & Deduplication| D[🗺️ Spatial Engine - Ola Maps & OSM]
    B -->|Clinical Triage & Protocol Routing| E[🩺 Medical Inference Engine]
    A -->|Direct Intent / Telephony| F[📞 Teleconsultation Gateway]
    F -->|Dialer Intent| F1[☎️ 104 Govt Health Helpline]
    F -->|Deep Link Intent| F2[🌐 eSanjeevani National OPD]
    B -->|Structured Telemetry| G[📊 Centralized System Logger]
```

### Key Ecosystem Capabilities
* 🗣️ **Multilingual & Voice-First Pipeline:** Built for intuitive voice interaction, enabling users to speak naturally in Indic dialects to describe symptoms and receive spoken advice.
* 🚑 **Smart Emergency Triage:** Categorizes symptom severity in real-time, delivering immediate first-aid steps while flagging critical conditions requiring urgent evacuation.
* 📍 **Government-First Facility Discovery:** Features a hybrid spatial engine using Ola Maps and OpenStreetMap (Overpass QL) with automated deduplication and spatial filtering to surface free government health centers (CHCs/PHCs) before private clinics.
* 📞 **3-Tier Telemedicine Integration:** 
  - **Instant Audio Triage:** One-tap telephony connection to the 24/7 National/State **104 Health Helpline**.
  - **National Video OPD:** Deep-linked integration with the official **eSanjeevani (MoHFW)** portal for free specialist video consultations.
  - **Open Digital Health Standards:** Architectural alignment with **ABDM (Ayushman Bharat Digital Mission)** and **UHI (Unified Health Interface)** specs.
* 📝 **Centralized Field Telemetry:** Unified end-to-end logging piping frontend runtime diagnostics straight to backend telemetry for remote debugging in low-connectivity zones.

---

## 🌿 Branching Strategy

To keep the development environments clean and avoid file-tracking conflicts, this repository is split across three isolated branches based on the application layer:

1. **main (Backend)**: Contains the Python **FastAPI backend** (AI routing, Vision Service, and database integration).
2. **whatsapp-app-simulation (Mobile Frontend)**: Contains the **React Native (Expo)** mobile application. This acts as the primary simulated WhatsApp interface for rural patients.
3. **whatsapp-simulation (Web Frontend)**: Contains the **React (Vite)** web application for quick browser-based simulation testing.

> **Note:** Because these branches track completely different tech stacks, they deliberately ignore each others directories. If you want to work on the backend and frontend simultaneously, it is recommended to clone the repository into two separate folders on your local machine (e.g., one folder on the main branch, and another on the whatsapp-app-simulation branch).

---

## 🚀 Getting Started

### Prerequisites
* **Node.js** (v18+ recommended) & **npm**
* **Python** (v3.11+)
* **Expo Go** app installed on your physical mobile device (Android / iOS)

### 1. Launching the FastAPI Backend
```bash
# Navigate to the backend directory
cd fastapi_backend

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Launching the Mobile App (React Native / Expo)
```bash
# Navigate to the App directory
cd App

# Install npm dependencies
npm install

# Start the Expo development bundler
npx expo start
```
*Scan the QR code displayed in your terminal using the **Expo Go** app on Android or default Camera app on iOS to run the app live on your phone.*

---

## 🛡️ License & Acknowledgments

This project is open-sourced under the [MIT License](LICENSE).

Special thanks to the **Ministry of Health and Family Welfare (MoHFW)**, **National Health Authority (NHA)**, **Ayushman Bharat Digital Mission (ABDM)**, **OpenStreetMap contributors**, and **Ola Maps** for enabling digital public infrastructure that makes equitable healthcare access possible.
