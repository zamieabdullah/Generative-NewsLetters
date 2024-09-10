from flask import Blueprint, jsonify
from tasks.blogposts import generate, html_to_str
from models.model import db
from models.blogposts import BlogPosts

bp = Blueprint('routes', __name__)

@bp.route('/create', methods=['GET'])
def create():
    try:
        data = generate()
        
        post = BlogPosts(
            url=data["url"],
            title=data["title"],
            content=data["content"]
        )

        db.session.add(post)
        db.session.commit()

        print("Post saved successfully")

        return data["content"]
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.remove()

@bp.route('/get-titles', methods=['GET'])
def getTitles():
    allPosts = BlogPosts.query.all()
    response = {}
    blogs = []
    for post in allPosts:
        contents = {
            "title": post.title,
            "url": post.url,
            "timedate": post.created_at,
            "content": html_to_str(post.content),
        }

        blogs.append(contents)

    response = {
        "blogs": blogs
    }

    return jsonify(response)

@bp.route('/blogs/<path:url>', methods=['GET'])
def get_post_by_url(url):
    # Query the post with the specific URL
    post = BlogPosts.query.filter_by(url=url).first()

    if post:
        return jsonify({
            "id": post.id,
            "url": post.url,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at
        })
    else:
        return "<h1>Error: Page does not exist</h1>"
