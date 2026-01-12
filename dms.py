from flask import Blueprint, request, current_app, render_template, send_file, url_for, redirect
from werkzeug.utils import secure_filename
from accounting import db
from datetime import datetime
import os
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

dms_bp = Blueprint('dms', __name__, template_folder='templates')


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(512))
    filepath = db.Column(db.String(1024))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    mime_type = db.Column(db.String(128))
    ocr_text = db.Column(db.Text)


@dms_bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return 'No file uploaded', 400
        filename = secure_filename(file.filename)
        storage_root = current_app.config.get('DOCUMENT_STORAGE', 'storage/documents')
        os.makedirs(storage_root, exist_ok=True)
        save_path = os.path.join(storage_root, filename)
        file.save(save_path)

        doc = Document(filename=filename, filepath=save_path, mime_type=file.mimetype)
        # Optional OCR
        if OCR_AVAILABLE:
            try:
                text = pytesseract.image_to_string(Image.open(save_path))
                doc.ocr_text = text
            except Exception:
                doc.ocr_text = None

        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('dms.list_documents'))
    return render_template('documents.html')


@dms_bp.route('/', methods=['GET'])
def list_documents():
    docs = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template('documents.html', documents=docs)


@dms_bp.route('/download/<int:doc_id>', methods=['GET'])
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_file(doc.filepath, as_attachment=True, download_name=doc.filename)
