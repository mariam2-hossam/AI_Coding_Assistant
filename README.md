# AI_Coding_Assistant

Run:

    pip install -r requirements.txt
   
    python ingest.py
    streamlit run app.py

- app.py: the chat app (classifier, routing, relevance check, code runner, memory)
- db.py: chunking, embeddings and Chroma
- ingest.py: loads the files in data/ into Chroma
- memory.json is created automatically (chat history + language/framework preference)
