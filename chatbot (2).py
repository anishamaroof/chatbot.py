import streamlit as st
import re
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text Mining Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* Header */
    .chat-header {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .chat-header h1 {
        color: #a78bfa;
        font-size: 26px;
        margin: 0;
        font-weight: 700;
    }
    .chat-header p {
        color: #c4b5fd;
        font-size: 14px;
        margin: 6px 0 0;
    }

    /* Chat messages */
    .msg-bot {
        background: rgba(167,139,250,0.15);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        color: #e9d5ff;
        font-size: 15px;
        max-width: 85%;
        line-height: 1.6;
    }
    .msg-user {
        background: rgba(99,179,237,0.2);
        border: 1px solid rgba(99,179,237,0.3);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0 8px auto;
        color: #bfdbfe;
        font-size: 15px;
        max-width: 85%;
        text-align: right;
        line-height: 1.6;
        display: flex;
        justify-content: flex-end;
    }
    .msg-label-bot {
        font-size: 11px;
        color: #a78bfa;
        margin: 4px 0 2px 4px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .msg-label-user {
        font-size: 11px;
        color: #93c5fd;
        margin: 4px 4px 2px 0;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-align: right;
    }

    /* Suggestion buttons */
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

    /* Input box */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 12px !important;
        color: #e9d5ff !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(196,181,253,0.5) !important;
    }

    /* Chat area */
    .chat-area {
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 16px;
        min-height: 380px;
        max-height: 420px;
        overflow-y: auto;
        margin-bottom: 16px;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.1); }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─── Knowledge Base (Rule-Based) ───────────────────────────────────────────────
