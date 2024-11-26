# from flask import Flask, render_template, request, redirect, url_for
# from werkzeug.utils import secure_filename
# from PIL import Image
# import pytesseract
# import os

# app = Flask(__name__)

# # Tentukan path ke executable Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Sesuaikan dengan lokasi Tesseract di sistem Anda

# # Folder untuk menyimpan gambar yang diunggah
# UPLOAD_FOLDER = 'upload'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Memeriksa apakah file gambar memiliki ekstensi yang valid
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Fungsi untuk melakukan OCR pada gambar
# def ocr_from_image(image_path):
#     try:
#         # Menggunakan 'with' untuk memastikan gambar ditutup setelah pemrosesan
#         with Image.open(image_path) as img:
#             extracted_text = pytesseract.image_to_string(img, lang='eng')  # Ganti 'eng' dengan bahasa lain jika diperlukan
#         return extracted_text
#     except Exception as e:
#         return f"Error during OCR processing: {e}"

# # Membuat folder upload jika belum ada
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return redirect(request.url)
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return redirect(request.url)
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Proses OCR pada file yang diunggah
#         text = ocr_from_image(filepath)
        
#         # Cobalah menghapus file setelah OCR selesai
#         try:
#             os.remove(filepath)
#         except PermissionError as e:
#             return f"Error deleting file: {e}"
        
#         return render_template('result.html', text=text)
#     else:
#         return 'File tidak valid! Pastikan format file adalah PNG, JPG, atau JPEG.'

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os
import cv2
import numpy as np

app = Flask(__name__)

# Tentukan path ke executable Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Sesuaikan dengan lokasi Tesseract di sistem Anda

# Folder untuk menyimpan gambar yang diunggah
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Memeriksa apakah file gambar memiliki ekstensi yang valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk meningkatkan kualitas gambar
def enhance_image(image_path):
    # Membuka gambar menggunakan PIL
    with Image.open(image_path) as img:
        # Menambah resolusi gambar
        img = img.convert('RGB')  # Pastikan gambar dalam mode RGB
        img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)  # Meningkatkan ukuran gambar
        
        # Menambahkan kontras lebih tinggi
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)  # Meningkatkan kontras 2.5x
        
        # Menambahkan ketajaman (Sharpness)
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(2)  # Meningkatkan ketajaman

        # Mengubah gambar menjadi grayscale (opsional, tetapi sangat disarankan)
        img = img.convert('L')  # Konversi ke grayscale
        
        # Pengaturan Thresholding (Binarisasi) menggunakan threshold yang lebih tinggi
        img = img.point(lambda p: p > 140 and 255)  # Thresholding manual (parameter bisa disesuaikan)
        
        # Menyimpan gambar hasil peningkatan
        img.save(image_path)
    
    return image_path

# Fungsi untuk melakukan OCR pada gambar
def ocr_from_image(image_path):
    try:
        # Meningkatkan kualitas gambar terlebih dahulu
        enhanced_image_path = enhance_image(image_path)
        
        # Menggunakan 'with' untuk memastikan gambar ditutup setelah pemrosesan
        with Image.open(enhanced_image_path) as img:
            extracted_text = pytesseract.image_to_string(img, lang='eng')  # Ganti 'eng' dengan bahasa lain jika diperlukan
        return extracted_text
    except Exception as e:
        return f"Error during OCR processing: {e}"

# Membuat folder upload jika belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Proses OCR pada file yang diunggah
        text = ocr_from_image(filepath)
        
        # Cobalah menghapus file setelah OCR selesai
        try:
            os.remove(filepath)
        except PermissionError as e:
            return f"Error deleting file: {e}"
        
        return render_template('result.html', text=text)
    else:
        return 'File tidak valid! Pastikan format file adalah PNG, JPG, atau JPEG.'

if __name__ == '__main__':
    app.run(debug=True)
