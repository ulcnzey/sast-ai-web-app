import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os
import re

st.set_page_config(
    page_title="SAST-AI | Code Security Analyzer",
    page_icon="🛡️",
    layout="wide"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

col_title, col_toggle = st.columns([6, 1])
with col_title:
    st.markdown("## 🛡️ SAST-AI")
    st.caption("Yapay Zekâ Destekli Statik Kod Zafiyet Analizcisi")
with col_toggle:
    st.session_state.dark_mode = st.toggle("🌙 Koyu Mod", value=st.session_state.dark_mode)

if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #0f172a; color: #e2e8f0; }
        .stTextArea textarea { background-color: #0f172a !important; color: #e2e8f0 !important; }
        .stButton > button { background: #3b82f6 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; }
        .stButton > button { background: #2563eb !important; color: white !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

BASE_MODEL = "deepseek-ai/deepseek-coder-1.3b-instruct"
ADAPTER_PATH = "./models/sast-lora-adapters"

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )

    if os.path.exists(ADAPTER_PATH):
        model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
        status = "fine-tuned"
    else:
        model = base_model
        status = "base"

    model.eval()
    return model, tokenizer, status

with st.spinner("Model yükleniyor (CPU modu)..."):
    model, tokenizer, model_status = load_model()

if model_status == "fine-tuned":
    st.success("Fine-tuned model aktif")
else:
    st.warning("Base model kullanılıyor")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔴 Zafiyetli Kod")
    vulnerable_code = st.text_area(
        "kod",
        height=300,
        placeholder="Zafiyetli kodunuzu yapıştırın...",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("#### 🟢 Güvenli Yama + Açıklama")
    result_box = st.empty()
    result_box.info("Sonuç burada görünecek.")

if st.button("🔍 Güvenlik Taraması Yap", use_container_width=True, type="primary"):
    if not vulnerable_code.strip():
        st.error("Lütfen kod yapıştırın.")
    else:
        with st.spinner("Analiz ediliyor..."):
            prompt = f"""### Vulnerable Code:
{vulnerable_code.strip()}

### Secure Patch:
"""
            inputs = tokenizer(prompt, return_tensors="pt")

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.1,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )

            full = tokenizer.decode(outputs[0], skip_special_tokens=True)
            secure_code = full.split("### Secure Patch:")[-1].strip() if "### Secure Patch:" in full else full

            explanation = ""
            code_lower = vulnerable_code.lower()
            if "select" in code_lower and ("f\"" in vulnerable_code or "f'" in vulnerable_code):
                explanation = "**Muhtemel Zafiyet:** SQL Injection\n\n**Neden tehlikeli?** Kullanıcı girdisi sorguya doğrudan ekleniyor.\n\n**Yapılan düzeltme:** Parametreli sorgu kullanılmalı."
            elif "os.system" in code_lower or "subprocess" in code_lower:
                explanation = "**Muhtemel Zafiyet:** Command Injection\n\n**Neden tehlikeli?** Kullanıcı girdisi sistem komutuna ekleniyor.\n\n**Yapılan düzeltme:** subprocess + liste argüman kullanılmalı."
            elif "pickle.loads" in code_lower:
                explanation = "**Muhtemel Zafiyet:** Insecure Deserialization\n\n**Neden tehlikeli?** Uzaktan kod çalıştırmaya yol açabilir."
            elif re.search(r"(api[_-]?key|secret|password|token)\s*=\s*[\"'][^\"']+[\"']", vulnerable_code, re.I):
                explanation = "**Muhtemel Zafiyet:** Hardcoded Secret\n\n**Neden tehlikeli?** Anahtar kod içinde açık yazılmış.\n\n**Yapılan düzeltme:** Ortam değişkeni kullanılmalı."
            else:
                explanation = "**Analiz:** Model güvenli alternatif üretti."

            # Hem açıklama hem güvenli kod sağ tarafta görünsün
            with result_box.container():
                st.markdown(explanation)
                st.markdown("**Secure Patch:**")
                st.code(secure_code, language="python")

            st.success("Analiz tamamlandı.")

st.divider()
st.caption("SAST-AI • DeepSeek-Coder 1.3B + LoRA • CPU modu")