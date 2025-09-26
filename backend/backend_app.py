from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_by = request.args.get("sort")
    direction = request.args.get("direction")
    results = POSTS.copy()

    if direction and not sort_by:
        return jsonify({"error": "Direction requires a sort field"}), 400

    if direction:
        if direction not in ["asc", "desc"]:
            return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400
        reverse = (direction == "desc")
    else:
        reverse = False

    if sort_by:
        if sort_by not in ["title", "content"]:
            return jsonify({"error": "Invalid sorting criteria. Use 'title' or 'content'."}), 400
        results.sort(key=lambda post: post[sort_by], reverse=reverse)

    return jsonify(results)


@app.route('/api/posts', methods=['POST'])
def add_post():
    if not request.is_json:
        return jsonify({"error": "Content type must be application/json"}), 415

    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    new_id = max((post["id"] for post in POSTS), default=0) + 1
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = None
    for element in POSTS:
        if element["id"] == post_id:
            post = element
            break

    if post is None:
        return jsonify({"error": f"ID {post_id} not found"}), 404

    POSTS.remove(post)

    return jsonify({"message": f"Post with ID {post_id} has been deleted successfully"}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = None
    for element in POSTS:
        if element["id"] == post_id:
            post = element
            break

    if post is None:
        return jsonify({"error": f"ID {post_id} not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Content type must be application/json"}), 415

    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")
    title = title.strip() if isinstance(title, str) else title
    content = content.strip() if isinstance(content, str) else content

    if title is not None:
        post["title"] = title
    if content is not None:
        post["content"] = content

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title = request.args.get("title")
    content = request.args.get("content")
    results = POSTS

    if title:
        results = [element for element in results if title.lower() in element["title"].lower()]
    if content:
        results = [element for element in results if content.lower() in element["content"].lower()]

    return jsonify(results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