RULES = [
    # Greetings
    {
        "keywords": ["salam", "salaam", "assalam", "hello", "hi ", "^hi$", "hey", "helo"],
        "response": "Wa Alaikum Assalam! 😊 Marhaba! Main Text Mining Chatbot hoon. Aap Sir Shazaib ke subject ke baare mein kuch bhi pooch sakte hain!"
    },
    {
        "keywords": ["good morning", "subha bakhair", "subah"],
        "response": "Good Morning! ☀️ Umeed hai aapka din acha ho. Text Mining ke baare mein koi sawaal puchna ho to zaroor puchein!"
    },
    {
        "keywords": ["good night", "shab bakhair", "raat", "good evening"],
        "response": "Good Night! 🌙 Kal phir milenge. Padhai jari rakhen!"
    },

    # Teacher Info
    {
        "keywords": ["sir shazaib", "teacher", "ustad", "professor", "lecturer", "instructor"],
        "response": "👨‍🏫 **Sir Shazaib** hamare Text Mining course ke instructor hain. Unka padhane ka andaz bohot clear aur practical hai. Woh real-world examples se concepts samjhate hain. Unke notes aur assignments bohot helpful hote hain!"
    },
    {
        "keywords": ["course", "subject", "class"],
        "response": "📚 Ye chatbot **Text Mining** course ke liye banaya gaya hai jo Sir Shazaib padhate hain. Is course mein text preprocessing, tokenization, NLP, sentiment analysis aur bahut kuch cover hota hai!"
    },

    # Text Mining Core Concepts
    {
        "keywords": ["text mining kya", "text mining hai", "what is text mining", "text mining define"],
        "response": "📖 **Text Mining** (ya Text Analytics) ek process hai jisme unstructured text data se meaningful patterns, information aur knowledge nikali jati hai.\n\n🔑 Key points:\n• Raw text → Useful insights\n• NLP + ML techniques use hoti hain\n• Applications: search engines, spam filters, sentiment analysis\n• Large text datasets par kaam karta hai"
    },
    {
        "keywords": ["tokenization", "token kya", "tokenize"],
        "response": "✂️ **Tokenization** text ko chhote pieces (tokens) mein todhne ka process hai.\n\n📌 Example:\n```\nInput:  'Text mining bohot useful hai'\nTokens: ['Text', 'mining', 'bohot', 'useful', 'hai']\n```\n\n🛠️ Python mein:\n```python\nimport nltk\nnltk.download('punkt')\ntokens = nltk.word_tokenize('Text mining bohot useful hai')\nprint(tokens)\n```"
    },
    {
        "keywords": ["stopword", "stop word", "stop words hatana"],
        "response": "🚫 **Stop Words** woh common words hain jo text mein meaning nahi add kartey — jaise: is, are, the, a, an, in, on...\n\n🛠️ Python mein remove karna:\n```python\nfrom nltk.corpus import stopwords\nfrom nltk.tokenize import word_tokenize\n\nstop_words = set(stopwords.words('english'))\ntext = 'This is a simple text mining example'\ntokens = word_tokenize(text)\nfiltered = [w for w in tokens if w.lower() not in stop_words]\nprint(filtered)\n# Output: ['simple', 'text', 'mining', 'example']\n```"
    },
    {
        "keywords": ["stemming", "stem kya", "stemmer"],
        "response": "🌱 **Stemming** words ko unki root/base form par reduce karne ka process hai.\n\n📌 Example:\n• running → run\n• flies → fli\n• studies → studi\n\n🛠️ Python mein:\n```python\nfrom nltk.stem import PorterStemmer\nps = PorterStemmer()\nwords = ['running', 'flies', 'studies', 'easily']\nfor w in words:\n    print(w, '->', ps.stem(w))\n```\n\n⚠️ Note: Stemming kabhi kabhi galat result deta hai (flies → fli). Iske liye Lemmatization behtar hai."
    },
    {
        "keywords": ["lemmatization", "lemma", "lemmatize"],
        "response": "📚 **Lemmatization** words ko unka proper dictionary form (lemma) deta hai.\n\n📌 Example:\n• running → run\n• flies → fly\n• better → good\n\n🛠️ Python mein:\n```python\nfrom nltk.stem import WordNetLemmatizer\nnltk.download('wordnet')\n\nlm = WordNetLemmatizer()\nprint(lm.lemmatize('running', pos='v'))  # run\nprint(lm.lemmatize('flies', pos='v'))   # fly\nprint(lm.lemmatize('better', pos='a'))  # good\n```\n\n✅ Stemming se zyada accurate hai!"
    },
    {
        "keywords": ["pos tagging", "part of speech", "pos tag"],
        "response": "🏷️ **POS Tagging** (Part-of-Speech Tagging) har word ko uski grammatical category assign karta hai.\n\n📌 Tags:\n• NN = Noun\n• VB = Verb\n• JJ = Adjective\n• RB = Adverb\n• DT = Determiner\n\n🛠️ Python mein:\n```python\nimport nltk\nnltk.download('averaged_perceptron_tagger')\n\ntext = nltk.word_tokenize('Text mining is very useful')\ntagged = nltk.pos_tag(text)\nprint(tagged)\n# [('Text', 'NNP'), ('mining', 'NN'), ('is', 'VBZ'), ...]\n```"
    },
    {
        "keywords": ["ner", "named entity", "entity recognition"],
        "response": "🔍 **Named Entity Recognition (NER)** text mein real-world entities identify karta hai.\n\n📌 Entity Types:\n• PERSON → 'Quaid-e-Azam'\n• ORG → 'Google', 'FAST University'\n• GPE → 'Pakistan', 'Lahore'\n• DATE → '10 May 2026'\n\n🛠️ Python mein (spaCy):\n```python\nimport spacy\nnlp = spacy.load('en_core_web_sm')\ndoc = nlp('Google was founded in California by Larry Page')\nfor ent in doc.ents:\n    print(ent.text, '->', ent.label_)\n```"
    },
    {
        "keywords": ["tfidf", "tf-idf", "tf idf", "term frequency"],
        "response": "📊 **TF-IDF** (Term Frequency-Inverse Document Frequency) words ki importance measure karta hai.\n\n📐 Formula:\n• TF = (word count in doc) / (total words in doc)\n• IDF = log(total docs / docs containing word)\n• TF-IDF = TF × IDF\n\n🛠️ Python mein:\n```python\nfrom sklearn.feature_extraction.text import TfidfVectorizer\n\ndocs = ['Text mining is useful', 'Mining data from text', 'NLP is interesting']\nvec = TfidfVectorizer()\ntfidf_matrix = vec.fit_transform(docs)\nprint(vec.get_feature_names_out())\nprint(tfidf_matrix.toarray())\n```"
    },
    {
        "keywords": ["bag of words", "bow", "word bag"],
        "response": "🎒 **Bag of Words (BoW)** text ko word frequency vectors mein convert karta hai.\n\n📌 Example:\n```\nDoc1: 'I love text mining'\nDoc2: 'Text mining is great'\n\nVocabulary: [I, love, text, mining, is, great]\nDoc1 vector: [1, 1, 1, 1, 0, 0]\nDoc2 vector: [0, 0, 1, 1, 1, 1]\n```\n\n🛠️ Python mein:\n```python\nfrom sklearn.feature_extraction.text import CountVectorizer\nvec = CountVectorizer()\nX = vec.fit_transform(['I love text mining', 'Text mining is great'])\nprint(vec.get_feature_names_out())\nprint(X.toarray())\n```"
    },
    {
        "keywords": ["sentiment analysis", "sentiment kya", "opinion mining"],
        "response": "😊😐😠 **Sentiment Analysis** text ki emotional tone detect karta hai — Positive, Negative ya Neutral.\n\n🛠️ Python mein (TextBlob):\n```python\nfrom textblob import TextBlob\n\nreviews = [\n    'This movie is amazing!',\n    'Terrible product, waste of money.',\n    'It is okay, nothing special.'\n]\nfor r in reviews:\n    blob = TextBlob(r)\n    polarity = blob.sentiment.polarity\n    if polarity > 0:\n        label = 'Positive 😊'\n    elif polarity < 0:\n        label = 'Negative 😠'\n    else:\n        label = 'Neutral 😐'\n    print(f'{r} --> {label} ({polarity:.2f})')\n```"
    },
    {
        "keywords": ["nlp kya", "natural language", "nlp hai"],
        "response": "🧠 **NLP** (Natural Language Processing) AI ki branch hai jo computers ko human language samajhne aur process karne mein help karta hai.\n\n📌 NLP Tasks:\n• Text Classification\n• Machine Translation\n• Question Answering\n• Summarization\n• Sentiment Analysis\n• Named Entity Recognition\n\n🔧 Popular Libraries:\n• NLTK\n• spaCy\n• Hugging Face Transformers\n• TextBlob\n• Gensim"
    },
    {
        "keywords": ["word2vec", "word embedding", "word vector"],
        "response": "🔢 **Word2Vec** words ko numeric vectors mein convert karta hai jisme semantic meaning preserve hoti hai.\n\n📌 Interesting Property:\n• King - Man + Woman = Queen\n• Paris - France + Italy = Rome\n\n🛠️ Python mein:\n```python\nfrom gensim.models import Word2Vec\n\nsentences = [\n    ['text', 'mining', 'is', 'useful'],\n    ['nlp', 'processing', 'language'],\n    ['machine', 'learning', 'text']\n]\nmodel = Word2Vec(sentences, vector_size=100, window=5, min_count=1)\nvector = model.wv['text']\nprint(vector[:5])  # First 5 dimensions\n```"
    },
    {
        "keywords": ["regex", "regular expression", "pattern matching"],
        "response": "🔎 **Regular Expressions (Regex)** text mein patterns dhundhne ke liye use hoti hain.\n\n🛠️ Python mein:\n```python\nimport re\n\ntext = 'Email: ali@gmail.com, Phone: 0300-1234567'\n\n# Email dhundho\nemails = re.findall(r'[\\w.]+@[\\w.]+', text)\nprint('Emails:', emails)\n\n# Phone dhundho\nphones = re.findall(r'\\d{4}-\\d{7}', text)\nprint('Phones:', phones)\n\n# Replace karo\nclean = re.sub(r'[^a-zA-Z\\s]', '', text)\nprint('Clean:', clean)\n```"
    },
    {
        "keywords": ["text classification", "classify text", "text categorize"],
        "response": "📂 **Text Classification** text ko predefined categories mein classify karta hai.\n\n📌 Examples:\n• Spam vs Not Spam\n• Positive vs Negative review\n• News categories: Sports, Politics, Tech\n\n🛠️ Python mein (Naive Bayes):\n```python\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.naive_bayes import MultinomialNB\nfrom sklearn.pipeline import Pipeline\n\ntexts = ['Free money now!', 'Meeting at 3pm', 'Win prize click here', 'Project deadline tomorrow']\nlabels = ['spam', 'ham', 'spam', 'ham']\n\nmodel = Pipeline([\n    ('tfidf', TfidfVectorizer()),\n    ('clf', MultinomialNB())\n])\nmodel.fit(texts, labels)\nprint(model.predict(['Get free gift now']))  # spam\n```"
    },
    {
        "keywords": ["nltk kya", "nltk hai", "nltk library"],
        "response": "📦 **NLTK** (Natural Language Toolkit) Python ki popular text processing library hai.\n\n🔧 Features:\n• Tokenization\n• Stemming & Lemmatization\n• POS Tagging\n• Parsing\n• Corpora & WordNet\n\n🛠️ Install & Use:\n```python\npip install nltk\n\nimport nltk\nnltk.download('all')  # Sab resources download karo\n\n# Ya specific:\nnltk.download('punkt')       # Tokenization\nnltk.download('stopwords')   # Stop words\nnltk.download('wordnet')     # Lemmatization\n```"
    },
    {
        "keywords": ["spacy", "spacy library"],
        "response": "⚡ **spaCy** ek fast aur production-ready NLP library hai.\n\n🔧 Features:\n• Tokenization\n• NER (Named Entity Recognition)\n• POS Tagging\n• Dependency Parsing\n• Word Vectors\n\n🛠️ Install & Use:\n```python\npip install spacy\npython -m spacy download en_core_web_sm\n\nimport spacy\nnlp = spacy.load('en_core_web_sm')\ndoc = nlp('Apple is looking at buying UK startup for $1 billion')\n\nfor token in doc:\n    print(token.text, token.pos_, token.dep_)\n\nfor ent in doc.ents:\n    print(ent.text, ent.label_)\n```"
    },
    {
        "keywords": ["preprocessing", "text clean", "text preprocess", "data clean"],
        "response": "🧹 **Text Preprocessing** raw text ko clean aur structured banane ka process hai.\n\n📋 Steps:\n1. **Lowercasing** → 'TEXT' → 'text'\n2. **Remove Punctuation** → 'Hello!' → 'Hello'\n3. **Tokenization** → words list\n4. **Stop Words Remove** → common words hatao\n5. **Stemming/Lemmatization** → root form\n\n🛠️ Complete Pipeline:\n```python\nimport re\nimport nltk\nfrom nltk.corpus import stopwords\nfrom nltk.stem import WordNetLemmatizer\n\ndef preprocess(text):\n    text = text.lower()                         # lowercase\n    text = re.sub(r'[^a-z\\s]', '', text)       # remove punctuation\n    tokens = nltk.word_tokenize(text)           # tokenize\n    stop = set(stopwords.words('english'))      # stop words\n    tokens = [t for t in tokens if t not in stop]\n    lm = WordNetLemmatizer()                    # lemmatize\n    tokens = [lm.lemmatize(t) for t in tokens]\n    return ' '.join(tokens)\n\nprint(preprocess('Text Mining is very USEFUL for analysis!'))\n# Output: text mining useful analysis\n```"
    },
    {
        "keywords": ["shukriya", "thank you", "thanks", "shukriya"],
        "response": "😊 Aapka shukriya! Mujhe khushi hai ke main aapki madad kar saka. Text Mining ke baare mein aur kuch poochhna ho to bilkul poochein. Sir Shazaib ke sawaalaat bhi welcome hain! 🎓"
    },
    {
        "keywords": ["bye", "alvida", "khuda hafiz", "phir milenge"],
        "response": "👋 Khuda Hafiz! Padhai mein mehnat karo. Sir Shazaib ke notes zaroor revise karna. Allah Hafiz! 🌟"
    },
    {
        "keywords": ["theek ho", "kya hal", "kaise ho", "how are you"],
        "response": "Main bilkul theek hoon, shukriya! 😄 Aur aap kaise hain? Koi Text Mining topic samajhna ho to bataein!"
    },

    # ── Class Info ─────────────────────────────────────────────────────────────
    {
        "keywords": ["cr kaun", "cr kon", "class representative", "cr ahmed", "ahmed cr", "cr hai", "cr kya"],
        "response": "👑 Hamare class ka **CR Ahmed** hai! Woh bahut zimmedar aur helpful student hai. Class ki saari updates, assignments aur announcements Ahmed hi deliver karta hai. Agar koi class se related kaam ho to Ahmed se milo! 📋"
    },
  
    {
        "keywords": ["favourite student", "favorite student", "meri favourite", "mera favourite", "pasandida student", "apni favourite"],
        "response": "❤️ Meri favourite student **Ayesha Anwar** hai! Woh bohot achi  hai aur class mein bohot active rehti hai. Ayesha se notes maango — zaroor NHI milenge! 🌸✨"
    },
    {
        "keywords": ["anisha maroof", "anisha", "aapka naam", "tumhara naam", "your name", "is chatbot ka naam", "chatbot naam", "mera naam", "teacher name", "banane wali", "kisne banaya", "developer"],
        "response": "👩‍💻 Is chatbot ko **Anisha Maroof** ne banaya hai!  Ye project unka **Text Mining Lab ka project** hai jo Sir Shazaib ke course ke liye develop kiya gaya hai! 🎓💻"
    },
    {
        "keywords": ["ye kis ka project", "kiska project", "yeh project", "lab project", "text mining lab", "kis ne banaya", "project kisne"],
        "response": "📁 Ye **Anisha Maroof** ka project hai! 👩‍💻\n\n🎓 **Project Details:**\n• **Developer:** Anisha Maroof\n• **Subject:** Text Mining Lab\n• **Instructor:** Sir Shazaib\n• **Type:** Rule-Based Chatbot\n• **Tech Stack:** Python + Streamlit\n\nIs chatbot mein Text Mining ke concepts, class info aur casual conversations — sab cover hain! 🚀"
    },
    {
        "keywords": ["ahmed kaun", "ahmed hai", "ahmed kon"],
        "response": "😄 **Ahmed** hamare class ka **CR (Class Representative)** hai! Woh class ke sab se responsible bande mein se hai. Assignments, attendance, announcements — sab ka khayal rakhta hai. Ek acha leader! 💪"
    },

    # ── Casual / Fun Questions ──────────────────────────────────────────────────
    {
        "keywords": ["bored", "bore ho", "kuch nahi karna", "pagal", "ajeeb"],
        "response": "😂 Arre bhai bore ho rahe ho? Chalo Text Mining padho — itni interesting cheez hai ke boredom bhool jaoge! Tokenization try karo, sentiment analysis dekho... maza aayega guarantee! 🤓"
    },
    {
        "keywords": ["bhook", "khana", "khaana", "hungry", "pizza", "biryani", "chai"],
        "response": "😄 Arre waah! Khane ki baat chal rahi hai? Pehle Text Mining ka homework khatam karo, phir biryani khao! 🍛 Waise agar chai pi rahe ho to saath mein NLTK documentation bhi parh lo — dono saath mein acha lagta hai! ☕😂"
    },
    {
        "keywords": ["neend", "so ja", "so raha", "sleepy", "tired", "thaka"],
        "response": "😴 Neend aa rahi hai? Ye natural hai — Text Mining padh ke bohot log so jaate hain! 😄 Lekin serious baat: exam se pehle soona mat, notes revise karo. Sir Shazaib ke questions tricky hote hain! ⚠️📖"
    },
    {
        "keywords": ["mausam", "weather", "garmi", "sardi", "baarish"],
        "response": "🌤️ Mausam ki baat chhodo yaar! Aaj ka mausam dekho — perfect hai ghar baith ke Text Mining padhne ka! 😄 Python kholo, code likho, life set karo!"
    },
    {
        "keywords": ["joke", "mazak", "funny", "hasao", "hans"],
        "response": "😂 Ek chhota sa NLP joke:\n\n**Q:** Why did the NLP model break up with the chatbot?\n**A:** Because it couldn't understand her *sentiment*! 💔😄\n\nAur ek:\n**Q:** Text miner ka favourite game kya hai?\n**A:** *Token* Ring! 🪙😂\n\nShukar ada karo ke main Data Scientist nahi comedian hoon! 😁"
    },
    {
        "keywords": ["problem", "mushkil", "samajh nahi", "confuse", "help karo", "madad"],
        "response": "💪 Koi baat nahi! Main hoon na! 😊 Batao kya samajh nahi aaya? Text Mining ka koi bhi topic pooch sakte ho:\n\n• Tokenization, Stemming, Lemmatization\n• TF-IDF, Bag of Words\n• Sentiment Analysis, NER\n• NLTK, spaCy, Regex\n\nYa agar kuch aur mushkil hai to Sir Shazaib ya CR Ahmed se rabta karo! 📞"
    },
    {
        "keywords": ["exam", "paper", "test", "quiz"],
        "response": "📝 Exam ki fikar? Ghabrao mat! 💪\n\n**Text Mining Exam Tips:**\n• Tokenization aur Preprocessing zaroor yaad karo\n• TF-IDF formula samjho — sirf yaad mat karo\n• NLTK code examples practice karo\n• Stemming vs Lemmatization ka farq clear karo\n• NER aur POS Tagging ke examples likhne ki practice karo\n\nSir Shazaib ke slides dobara dekho — woh important topics bold karte hain! 🌟"
    },
    {
        "keywords": ["assignment", "homework", "task", "project"],
        "response": "📋 Assignment mein help chahiye? 😊\n\nText Mining assignments mein usually ye hota hai:\n• Text data ko preprocess karna\n• TF-IDF ya BoW se features banana\n• Sentiment analysis karna\n• Classification model banana\n\nCode likhte waqt comments zaroor lagao — Sir Shazaib ko pasand hai! 😄\nAur CR Ahmed se deadline zaroor pooch lena! ⏰"
    },
    {
        "keywords": ["love", "pyaar", "mohabbat", "crush", "dil"],
        "response": "😄💜 Arre yaar! Abhi pyaar chhodo, pehle Text Mining se pyaar karo! Jis din TF-IDF samajh aa gaya, us din sab kuch samajh aa jayega! 😂\n\nSir Shazaib kehte hain: **'Data se mohabbat karo, result milega!'** 🤖❤️"
    },
    {
        "keywords": ["time kya", "date kya", "aaj kya", "kitne baje"],
        "response": "🕐 Main ek chatbot hoon, isliye real-time clock mera kaam nahi! 😄 Apne phone mein dekh lo — wahan exact time milega. Lekin jo bhi time hai, padhai shuru karo! 📚"
    },
    {
        "keywords": ["chutti", "holiday", "break", "chhutti"],
        "response": "🎉 Chutti ki baat achi lagi!  CR Ahmed se confirm karo ke kal class hai ya nahi. Aur chutti mein bhi Text Mining thoda parh lena — future ke liye kaam aayega! 😄"
    },
    {
        "keywords": ["kya lagta", "opinion", "best topic", "pasandida topic"],
        "response": "🤔 Mera personal favourite topic? **Sentiment Analysis!** 😊\n\nSoch ke dekho — ek program jo samajh sake ke banda khush hai ya udaas — kitna amazing hai yeh! Aur **NER** bhi bohot interesting hai. Real-world mein bohot use hota hai social media analysis, news processing mein. Aapka favourite kya hai? 😄"
    },
    {
        "keywords": ["python easy", "python mushkil", "coding hard", "programming", "code"],
        "response": "💻 Python actually bohot easy language hai — especially Text Mining ke liye! 🐍\n\n**Beginner Tips:**\n• Pehle basic syntax seekho (1 hafte mein)\n• NLTK se start karo\n• Chote chote programs likho\n• Errors se ghabrao mat — ye normal hai!\n• Stack Overflow tumhara dost hai! 😄\n\nYaad rakho: Sir Shazaib bhi kabhi beginner the! 🌱"
    },
]

