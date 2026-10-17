import os
from db import add_text, collection

for name in os.listdir("data"):
    if not name.endswith((".md", ".txt")):
        continue
    with open("data/" + name, encoding="utf-8") as f:
        text = f.read()
    collection.delete(where={"source": name})
    n = add_text(text, name.replace("_", " "), name)
    print(name, n, "chunks")
