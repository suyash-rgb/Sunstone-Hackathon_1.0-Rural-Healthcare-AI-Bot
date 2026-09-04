# 🏥 Rural Healthcare AI Bot

## 📖 Case Story

There is an almost **80% shortfall in Community Health Centres (CHCs)** in rural India, according to the *Health Dynamics of India* report on infrastructure and human resources released by the **Ministry of Health and Family Welfare**.

In **Tier 2 and Tier 3 towns**, access to quality healthcare remains a major challenge:
- Doctor shortages
- Long waiting times
- Limited hospital infrastructure
- Long travel hours just to reach a hospital

Meanwhile, **WhatsApp and other messaging platforms** are widely used across rural and semi-urban India. As of **January 2023**, India has:
- Over **700 million smartphone users**
- **425 million users in rural areas**

This presents a powerful opportunity:  
> What if essential healthcare guidance could be delivered directly to patients through familiar tools like WhatsApp?

---

## 🎯 Core Challenge

Design a solution that leverages **AI and conversational interfaces (like chatbots)** to improve access to healthcare in Tier 2/3 regions.

### Your solution might:
1. ✅ Provide **verified first-aid and basic health guidance**
2. 📞 Schedule **free or low-cost tele-consultations**
3. 🏥 Connect patients with **nearby government hospitals, clinics, or health camps**
4. 🌐 Handle **local languages** and **low-bandwidth environments**

---

## 💡 Goal

Empower rural communities with accessible, reliable, and scalable healthcare support — delivered through platforms they already use.

## 🌿 Branching Strategy

To keep the development environments clean and avoid file-tracking conflicts, this repository is split across three isolated branches based on the application layer:

1. **main (Backend)**: Contains the Python **FastAPI backend** (AI routing, Vision Service, and database integration).
2. **whatsapp-app-simulation (Mobile Frontend)**: Contains the **React Native (Expo)** mobile application. This acts as the primary simulated WhatsApp interface for rural patients.
3. **whatsapp-simulation (Web Frontend)**: Contains the **React (Vite)** web application for quick browser-based simulation testing.

> **Note:** Because these branches track completely different tech stacks, they deliberately ignore each others directories. If you want to work on the backend and frontend simultaneously, it is recommended to clone the repository into two separate folders on your local machine (e.g., one folder on the main branch, and another on the whatsapp-app-simulation branch).

---

## 🔗 Sources/Resources

*(Add your external APIs, datasets, documentation links, and other references here)*

