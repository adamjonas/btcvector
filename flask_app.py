from flask import Flask, request
from src.utils import query_index, query_index_by_author, connect_to_pinecone_index

pinecone_index = connect_to_pinecone_index()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route("/")
def health_check():
    return "<p>Welcome to Chaincode-Pinecone-Bot</p>"


@app.route("/search", methods=["POST"])
def search_app():
    try:
        query = request.json["query"]
        data = query_index(query, pinecone_index)
        output_data = {"data": data}
        return output_data
    except Exception as e:
        print(str(e))
        error = {"error": str(e)}
        return error


@app.route("/search_by_author", methods=["POST"])
def search_by_author_app():
    try:
        query = request.json["query"]
        author = request.json["author"]
        data = query_index_by_author(query, pinecone_index, author)
        output_data = {"data": data}
        return output_data
    except Exception as e:
        print(str(e))
        error = {"error": str(e)}
        return error


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
