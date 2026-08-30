import sys
sys.stdout.reconfigure(encoding='utf-8')
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
SRC_LANG = "eng_Latn"
TGT_LANG = "mar_Deva"  # Change to "tam_Taml" for Tamil, "tel_Telu" for Telugu

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, trust_remote_code=True)
ip = IndicProcessor(inference=True)

# Qwen's English First-Aid Step Output
english_steps = [
    "1. Sit down immediately and remain calm. 2. Loosen any tight clothing around your neck and chest."
]

batch = ip.preprocess_batch(english_steps, src_lang=SRC_LANG, tgt_lang=TGT_LANG)
inputs = tokenizer(batch, src_lang=SRC_LANG, return_tensors="pt", padding=True)

with torch.inference_mode():
    outputs = model.generate(**inputs, num_beams=5, max_length=256, use_cache=False)

outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)
translations = ip.postprocess_batch(outputs, lang=TGT_LANG)

print("\n--- TRANSLATION OUTPUT ---")
print(f"English Input: {english_steps[0]}")
print(f"Hindi Output : {translations[0]}")
