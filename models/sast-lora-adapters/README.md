# 🛡️ SAST-AI: Yapay Zekâ Destekli Statik Kod Zafiyet Analizcisi

> **On-premise, API’siz, tamamen yerel çalışan** bir Static Application Security Testing (SAST) aracı.  
> Kullanıcının girdiği zafiyetli kodu analiz eder, güvenlik açıklarını tespit eder ve **güvenli yama (secure patch)** üretir.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Model](https://img.shields.io/badge/Model-DeepSeek--Coder--1.3B%20%2B%20LoRA-orange.svg)](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct)

---

## 🎯 Proje Özeti

Bu proje, klasik SAST araçlarının (SonarQube, Semgrep, Bandit vb.) ötesine geçerek **yapay zekâ** ile kod güvenliği analizi yapan uçtan uca bir sistemdir.

- Kullanıcı kodunu web arayüzüne yapıştırır
- Fine-tune edilmiş yerel model zafiyetleri analiz eder
- Hem zafiyet açıklaması hem de **düzeltilmiş güvenli kod** sunar
- **Hiçbir dış API (OpenAI, Claude vb.) kullanılmaz** — tamamen on-premise çalışır

---

## ✨ Öne Çıkan Özellikler

- **Yerel Fine-tuned Model**: DeepSeek-Coder-1.3B modeli QLoRA ile güvenlik veri setleri üzerinde eğitildi
- **Secure Patch Üretimi**: Sadece “zafiyet var” demez, düzeltilmiş kodu da verir
- **Web Tabanlı Arayüz**: Streamlit ile modern ve kullanıcı dostu arayüz
- **API Bağımsız**: İnternet bağlantısı olmadan da çalışabilir
- **Modüler Mimari**: Veri hazırlama, eğitim, inference ve arayüz birbirinden ayrı

---

## 🏗️ Mimari
1. Model Eğitimi (Google Colab - T4 GPU)
└── QLoRA + PEFT + TRL ile fine-tuning
└── Güvenlik odaklı veri setleri (Vulnerable → Secure pair)
2. Inference Engine
└── LoRA adapter + base model birleştirilerek yerel inference
3. Web Arayüzü (Streamlit)
└── Sol: Zafiyetli Kod | Sağ: Güvenli Yama


---

## 🛠️ Teknoloji Stack

| Katman              | Teknoloji                          |
|---------------------|------------------------------------|
| Base Model          | deepseek-ai/deepseek-coder-1.3b-instruct |
| Fine-tuning         | QLoRA, PEFT, TRL, bitsandbytes     |
| Web Framework       | Streamlit                          |
| Quantization        | 4-bit NF4                          |
| Dil                 | Python 3.10+                       |

---

## 🚀 Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/ulcnzey/sast-ai-web-app.git
cd sast-ai-web-app

# 2. Sanal ortam oluştur
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı başlat
streamlit run app.py

Not: models/sast-lora-adapters klasöründe fine-tune edilmiş LoRA ağırlıklarının bulunması gerekir.