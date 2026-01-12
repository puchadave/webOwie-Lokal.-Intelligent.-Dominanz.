from flask import Blueprint, request, render_template, redirect, url_for, current_app, jsonify
from datetime import datetime
from accounting import db
import os

try:
    from users import login_required, current_user, user_has_permission
except Exception:
    # fallback stubs if users module not yet available
    def login_required(f):
        return f

    def current_user():
        return None

    def user_has_permission(u, name):
        return False

from main import generate_email_content

blog_bp = Blueprint('blog', __name__, template_folder='templates')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    is_vlog = db.Column(db.Boolean, default=False)
    video_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)


@blog_bp.route('/')
def list_posts():
    posts = Post.query.filter_by(is_published=True).order_by(Post.published_at.desc()).all()
    return render_template('blog_list.html', posts=posts)


@blog_bp.route('/admin')
@login_required
def admin_posts():
    u = current_user()
    if not u or getattr(u, 'role', None) != 'admin':
        return "Forbidden", 403
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('blog_admin.html', posts=posts)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    u = current_user()
    if not u or getattr(u, 'role', None) != 'admin':
        return "Forbidden", 403
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug') or title.lower().replace(' ', '-')
        content = request.form.get('content')
        is_vlog = bool(request.form.get('is_vlog'))
        video_url = request.form.get('video_url')
        publish = bool(request.form.get('publish'))

        p = Post(title=title, slug=slug, content=content, is_vlog=is_vlog, video_url=video_url, is_published=publish)
        if publish:
            p.published_at = datetime.utcnow()
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('blog.admin_posts'))
    return render_template('blog_create.html')


@blog_bp.route('/<slug>')
def view_post(slug):
    p = Post.query.filter_by(slug=slug).first_or_404()
    if not p.is_published and (not current_user() or getattr(current_user(), 'role', None) != 'admin'):
        return "Forbidden", 403
    return render_template('blog_view.html', post=p)


@blog_bp.route('/ai_generate', methods=['POST'])
@login_required
def ai_generate_post():
    # Generate a draft post using AI. Requires 'use_ai'.
    try:
        if not user_has_permission(current_user(), 'use_ai'):
            return jsonify({'error': 'Forbidden: missing permission use_ai'}), 403
    except Exception:
        return jsonify({'error': 'Permission system unavailable'}), 500

    data = request.get_json() or {}
    topic = data.get('topic') or data.get('title') or 'Marketing Insights'
    prompt = data.get('prompt') or f'Write a detailed blog post about: {topic}'
    # Reuse the existing AI email generator as a simple content generator
    fake_lead = {'company_name': topic, 'osint_data': {}, 'email_interactions': []}
    gen = generate_email_content(fake_lead, prompt)
    title = data.get('title') or gen.get('subject') or topic
    content = gen.get('body')

    p = Post(title=title, slug=(title.lower().replace(' ', '-')[:200]), content=content, is_published=False)
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'title': p.title, 'preview': content[:200]})


@blog_bp.route('/ai_create_and_post', methods=['POST'])
@login_required
def ai_create_and_post():
    # Create and publish a post automatically. Requires both 'use_ai' and 'auto_post'.
    try:
        u = current_user()
        if not user_has_permission(u, 'use_ai'):
            return jsonify({'error': 'Forbidden: missing permission use_ai'}), 403
        if not user_has_permission(u, 'auto_post'):
            return jsonify({'error': 'Forbidden: missing permission auto_post'}), 403
    except Exception:
        return jsonify({'error': 'Permission system unavailable'}), 500

    data = request.get_json() or {}
    topic = data.get('topic') or 'Automated Post'
    prompt = data.get('prompt') or f'Create a publish-ready blog post about: {topic}'
    fake_lead = {'company_name': topic, 'osint_data': {}, 'email_interactions': []}
    gen = generate_email_content(fake_lead, prompt)
    title = data.get('title') or gen.get('subject') or topic
    content = gen.get('body')

    p = Post(title=title, slug=(title.lower().replace(' ', '-')[:200]), content=content, is_published=True, published_at=datetime.utcnow())
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'title': p.title})


def seed_blog_permissions():
    """Ensure default permissions for blog features exist."""
    try:
        from users import Permission
        defaults = [
            ('use_ai', 'Allow use of AI generation features'),
            ('auto_post', 'Allow automatic publishing of AI-created posts'),
            ('manage_blog', 'Allow manual blog management')
        ]
        for name, desc in defaults:
            if not Permission.query.filter_by(name=name).first():
                p = Permission(name=name, description=desc)
                db.session.add(p)
        db.session.commit()
    except Exception:
        # If users/Permission not available yet, skip quietly
        pass

