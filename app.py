import os
import re
import json
import subprocess
import sys
import requests
import streamlit as st
from dotenv import load_dotenv
from db import add_text, search

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
URL = "https://openrouter.ai/api/v1/chat/completions"
MEMORY_FILE = "memory.json"

NOT_FOUND = ("I couldn't find relevant knowledge for your request. Could you provide "
             "the correct solution or reference so I can learn it for future interactions?")

languages = ["python", "java", "javascript", "c++", "c#"]
frameworks = ["flask", "django", "fastapi", "pytorch", "tensorflow", "streamlit"]


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"messages": [], "language": "", "framework": ""}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def ask(messages):
    r = requests.post(URL, headers={"Authorization": "Bearer " + str(API_KEY)},
                      json={"model": MODEL, "messages": messages, "temperature": 0}, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"] or ""


def ask_stream(messages):
    r = requests.post(URL, headers={"Authorization": "Bearer " + str(API_KEY)},
                      json={"model": MODEL, "messages": messages, "stream": True},
                      stream=True, timeout=90)
    r.raise_for_status()
    for line in r.iter_lines():
        line = line.decode("utf-8") if line else ""
        if not line.startswith("data:") or "[DONE]" in line:
            continue
        try:
            piece = json.loads(line[5:])["choices"][0]["delta"].get("content")
        except (KeyError, IndexError, ValueError):
            continue
        if piece:
            yield piece


def classify(question):
    answer = ask([
        {"role": "system", "content": "Is the user asking to EXPLAIN existing code or to GENERATE new code? "
                                      "Answer with one word: EXPLAIN or GENERATE."},
        {"role": "user", "content": question},
    ]).upper()
    if "EXPLAIN" in answer and "GENERATE" not in answer:
        return "EXPLAIN"
    return "GENERATE"


def is_relevant(question, context):
    answer = ask([
        {"role": "system", "content": "Is the context useful for the request? Be strict. "
                                      "Answer only RELEVANT or NOT_RELEVANT."},
        {"role": "user", "content": "Request:\n" + question + "\n\nContext:\n" + context},
    ]).strip().upper()
    return answer.startswith("RELEVANT")


def find_preferences(memory, text):
    text = text.lower()
    for lang in languages:
        if lang in text:
            memory["language"] = lang
    for fw in frameworks:
        if fw in text:
            memory["framework"] = fw


def build_messages(system, memory, question):
    if memory["language"]:
        system += " The user prefers " + memory["language"] + "."
    if memory["framework"]:
        system += " The user uses " + memory["framework"] + "."
    messages = [{"role": "system", "content": system}]
    messages += memory["messages"][-10:]
    messages.append({"role": "user", "content": question})
    return messages


def run_code(code):
    with open("temp_code.py", "w", encoding="utf-8") as f:
        f.write(code)
    try:
        r = subprocess.run([sys.executable, "temp_code.py"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=10)
        return r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "", "Timeout: the code ran for more than 10 seconds"


def show_run_buttons(text, i):
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    for j, code in enumerate(blocks):
        key = f"run_{i}_{j}"
        if st.button("Run code", key=key):
            st.session_state.results[key] = run_code(code)
        if key in st.session_state.results:
            out, err = st.session_state.results[key]
            if out:
                st.code(out)
            if err:
                st.error(err)


st.title("AI Coding Assistant")

memory = load_memory()
if "waiting" not in st.session_state:
    st.session_state.waiting = None
if "results" not in st.session_state:
    st.session_state.results = {}

if st.sidebar.button("Clear chat"):
    memory["messages"] = []
    save_memory(memory)
    st.session_state.waiting = None
    st.rerun()

for i, m in enumerate(memory["messages"]):
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m["role"] == "assistant":
            show_run_buttons(m["content"], i)

question = st.chat_input("Ask a programming question")
if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            if st.session_state.waiting and ("```" in question or question.count("\n") >= 3):
                # the user answered our request for a solution, so we learn it
                text = "Question: " + st.session_state.waiting + "\n\nSolution:\n" + question
                add_text(text, st.session_state.waiting[:80], "user_feedback")
                st.session_state.waiting = None
                answer = "Thanks, I saved your solution. Ask me again and I will use it."
                st.write(answer)
            else:
                find_preferences(memory, question)
                if classify(question) == "EXPLAIN":
                    # route 1: no rag
                    system = "You are a programming tutor. Explain the code step by step."
                    answer = st.write_stream(ask_stream(build_messages(system, memory, question)))
                else:
                    # route 2: rag, then relevance check, then the llm
                    query = question
                    old = [m["content"] for m in memory["messages"] if m["role"] == "user"]
                    if len(question.split()) < 6 and old:
                        query = old[-1] + " " + question
                    docs = search(query)
                    context = "\n\n".join(docs)
                    if not docs or not is_relevant(query, context):
                        answer = NOT_FOUND
                        st.write(answer)
                        st.session_state.waiting = question
                    else:
                        system = ("You are a programming assistant. Write complete code in a markdown "
                                  "code block, with comments, error handling and best practices. "
                                  "Use the reference material if it helps.")
                        full = question + "\n\nReference material:\n" + context
                        answer = st.write_stream(ask_stream(build_messages(system, memory, full)))
        except Exception as e:
            answer = "Something went wrong: " + str(e)
            st.error(answer)

    memory["messages"].append({"role": "user", "content": question})
    memory["messages"].append({"role": "assistant", "content": answer})
    save_memory(memory)
    st.rerun()
