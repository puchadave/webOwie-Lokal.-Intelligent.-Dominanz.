from flask import Blueprint, request, jsonify, render_template, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from lxml import etree

db = SQLAlchemy()

accounting_bp = Blueprint('accounting', __name__, template_folder='templates')


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(256))
    buyer = db.Column(db.String(256))
    issue_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date)
    currency = db.Column(db.String(8), default='EUR')
    status = db.Column(db.String(32), default='draft')
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InvoiceLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    description = db.Column(db.String(512))
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    level = db.Column(db.Integer, default=1)
    sent_at = db.Column(db.DateTime)
    text = db.Column(db.Text)



def ai_categorize_transaction(text):
    ai_engine = os.environ.get('AI_ENGINE', 'gemini').lower()
    prompt = f"Kategorisiere diese Transaktion: {text}"
    if ai_engine == 'openai':
        try:
            from utils.openai_client import OpenAIClient
            client = OpenAIClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'
    elif ai_engine == 'ollama':
        try:
            from utils.ollama_client import OllamaClient
            client = OllamaClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'
    else:
        try:
            from utils.gemini_client import GeminiClient
            client = GeminiClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'



def ai_generate_dunning_text(invoice, reminder_level):
    ai_engine = os.environ.get('AI_ENGINE', 'gemini').lower()
    prompt = f"Schreibe einen Mahntext für Rechnung {invoice.id} (Stufe {reminder_level}), fällig am {invoice.due_date}."
    if ai_engine == 'openai':
        try:
            from utils.openai_client import OpenAIClient
            client = OpenAIClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'
    elif ai_engine == 'ollama':
        try:
            from utils.ollama_client import OllamaClient
            client = OllamaClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'
    else:
        try:
            from utils.gemini_client import GeminiClient
            client = GeminiClient()
            return client.generate(prompt)
        except Exception as e:
            return f'AI error: {e}'


@accounting_bp.route('/')
def invoices_list():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoices.html', invoices=invoices)


@accounting_bp.route('/create', methods=['POST'])
def create_invoice():
    data = request.get_json() or {}
    inv = Invoice(
        seller=data.get('seller', 'Seller Ltd'),
        buyer=data.get('buyer', 'Buyer GmbH'),
        issue_date=datetime.strptime(data.get('issue_date'), '%Y-%m-%d').date() if data.get('issue_date') else date.today(),
        due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date() if data.get('due_date') else date.today(),
        currency=data.get('currency', 'EUR'),
        status=data.get('status', 'draft')
    )
    db.session.add(inv)
    db.session.commit()
    return jsonify({'id': inv.id}), 201


@accounting_bp.route('/<int:invoice_id>', methods=['GET'])
def invoice_detail(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    lines = InvoiceLine.query.filter_by(invoice_id=invoice_id).all()
    return render_template('invoice_detail.html', invoice=inv, lines=lines)


@accounting_bp.route('/<int:invoice_id>/lines', methods=['POST'])
def add_invoice_line(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    data = request.get_json() or {}
    line = InvoiceLine(
        invoice_id=invoice_id,
        description=data.get('description', ''),
        quantity=float(data.get('quantity', 1)),
        unit_price=float(data.get('unit_price', 0)),
    )
    db.session.add(line)
    # Update invoice total
    inv.total = (inv.total or 0.0) + line.quantity * line.unit_price
    db.session.commit()
    return jsonify({'line_id': line.id}), 201


def invoice_to_dict(inv):
    lines = InvoiceLine.query.filter_by(invoice_id=inv.id).all()
    return {
        'id': inv.id,
        'seller': inv.seller,
        'buyer': inv.buyer,
        'issue_date': inv.issue_date.isoformat() if inv.issue_date else None,
        'due_date': inv.due_date.isoformat() if inv.due_date else None,
        'currency': inv.currency,
        'total': inv.total,
        'lines': [{'description': l.description, 'quantity': l.quantity, 'unit_price': l.unit_price} for l in lines]
    }


def save_einvoice_xml(invoice, path):
    root = etree.Element('Invoice')
    seller = etree.SubElement(root, 'Seller')
    seller.text = invoice.get('seller')
    buyer = etree.SubElement(root, 'Buyer')
    buyer.text = invoice.get('buyer')
    issue = etree.SubElement(root, 'IssueDate')
    issue.text = invoice.get('issue_date')
    due = etree.SubElement(root, 'DueDate')
    due.text = invoice.get('due_date')
    lines_el = etree.SubElement(root, 'InvoiceLines')
    for idx, l in enumerate(invoice.get('lines', []), start=1):
        li = etree.SubElement(lines_el, 'InvoiceLine', id=str(idx))
        desc = etree.SubElement(li, 'Description')
        desc.text = l.get('description')
        qty = etree.SubElement(li, 'Quantity')
        qty.text = str(l.get('quantity'))
        up = etree.SubElement(li, 'UnitPrice')
        up.text = str(l.get('unit_price'))
    total_el = etree.SubElement(root, 'Total')
    total_el.text = str(invoice.get('total', 0.0))

    tree = etree.ElementTree(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')


@accounting_bp.route('/<int:invoice_id>/einvoice', methods=['GET'])
def generate_einvoice(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    inv_dict = invoice_to_dict(inv)
    out_dir = current_app.config.get('EINVOICE_PATH', 'storage/einvoices')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'invoice_{inv.id}.xml')
    save_einvoice_xml(inv_dict, path)
    return send_file(path, mimetype='application/xml', as_attachment=True)


def render_invoice_html(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    lines = InvoiceLine.query.filter_by(invoice_id=invoice_id).all()
    # Placeholder render; PDF generation could be added here
    return render_template('invoice_detail.html', invoice=inv, lines=lines)


def run_dunning_cycle():
    today = date.today()
    overdue = Invoice.query.filter(Invoice.due_date < today, Invoice.status != 'paid').all()
    reminders = []
    for inv in overdue:
        reminder = Reminder(invoice_id=inv.id, level=1, sent_at=datetime.utcnow(), text=ai_generate_dunning_text(inv, 1))
        db.session.add(reminder)
        reminders.append(reminder)
    db.session.commit()
    return reminders


@accounting_bp.route('/run_dunning', methods=['POST'])
def run_dunning_endpoint():
    # Protect this endpoint: only users with 'run_dunning' permission may trigger
    try:
        from users import current_user, user_has_permission
    except Exception:
        # if users module not available, deny for safety
        return "Forbidden", 403

    u = current_user()
    if not user_has_permission(u, 'run_dunning'):
        return "Forbidden: missing permission 'run_dunning'", 403

    reminders = run_dunning_cycle()
    return jsonify({'created': len(reminders)})
