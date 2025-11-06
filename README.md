# 🩺 Medical Diagnostics GenAI Chatbot

The **Medical Diagnostics GenAI Chatbot** is an advanced, AI-powered healthcare assistant designed to enhance preliminary medical assessments through intelligent, conversational interaction. Built with **Generative AI**, **Retrieval-Augmented Generation (RAG)**, **LangChain**, and **OpenAI’s large language models**, this project provides context-aware and reliable health insights based on user-described symptoms.

---

## 🚀 Features

- 🤖 **Conversational Intelligence:** Engages users in natural, human-like dialogue powered by OpenAI models.  
- 🧠 **RAG-Based Knowledge Retrieval:** Combines generative reasoning with external medical data for accurate, evidence-grounded responses.  
- ⚙️ **LangChain Integration:** Handles prompt orchestration, context management, and dynamic response generation.  
- 🩹 **User-Friendly Interface:** Simple, accessible chat design for seamless user experience.  
- 🔒 **Privacy & Ethics:** Developed following responsible AI and healthcare data protection principles.

---

## 🏗️ Tech Stack

- **Language Models:** OpenAI GPT-based APIs  
- **Framework:** LangChain  
- **Retrieval Pipeline:** RAG (Retrieval-Augmented Generation)  
- **Backend:** Python / FastAPI (optional)  
- **Frontend:** Streamlit or React (customizable)  
- **Database:** Vector database (e.g., FAISS, Pinecone, or Chroma)

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/REHANAHEMAD17/medical-diagnostics-genai-chatbot.git
   cd medical-diagnostics-genai-chatbot

pip install -r requirements.txt

export OPENAI_API_KEY="your_api_key_here"

streamlit run app.py


📘 How It Works

The user inputs symptoms or health concerns via chat.

The system processes the query using LangChain pipelines.

RAG retrieves relevant medical data and knowledge base entries.

OpenAI’s model generates a personalized, contextually accurate response.
