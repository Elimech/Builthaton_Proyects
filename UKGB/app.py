from flask import Flask, request, render_template, url_for, redirect
import os
import networkx as nx
from Ingestion import load_text
from Extraction import extract_relationships
from Graph_Builder import build_graph as create_nx_graph
from Visualization import visualize_graph
from Analysis import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.getcwd(), "static")
GRAPH_FILE = os.path.join(STATIC_DIR, "graph.html")

LAST_TRIPLES = []

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route("/", methods=["GET", "POST"])
def index():
    global LAST_TRIPLES
    show_graph = False
    response_text = None

    if request.method == "GET":
        LAST_TRIPLES = []
        if os.path.exists(GRAPH_FILE):
            try:
                os.remove(GRAPH_FILE) 
            except Exception as e:
                print(f"Error cleaning up at startup: {e}")
        return render_template("index.html", show_graph=False, response=None, graph_ready=False)

    graph_ready = os.path.exists(GRAPH_FILE)

    if request.method == "POST":
        if "create_graph" in request.form:
            text_input = request.form.get("text_input")
            url_input = request.form.get("url")
            file = request.files.get("file")
            
            text = ""
            if text_input: text = text_input
            elif url_input: text = load_text(url=url_input)
            elif file and file.filename != "": text = file.read().decode("utf-8")

            if text:
                LAST_TRIPLES = extract_relationships(text[:8000])
                if LAST_TRIPLES:
                    graph_obj = create_nx_graph(LAST_TRIPLES)
                    visualize_graph(graph_obj)
                    graph_ready = True
                    show_graph = True
                else:
                    response_text = "The AI ​​was unable to process the text. Please try again in a few seconds."

        elif "ask_question" in request.form and graph_ready:
            question = request.form.get("question")
            if question and LAST_TRIPLES:
                graph_obj = create_nx_graph(LAST_TRIPLES)
                response_text = answer_question(graph_obj, question)
                show_graph = True

    return render_template(
        "index.html", 
        show_graph=show_graph or graph_ready, 
        response=response_text,
        graph_ready=graph_ready
    )

@app.route("/reset")
def reset():
    global LAST_TRIPLES
    LAST_TRIPLES = []
    if os.path.exists(GRAPH_FILE):
        try:
            os.remove(GRAPH_FILE)
        except:
            pass
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)