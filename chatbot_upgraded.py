import streamlit as st
import re
import math
from collections import Counter

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text Mining Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }
    .chat-header {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .chat-header h1 { color: #a78bfa; font-size: 26px; margin: 0; font-weight: 700; }
    .chat-header p  { color: #c4b5fd; font-size: 14px; margin: 6px 0 0; }

    .msg-bot {
        background: rgba(167,139,250,0.15);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px; margin: 8px 0;
        color: #e9d5ff; font-size: 15px; max-width: 85%; line-height: 1.6;
    }
    .msg-user {
        background: rgba(99,179,237,0.2);
        border: 1px solid rgba(99,179,237,0.3);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px; margin: 8px 0 8px auto;
        color: #bfdbfe; font-size: 15px; max-width: 85%;
        text-align: right; line-height: 1.6; display: flex; justify-content: flex-end;
    }
    .msg-label-bot  { font-size:11px; color:#a78bfa; margin:4px 0 2px 4px; font-weight:600; letter-spacing:.5px; }
    .msg-label-user { font-size:11px; color:#93c5fd; margin:4px 4px 2px 0; font-weight:600; letter-spacing:.5px; text-align:right; }

    .analysis-box {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 12px;
        color: #c4b5fd;
        margin: 6px 0;
    }
    .tag-pos  { background: rgba(74,222,128,0.2); color:#4ade80; padding:2px 8px; border-radius:12px; font-size:11px; margin:2px; display:inline-block; }
    .tag-neg  { background: rgba(248,113,113,0.2); color:#f87171; padding:2px 8px; border-radius:12px; font-size:11px; margin:2px; display:inline-block; }
    .tag-neu  { background: rgba(250,204,21,0.2);  color:#facc15; padding:2px 8px; border-radius:12px; font-size:11px; margin:2px; display:inline-block; }
    .tag-word { background: rgba(167,139,250,0.2); color:#a78bfa; padding:2px 8px; border-radius:12px; font-size:11px; margin:2px; display:inline-block; }

    .stButton > button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 20px !important;
        color: #c4b5fd !important;
        font-size: 12px !important;
        padding: 6px 14px !important;
        margin: 3px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: rgba(167,139,250,0.2) !important;
        border-color: #a78bfa !important;
        color: #fff !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 12px !important;
        color: #e9d5ff !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(196,181,253,0.5) !important; }
    .chat-area {
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 16px; min-height: 380px; max-height: 450px;
        overflow-y: auto; margin-bottom: 16px;
    }
    hr { border-color: rgba(255,255,255,0.1); }
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
#  TEXT MINING PIPELINE  (pure Python — no heavy external downloads needed)
# ════════════════════════════════════════════════════════════════════════════════

# ── 1. Stop-words list (built-in, no download) ─────────────────────────────────
STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","he","him","his","himself","she","her","hers","herself","it",
    "its","itself","they","them","their","theirs","themselves","what","which",
    "who","whom","this","that","these","those","am","is","are","was","were",
    "be","been","being","have","has","had","having","do","does","did","doing",
    "a","an","the","and","but","if","or","because","as","until","while","of",
    "at","by","for","with","about","against","between","into","through",
    "during","before","after","above","below","to","from","up","down","in",
    "out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll",
    "m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn",
    "weren","won","wouldn","main","hai","hain","ho","ka","ki","ke","mein",
    "se","ko","ne","bhi","to","yeh","ye","woh","wo","ek","aur","kya","nahi",
    "tha","thi","the","hoga","hogi","karo","karta","karti","karte","gaya",
    "gayi","gaye","raha","rahi","rahe","liye","wala","wali","wale","ab","aaj",
}

# ── 2. Stemmer (simple suffix-stripping, no download) ──────────────────────────
SUFFIXES = ["ing","tion","ness","ment","ful","less","ous","er","est","ly",
            "ed","es","ies","ied","ier","iest","ize","ise","ize"]

def simple_stem(word: str) -> str:
    w = word.lower()
    for suf in SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w

# ── 3. Lemmatizer dictionary (common irregular forms) ──────────────────────────
LEMMA_MAP = {
    "running":"run","runs":"run","ran":"run",
    "flying":"fly","flies":"fly","flew":"fly",
    "studying":"study","studies":"study","studied":"study",
    "better":"good","best":"good","worse":"bad","worst":"bad",
    "was":"be","were":"be","am":"be","are":"be","is":"be","been":"be",
    "had":"have","has":"have","having":"have",
    "did":"do","does":"do","doing":"do","done":"do",
    "went":"go","goes":"go","going":"go","gone":"go",
    "said":"say","says":"say","saying":"say",
    "took":"take","takes":"take","taking":"take","taken":"take",
    "made":"make","makes":"make","making":"make",
    "came":"come","comes":"come","coming":"come",
    "saw":"see","sees":"see","seeing":"see","seen":"see",
    "knew":"know","knows":"know","knowing":"know","known":"know",
    "children":"child","men":"man","women":"woman","people":"person",
    "teeth":"tooth","feet":"foot","mice":"mouse","geese":"goose",
}

def simple_lemmatize(word: str) -> str:
    w = word.lower()
    return LEMMA_MAP.get(w, w)

# ── 4. Tokenizer ───────────────────────────────────────────────────────────────
def tokenize(text: str):
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

# ── 5. Full preprocessing pipeline ────────────────────────────────────────────
def preprocess(text: str, use_stem=False):
    tokens = tokenize(text)
    tokens = [t for t in tokens if t not in STOPWORDS]
    if use_stem:
        tokens = [simple_stem(t) for t in tokens]
    else:
        tokens = [simple_lemmatize(t) for t in tokens]
    return tokens

# ── 6. Simple sentiment (lexicon-based) ───────────────────────────────────────
POS_WORDS = {
    "good","great","amazing","excellent","wonderful","fantastic","awesome",
    "love","like","best","happy","joy","nice","helpful","useful","clear",
    "interesting","perfect","beautiful","brilliant","cool","easy","fast",
    "fun","smart","strong","success","win","acha","achi","badhiya","shukriya",
    "maza","khushi","pasand","help","madad","theek","bilkul","zaroor",
}
NEG_WORDS = {
    "bad","terrible","awful","hate","worst","boring","hard","difficult",
    "wrong","fail","error","bug","confused","problem","issue","slow","ugly",
    "stupid","useless","mushkil","mushkilat","ganda","bura","nahi","nahi",
    "samajh","confuse","thaka","bore","pareshan",
}

def detect_sentiment(tokens):
    pos = sum(1 for t in tokens if t in POS_WORDS)
    neg = sum(1 for t in tokens if t in NEG_WORDS)
    score = pos - neg
    if score > 0:
        return "Positive 😊", "#4ade80", "pos"
    elif score < 0:
        return "Negative 😠", "#f87171", "neg"
    else:
        return "Neutral 😐", "#facc15", "neu"

# ── 7. TF-IDF cosine similarity for intent matching ────────────────────────────
def build_tfidf(corpus):
    """Returns (tfidf_matrix list-of-dicts, idf_dict)."""
    N = len(corpus)
    tokenized = [tokenize(doc) for doc in corpus]
    df = Counter()
    for tokens in tokenized:
        for t in set(tokens):
            df[t] += 1
    idf = {t: math.log((N + 1) / (cnt + 1)) + 1 for t, cnt in df.items()}
    matrix = []
    for tokens in tokenized:
        tf = Counter(tokens)
        total = len(tokens) or 1
        vec = {t: (cnt / total) * idf.get(t, 1) for t, cnt in tf.items()}
        matrix.append(vec)
    return matrix, idf

def cosine_sim(v1, v2):
    keys = set(v1) & set(v2)
    dot  = sum(v1[k] * v2[k] for k in keys)
    n1   = math.sqrt(sum(x*x for x in v1.values()))
    n2   = math.sqrt(sum(x*x for x in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def query_tfidf(user_input, matrix, idf):
    tokens = tokenize(user_input)
    tf = Counter(tokens)
    total = len(tokens) or 1
    q_vec = {t: (cnt / total) * idf.get(t, 1) for t, cnt in tf.items()}
    scores = [cosine_sim(q_vec, doc_vec) for doc_vec in matrix]
    return scores

# ── 8. Simple NER (regex + keyword lookup) ────────────────────────────────────
NER_PATTERNS = [
    (r"\b(python|nltk|spacy|gensim|sklearn|textblob|streamlit|tensorflow|pytorch)\b",    "LIBRARY 📦"),
    (r"\b(text mining|nlp|natural language processing|machine learning|deep learning)\b", "FIELD 🔬"),
    (r"\b(sir shazaib|anisha maroof|javeria akmal|kainat arshad|ahmed)\b",               "PERSON 👤"),
    (r"\b(tokenization|stemming|lemmatization|tfidf|tf-idf|bag of words|ner|pos tagging|sentiment analysis|word2vec|regex|preprocessing)\b", "CONCEPT 💡"),
    (r"\b\d{4}\b",                                                                        "YEAR 📅"),
]

def extract_entities(text):
    found = []
    t = text.lower()
    for pattern, label in NER_PATTERNS:
        matches = re.findall(pattern, t)
        for m in matches:
            found.append((m, label))
    return found


# ════════════════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE (Rule-Based)
# ════════════════════════════════════════════════════════════════════════════════
RULES = [
    # Greetings
    {"keywords": ["salam","salaam","assalam","hello","^hi$","hi ","hey","helo"],
     "response": "Wa Alaikum Assalam! 😊 Marhaba! Main Text Mining Chatbot hoon. Aap Sir Shazaib ke subject ke baare mein kuch bhi pooch sakte hain!"},
    {"keywords": ["good morning","subha bakhair","subah"],
     "response": "Good Morning! ☀️ Umeed hai aapka din acha ho. Text Mining ke baare mein koi sawaal puchna ho to zaroor puchein!"},
    {"keywords": ["good night","shab bakhair","raat","good evening"],
     "response": "Good Night! 🌙 Kal phir milenge. Padhai jari rakhen!"},

    # Teacher / Course
    {"keywords": ["sir shazaib","teacher","ustad","professor","lecturer","instructor"],
     "response": "👨‍🏫 **Sir Shazaib** hamare Text Mining course ke instructor hain. Unka padhane ka andaz bohot clear aur practical hai. Woh real-world examples se concepts samjhate hain."},
    {"keywords": ["course","subject","class"],
     "response": "📚 Ye chatbot **Text Mining** course ke liye banaya gaya hai jo Sir Shazaib padhate hain. Is course mein text preprocessing, tokenization, NLP, sentiment analysis aur bahut kuch cover hota hai!"},

    # Core Concepts
    {"keywords": ["text mining kya","text mining hai","what is text mining","text mining define"],
     "response": "📖 **Text Mining** ek process hai jisme unstructured text data se meaningful patterns nikale jate hain.\n\n🔑 Key points:\n• Raw text → Useful insights\n• NLP + ML techniques use hoti hain\n• Applications: search engines, spam filters, sentiment analysis"},
    {"keywords": ["tokenization","token kya","tokenize"],
     "response": "✂️ **Tokenization** text ko chhote pieces (tokens) mein todhne ka process hai.\n\n📌 Example:\n```\nInput:  'Text mining bohot useful hai'\nTokens: ['Text', 'mining', 'bohot', 'useful', 'hai']\n```\n\n🛠️ Python:\n```python\nimport nltk\ntokens = nltk.word_tokenize('Text mining bohot useful hai')\nprint(tokens)\n```"},
    {"keywords": ["stopword","stop word","stop words"],
     "response": "🚫 **Stop Words** woh common words hain jo meaning nahi add kartey — jaise: is, are, the, a, an...\n\n🛠️ Python:\n```python\nfrom nltk.corpus import stopwords\nstop_words = set(stopwords.words('english'))\nfiltered = [w for w in tokens if w.lower() not in stop_words]\n```"},
    {"keywords": ["stemming","stem kya","stemmer"],
     "response": "🌱 **Stemming** words ko root form par reduce karta hai.\n\n📌 Example:\n• running → run  |  flies → fli  |  studies → studi\n\n🛠️ Python:\n```python\nfrom nltk.stem import PorterStemmer\nps = PorterStemmer()\nprint(ps.stem('running'))  # run\n```\n\n⚠️ Kabhi kabhi galat result deta hai — Lemmatization behtar hai."},
    {"keywords": ["lemmatization","lemma","lemmatize"],
     "response": "📚 **Lemmatization** proper dictionary form (lemma) deta hai.\n\n📌 Example:\n• running → run  |  flies → fly  |  better → good\n\n🛠️ Python:\n```python\nfrom nltk.stem import WordNetLemmatizer\nlm = WordNetLemmatizer()\nprint(lm.lemmatize('running', pos='v'))  # run\nprint(lm.lemmatize('better', pos='a'))   # good\n```"},
    {"keywords": ["pos tagging","part of speech","pos tag"],
     "response": "🏷️ **POS Tagging** har word ko grammatical category assign karta hai.\n\n📌 Tags: NN=Noun, VB=Verb, JJ=Adjective, RB=Adverb\n\n🛠️ Python:\n```python\nimport nltk\ntagged = nltk.pos_tag(nltk.word_tokenize('Text mining is useful'))\nprint(tagged)\n```"},
    {"keywords": ["ner","named entity","entity recognition"],
     "response": "🔍 **NER** text mein real-world entities identify karta hai.\n\n📌 Types: PERSON, ORG, GPE (location), DATE\n\n🛠️ Python (spaCy):\n```python\nimport spacy\nnlp = spacy.load('en_core_web_sm')\ndoc = nlp('Google was founded in California by Larry Page')\nfor ent in doc.ents:\n    print(ent.text, '->', ent.label_)\n```"},
    {"keywords": ["tfidf","tf-idf","tf idf","term frequency"],
     "response": "📊 **TF-IDF** words ki importance measure karta hai.\n\n📐 Formula:\n• TF = word count / total words\n• IDF = log(total docs / docs with word)\n• TF-IDF = TF × IDF\n\n🛠️ Python:\n```python\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nvec = TfidfVectorizer()\nmatrix = vec.fit_transform(docs)\n```"},
    {"keywords": ["bag of words","bow","word bag"],
     "response": "🎒 **Bag of Words** text ko word frequency vectors mein convert karta hai.\n\n📌 Example:\n```\nDoc1: 'I love text mining'  → [1,1,1,1,0,0]\nDoc2: 'Text mining is great' → [0,0,1,1,1,1]\n```\n\n🛠️ Python:\n```python\nfrom sklearn.feature_extraction.text import CountVectorizer\nvec = CountVectorizer()\nX = vec.fit_transform(docs)\n```"},
    {"keywords": ["sentiment analysis","sentiment kya","opinion mining"],
     "response": "😊😐😠 **Sentiment Analysis** text ki emotional tone detect karta hai.\n\n🛠️ Python (TextBlob):\n```python\nfrom textblob import TextBlob\nblob = TextBlob('This is amazing!')\nprint(blob.sentiment.polarity)  # > 0 → Positive\n```"},
    {"keywords": ["word2vec","word embedding","word vector"],
     "response": "🔢 **Word2Vec** words ko numeric vectors mein convert karta hai.\n\n📌 Interesting: King - Man + Woman = Queen!\n\n🛠️ Python:\n```python\nfrom gensim.models import Word2Vec\nmodel = Word2Vec(sentences, vector_size=100)\nvector = model.wv['text']\n```"},
    {"keywords": ["regex","regular expression","pattern matching"],
     "response": "🔎 **Regex** text mein patterns dhundhne ke liye use hoti hai.\n\n🛠️ Python:\n```python\nimport re\nemails = re.findall(r'[\\w.]+@[\\w.]+', text)\nphones = re.findall(r'\\d{4}-\\d{7}', text)\n```"},
    {"keywords": ["text classification","classify text","categorize"],
     "response": "📂 **Text Classification** text ko categories mein classify karta hai.\n\n🛠️ Python (Naive Bayes):\n```python\nfrom sklearn.naive_bayes import MultinomialNB\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nmodel = Pipeline([('tfidf', TfidfVectorizer()), ('clf', MultinomialNB())])\nmodel.fit(texts, labels)\n```"},
    {"keywords": ["preprocessing","text clean","data clean"],
     "response": "🧹 **Text Preprocessing** steps:\n1. Lowercasing\n2. Remove Punctuation\n3. Tokenization\n4. Stop Words Remove\n5. Stemming / Lemmatization\n\n```python\ndef preprocess(text):\n    text = text.lower()\n    text = re.sub(r'[^a-z\\s]', '', text)\n    tokens = nltk.word_tokenize(text)\n    tokens = [t for t in tokens if t not in stop_words]\n    tokens = [lm.lemmatize(t) for t in tokens]\n    return ' '.join(tokens)\n```"},
    {"keywords": ["nltk","nltk library"],
     "response": "📦 **NLTK** Python ki popular text processing library hai.\n\n```python\npip install nltk\nimport nltk\nnltk.download('all')\n```\n\nFeatures: Tokenization, Stemming, Lemmatization, POS Tagging, Corpora"},
    {"keywords": ["spacy","spacy library"],
     "response": "⚡ **spaCy** fast aur production-ready NLP library hai.\n\n```python\npip install spacy\npython -m spacy download en_core_web_sm\nimport spacy\nnlp = spacy.load('en_core_web_sm')\n```\n\nFeatures: NER, POS Tagging, Dependency Parsing, Word Vectors"},
    {"keywords": ["cosine similarity","cosine","similarity"],
     "response": "📐 **Cosine Similarity** do documents ke beech similarity measure karta hai.\n\n📌 Formula: cos(θ) = (A·B) / (|A| × |B|)\n• 1 = identical\n• 0 = completely different\n\n🛠️ Python:\n```python\nfrom sklearn.metrics.pairwise import cosine_similarity\nscore = cosine_similarity(vec1, vec2)\n```"},

    # Class Info
    {"keywords": ["cr kaun","cr kon","class representative","cr ahmed"],
     "response": "👑 Hamare class ka **CR Ahmed** hai! Class ki saari updates, assignments aur announcements Ahmed hi deliver karta hai!"},
    {"keywords": ["topper","first position","best student","ayesha anwar","topper kaun"],
     "response": "🏆 Hamare class ka **topper Ahmed** hai! Har exam mein first position leta hai. CR bhi, topper bhi — double role! 💪"},
    {"keywords": ["favourite student","pasandida student"],
     "response": "❤️ Meri favourite student **Ayesha Anwar** hai! Class mein bohot active rehti hai. 🌸"},
    {"keywords": ["anisha","is chatbot ka naam","developer","banane wali","kisne banaya"],
     "response": "👩‍💻 Is chatbot ko **Anisha Maroof** ne banaya hai! Ye project unka Text Mining Lab ka project hai jo Sir Shazaib ke course ke liye develop kiya gaya hai! 🎓"},
    {"keywords": ["kis ka project","kiska project","lab project","kis ne banaya"],
     "response": "📁 Ye **Anisha Maroof, Javeria Akmal aur Kainat Arshad** ka project hai!\n\n🎓 Subject: Text Mining Lab | Instructor: Sir Shazaib | Tech Stack: Python + Streamlit 🚀"},

    # Casual
    {"keywords": ["joke","mazak","funny","hasao"],
     "response": "😂 Ek NLP joke:\n**Q:** Why did the NLP model break up?\n**A:** Because it couldn't understand her *sentiment*! 💔\n\n**Q:** Text miner ka favourite game?\n**A:** *Token* Ring! 🪙"},
    {"keywords": ["exam","paper","test","quiz"],
     "response": "📝 **Exam Tips:**\n• Tokenization aur Preprocessing zaroor yaad karo\n• TF-IDF formula samjho — sirf yaad mat karo\n• Stemming vs Lemmatization ka farq clear karo\n• NLTK code practice karo\n• Sir Shazaib ke slides dobara dekho! 🌟"},
    {"keywords": ["assignment","homework","task","project"],
     "response": "📋 Text Mining assignments mein usually:\n• Text data ko preprocess karna\n• TF-IDF ya BoW se features banana\n• Sentiment analysis karna\n• Classification model banana\n\nCode mein comments lagao — Sir Shazaib ko pasand hai! 😄"},
    {"keywords": ["bored","bore ho","kuch nahi karna"],
     "response": "😂 Bore ho rahe ho? Chalo Text Mining padho — Tokenization try karo, sentiment analysis dekho... maza aayega! 🤓"},
    {"keywords": ["bhook","khana","hungry","biryani","chai"],
     "response": "😄 Pehle Text Mining ka homework khatam karo, phir biryani khao! 🍛 Waise chai ke saath NLTK documentation bhi parh lo! ☕"},
    {"keywords": ["theek ho","kaise ho","how are you"],
     "response": "Main bilkul theek hoon! 😄 Aur aap? Koi Text Mining topic samajhna ho to bataein!"},
    {"keywords": ["shukriya","thank you","thanks"],
     "response": "😊 Aapka shukriya! Mujhe khushi hai ke main madad kar saka. Aur kuch poochhna ho to zaroor puchein!"},
    {"keywords": ["bye","alvida","khuda hafiz","phir milenge"],
     "response": "👋 Khuda Hafiz! Padhai mein mehnat karo. Sir Shazaib ke notes zaroor revise karna. Allah Hafiz! 🌟"},
    {"keywords": ["love","pyaar","crush","dil"],
     "response": "😄 Abhi pyaar chhodo, pehle Text Mining se pyaar karo! Jis din TF-IDF samajh aa gaya, us din sab samajh aa jayega! 😂"},
    {"keywords": ["mausam","weather","garmi","sardi"],
     "response": "🌤️ Perfect mausam hai ghar baith ke Text Mining padhne ka! 😄 Python kholo, code likho, life set karo!"},
]

SUGGESTIONS = [
    "Salam! 👋", "Text Mining kya hai?", "Tokenization explain karo",
    "Stop Words kya hain?", "Stemming vs Lemmatization", "TF-IDF kya hai?",
    "Sentiment Analysis", "Bag of Words samjhao", "NER kya hai?",
    "Cosine Similarity", "Word2Vec kya hai?", "Regex in Python",
    "NLTK library", "Text Classification", "Sir Shazaib kaun hain?",
    "CR kaun hai? 👑", "Ek joke sunao 😂", "Exam tips do! 📝",
    "Kaise ho? 😊", "Ye kis ka project hai?",
]


# ════════════════════════════════════════════════════════════════════════════════
#  TF-IDF INDEX over RULES (built once at startup)
# ════════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def build_rule_index():
    # Represent each rule as a "document" = its keywords joined
    corpus = [" ".join(r["keywords"]) for r in RULES]
    matrix, idf = build_tfidf(corpus)
    return matrix, idf

TFIDF_MATRIX, IDF = build_rule_index()


# ════════════════════════════════════════════════════════════════════════════════
#  RESPONSE ENGINE
# ════════════════════════════════════════════════════════════════════════════════
def get_response(user_input):
    text = user_input.lower().strip()

    # ── Step 1: Rule-based regex match (fast, exact) ──────────────────────────
    for rule in RULES:
        for kw in rule["keywords"]:
            if re.search(kw, text):
                return rule["response"], "regex"

    # ── Step 2: TF-IDF cosine similarity fallback ─────────────────────────────
    scores = query_tfidf(text, TFIDF_MATRIX, IDF)
    best_idx = max(range(len(scores)), key=lambda i: scores[i])
    best_score = scores[best_idx]

    if best_score > 0.1:
        return RULES[best_idx]["response"], f"tfidf ({best_score:.2f})"

    # ── Step 3: Default fallback ───────────────────────────────────────────────
    return (
        "🤔 Is sawaal ka jawab mere paas nahi hai abhi.\n\n"
        "Aap ye topics pooch sakte hain:\n"
        "• Text Mining basics\n• Tokenization, Stemming, Lemmatization\n"
        "• TF-IDF, Bag of Words, Cosine Similarity\n"
        "• Sentiment Analysis, NER\n• NLTK, spaCy libraries\n\n"
        "Ya Sir Shazaib se class mein poochein! 😊"
    ), "no_match"


def analyze_input(user_input):
    """Run full text mining pipeline on user input and return analysis dict."""
    tokens_raw = tokenize(user_input)
    tokens_no_stop = [t for t in tokens_raw if t not in STOPWORDS]
    tokens_lemma = [simple_lemmatize(t) for t in tokens_no_stop]
    tokens_stem = [simple_stem(t) for t in tokens_no_stop]
    sentiment_label, sentiment_color, sentiment_cls = detect_sentiment(tokens_lemma)
    entities = extract_entities(user_input)
    return {
        "tokens_raw": tokens_raw,
        "tokens_no_stop": tokens_no_stop,
        "tokens_lemma": tokens_lemma,
        "tokens_stem": tokens_stem,
        "sentiment_label": sentiment_label,
        "sentiment_color": sentiment_color,
        "sentiment_cls": sentiment_cls,
        "entities": entities,
    }


def render_analysis(a):
    """Return HTML string showing the text mining analysis panel."""
    def tags(words, cls="word"):
        return " ".join(f'<span class="tag-{cls}">{w}</span>' for w in words) or "<i>—</i>"

    ent_html = " ".join(
        f'<span class="tag-word">{e} <small style="opacity:.7">{lbl}</small></span>'
        for e, lbl in a["entities"]
    ) or "<i>none detected</i>"

    scls = a["sentiment_cls"]
    return f"""
<div class="analysis-box">
<b>🔬 Text Mining Analysis</b><br><br>
<b>Tokens:</b> {tags(a["tokens_raw"])}<br>
<b>After Stopword Removal:</b> {tags(a["tokens_no_stop"])}<br>
<b>Lemmatized:</b> {tags(a["tokens_lemma"])}<br>
<b>Stemmed:</b> {tags(a["tokens_stem"])}<br>
<b>Sentiment:</b> <span class="tag-{scls}">{a["sentiment_label"]}</span><br>
<b>NER Entities:</b> {ent_html}
</div>
"""


# ════════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "bot",
            "text": (
                "Assalamualaikum! 👋\n"
                "Main **Text Mining Chatbot** hoon — Sir Shazaib ke course ka virtual assistant!\n\n"
                "✨ **Naya Feature:** Har message ke saath live **Text Mining Analysis** dikhaya jata hai:\n"
                "Tokenization → Stopword Removal → Lemmatization → Stemming → Sentiment → NER!\n\n"
                "Neeche suggestions dekhen ya khud kuch type karein! 📚"
            ),
            "analysis": None,
        }
    ]

show_analysis = st.sidebar.toggle("🔬 Show Text Mining Analysis", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**📌 Text Mining Pipeline:**
1. Tokenization
2. Stopword Removal
3. Lemmatization
4. Stemming
5. Sentiment Analysis
6. Named Entity Recognition
7. TF-IDF Intent Matching
""")


# ════════════════════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="chat-header">
    <h1>🤖 Text Mining Chatbot</h1>
    <p>Sir Shazaib ke Text Mining Course ka Virtual Assistant | NLP-Powered</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
#  CHAT DISPLAY
# ════════════════════════════════════════════════════════════════════════════════
def render_text(t):
    return (t.replace("\n", "<br>")
             .replace("```python", '<pre style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;color:#a5f3fc;font-size:12px;overflow-x:auto;">')
             .replace("```", "</pre>")
             .replace("**", "<b>", 1).replace("**", "</b>"))

chat_html = '<div class="chat-area">'
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        chat_html += '<div class="msg-label-bot">🤖 StudyBot</div>'
        chat_html += f'<div class="msg-bot">{render_text(msg["text"])}</div>'
    else:
        chat_html += '<div class="msg-label-user">Aap 👤</div>'
        chat_html += f'<div class="msg-user">{msg["text"]}</div>'
        if show_analysis and msg.get("analysis"):
            chat_html += render_analysis(msg["analysis"])
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
#  SUGGESTION BUTTONS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("**💡 Quick Questions:**")
cols = st.columns(3)
for i, sug in enumerate(SUGGESTIONS):
    with cols[i % 3]:
        if st.button(sug, key=f"sug_{i}"):
            analysis = analyze_input(sug)
            response, method = get_response(sug)
            st.session_state.messages.append({"role": "user", "text": sug, "analysis": analysis})
            st.session_state.messages.append({"role": "bot", "text": response, "analysis": None})
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
#  INPUT BOX
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("---")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Apna sawaal yahan likhein:",
        placeholder="Masalan: Tokenization kya hai?",
        key="user_input",
        label_visibility="collapsed"
    )
with col2:
    send = st.button("📤 Send")

if send and user_input.strip():
    analysis = analyze_input(user_input.strip())
    response, method = get_response(user_input.strip())
    st.session_state.messages.append({"role": "user", "text": user_input.strip(), "analysis": analysis})
    st.session_state.messages.append({"role": "bot",  "text": response, "analysis": None})
    st.rerun()

if st.button("🗑️ Chat Clear Karo"):
    st.session_state.messages = [
        {"role": "bot", "text": "Chat clear ho gaya! Dobara start karte hain. Kya poochhna hai? 😊", "analysis": None}
    ]
    st.rerun()

st.markdown("---")
st.markdown(
    "<center style='color:rgba(196,181,253,0.5);font-size:12px;'>"
    "Text Mining Chatbot v2.0 | Anisha Maroof, Javeria Akmal, Kainat Arshad | Sir Shazaib | Python + Streamlit"
    "</center>",
    unsafe_allow_html=True
)
