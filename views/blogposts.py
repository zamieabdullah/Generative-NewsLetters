from flask import Blueprint, jsonify, request
from tasks.blogposts import generate, review, final_draft, html_to_str
from models.model import db
from models.blogposts import BlogPosts
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/create', methods=['GET'])
def create():
    try:
        print("creating blog", flush=True)
        data = generate()
        if data == None: return "<h1>Error 500</h1>"
        print("creating suggestions", flush=True)

        suggestions = review(data)
        if suggestions == None: return "<h1>Error 500</h1>"
        print("creating final draft", flush=True)
        final = final_draft(data, suggestions)
        if final == None: return "<h1>Error 500</h1>"
        print("created final draft", flush=True)
        
        post = BlogPosts(
            url=final["url"],
            title=final["title"],
            content=final["content"]
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
    allPosts = BlogPosts.query.order_by(desc(BlogPosts.created_at)).all()

    response = {}
    blogs = []
    for post in allPosts:
        contents = {
            "title": post.title,
            "url": post.url,
            "timedate": post.created_at.strftime('%B %d, %Y'),
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
    if (url == None or url == "") and request.args.get('url'):
        blog_url = request.args.get('url')
    else:
        blog_url = url

    post = BlogPosts.query.filter_by(url=blog_url).first()

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
