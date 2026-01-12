from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, session
from accounting import db
from datetime import datetime

ecom = Blueprint('ecommerce', __name__, template_folder='templates')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    active = db.Column(db.Boolean, default=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@ecom.route('/')
def product_list():
    products = Product.query.filter_by(active=True).all()
    return render_template('products.html', products=products)


@ecom.route('/<int:product_id>')
def product_detail(product_id):
    p = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=p)


@ecom.route('/<int:product_id>/buy', methods=['GET', 'POST'])
def buy_product(product_id):
    p = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        user_id = session.get('user_id')
        # Create order
        order = Order(user_id=user_id, product_id=p.id, amount=p.price, status='processing')
        db.session.add(order)
        db.session.commit()

        # Payment flow: call configured connector (mock or real)
        try:
            from connectors import get_payment_connector
            provider = current_app.config.get('PAYMENT_PROVIDER') or __import__('os').environ.get('PAYMENT_PROVIDER')
            conn = get_payment_connector(provider)
            resp = conn.send_payment(amount=order.amount, currency='EUR', account_details={'order_id': order.id})
            # mock response handling
            if resp.get('status') in ('success', 'paid', 'scheduled'):
                order.status = 'paid'
            else:
                order.status = 'failed'
        except Exception:
            # fallback to mock-paid for now
            order.status = 'paid'
        db.session.commit()
        return redirect(url_for('ecommerce.order_detail', order_id=order.id))
    return render_template('checkout.html', product=p)


@ecom.route('/order/<int:order_id>')
def order_detail(order_id):
    o = Order.query.get_or_404(order_id)
    return render_template('order_detail.html', order=o)


@ecom.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    # very small admin guard — real app should use proper decorators
    if session.get('user_role') != 'admin':
        return "Forbidden", 403
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        desc = request.form.get('description')
        price = float(request.form.get('price', 0))
        p = Product(name=name, slug=slug, description=desc, price=price, active=True)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('ecommerce.admin_products'))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin_products.html', products=products)
