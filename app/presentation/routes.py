from app.services.post import PostService
from flask import Blueprint, jsonify, request

from app.infrastructure.repositories.post import PostRepository
from app.infrastructure.database import get_session

post_blueprint = Blueprint("posts", __name__)
post_service = PostService(PostRepository())


@post_blueprint.route("/posts", methods=["GET"])
def get_posts():
    posts = post_service.get_all_posts()
    return jsonify([post.dict() for post in posts]), 200


@post_blueprint.route("/posts/<int:post_id>", methods=["GET"])
async def get_post(post_id):
    async with get_session() as session:
        user_service = PostService(session)
        post = await user_service.get_post_by_slug(id=post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post.dict()), 200


@post_blueprint.route("/posts", methods=["POST"])
def create_post():
    data = request.json
    if (
        not data
        or "title" not in data
        or "content" not in data
        or "author_id" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    post = post_service.create_post(data["title"], data["content"], data["author_id"])
    return jsonify(post.dict()), 201


@post_blueprint.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.json
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    updated_post = post_service.update_post(post_id, data["title"], data["content"])
    if updated_post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(updated_post.dict()), 200


@post_blueprint.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    success = post_service.delete_post(post_id)
    if not success:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"message": "Post deleted"}), 200