SUGGESTIONS = [
    "Salam! 👋",
    "Text Mining kya hai?",
    "Tokenization explain karo",
    "Stop Words kya hain?",
    "Stemming vs Lemmatization",
    "TF-IDF kya hai?",
    "Sentiment Analysis",
    "Bag of Words samjhao",
    "NER kya hai?",
    "Text Preprocessing steps",
    "Word2Vec kya hai?",
    "Regex in Python",
    "NLTK library",
    "Text Classification",
    "Sir Shazaib kaun hain?",
    "CR kaun hai? 👑",
    "Favourite student kaun hai? ❤️",
    "Anisha Maroof kaun hain?",
    "Ye kis ka project hai?",
    "Ek joke sunao 😂",
    "Exam tips do! 📝",
    "Kaise ho? 😊",
]


# ─── Rule Matching Function ─────────────────────────────────────────────────────
def get_response(user_input):
    text = user_input.lower().strip()
    for rule in RULES:
        for kw in rule["keywords"]:
            if re.search(kw, text):
                return rule["response"]
    return ("🤔 Is sawaal ka jawab mere paas nahi hai abhi.\n\n"
            "Aap ye topics pooch sakte hain:\n"
            "• Text Mining basics\n• Tokenization, Stemming, Lemmatization\n"
            "• TF-IDF, Bag of Words\n• Sentiment Analysis, NER\n"
            "• NLTK, spaCy libraries\n• Text Preprocessing\n\n"
            "Ya Sir Shazaib se class mein poochein! 😊")


