# Simple REST API with Flask

A small tasks API with GET, POST and DELETE, input validation and JSON error messages.
Install with `pip install flask` and run with `python app.py`.

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = []       # in memory storage, replace with a database for real projects
next_id = 1


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id
    data = request.get_json(silent=True)
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    task = {"id": next_id, "title": data["title"], "done": False}
    next_id += 1
    tasks.append(task)
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return jsonify({"deleted": task_id})
    return jsonify({"error": "task not found"}), 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
```
