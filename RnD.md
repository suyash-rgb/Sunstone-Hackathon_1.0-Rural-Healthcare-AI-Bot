we decided on a hybrid approach due to your 4GB VRAM hardware constraint:

EasyOCR (Local CPU): Used for reading text off of documents, prescriptions, and handwritten notes.

Gemini Flash (Cloud via google-generativeai): Used when the user uploads an actual photograph (like a picture of a skin rash, an injury, or an X-ray).

# What is NMT (Neural Machine Translation)?
NMT stands for Neural Machine Translation. It is the modern deep-learning approach to translating text between languages using neural network architectures (specifically Transformers).

Here is how it differs from older translation methods:

Old Way (Statistical / Rule-Based Translation): Translated text phrase-by-phrase or word-by-word. This frequently resulted in broken grammar, literal mistakes, and awkward phrasing—especially in Indian languages where sentence structure is Subject-Object-Verb (SOV) compared to English's Subject-Verb-Object (SVO).

NMT Way (Neural Networks): An NMT model (like IndicTrans2 or NLLB-200) reads the entire input sentence, converts its meaning into an abstract mathematical representation (vector space), and then generates a completely natural sentence in the target language while maintaining context, grammar, and idioms.