# ─── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "bot",
            "text": "Assalamualaikum! 👋\nMain **Text Mining Chatbot** hoon — Sir Shazaib ke course ka virtual assistant!\n\nAap Text Mining ke kisi bhi topic ke baare mein pooch sakte hain. Neeche suggestions dekhen ya khud kuch type karein! 📚"
        }
    ]


# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h1>🤖 Text Mining Chatbot</h1>
    <p>Sir Shazaib ke Text Mining Course ka Virtual Assistant</p>
</div>
""", unsafe_allow_html=True)


# ─── Chat Display ───────────────────────────────────────────────────────────────
chat_html = '<div class="chat-area">'
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        chat_html += f'<div class="msg-label-bot">🤖 StudyBot</div>'
        text = msg["text"].replace("\n", "<br>").replace("```python", '<pre style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;color:#a5f3fc;font-size:12px;overflow-x:auto;">').replace("```", "</pre>").replace("**", "<b>").replace("**", "</b>")
        chat_html += f'<div class="msg-bot">{text}</div>'
    else:
        chat_html += f'<div class="msg-label-user">Aap 👤</div>'
        chat_html += f'<div class="msg-user">{msg["text"]}</div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)


# ─── Suggestion Buttons ─────────────────────────────────────────────────────────
st.markdown("**💡 Quick Questions:**")
cols = st.columns(3)
for i, sug in enumerate(SUGGESTIONS):
    with cols[i % 3]:
        if st.button(sug, key=f"sug_{i}"):
            st.session_state.messages.append({"role": "user", "text": sug})
            response = get_response(sug)
            st.session_state.messages.append({"role": "bot", "text": response})
            st.rerun()


# ─── Input Box ─────────────────────────────────────────────────────────────────
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
    st.session_state.messages.append({"role": "user", "text": user_input.strip()})
    response = get_response(user_input.strip())
    st.session_state.messages.append({"role": "bot", "text": response})
    st.rerun()

# Clear Chat
if st.button("🗑️ Chat Clear Karo"):
    st.session_state.messages = [
        {"role": "bot", "text": "Chat clear ho gaya! Dobara start karte hain. Kya poochhna hai? 😊"}
    ]
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<center style='color:rgba(196,181,253,0.5);font-size:12px;'>"
    "Text Mining Chatbot | Sir Shazaib | Built with Python & Streamlit"
    "</center>",
    unsafe_allow_html=True
)
