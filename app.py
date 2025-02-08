from flask import Flask, render_template, request, send_file
import qrcode
import os
import re

app = Flask(__name__)

# QR kodları saxlayacağımız qovluğu yaradırıq
QR_FOLDER = "static/qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)

def sanitize_filename(text):
    """Fayl adı üçün keçərli simvolları saxlayır"""
    return re.sub(r'[<>:"/\\|?*]', "_", text)[:30]  # 30 simvolla məhdudlaşdırır

@app.route("/", methods=["GET", "POST"])
def index():
    qr_codes = {}

    if request.method == "POST":
        qr_name = request.form.get("qr_name", "").strip()  # Adı götür
        data = request.form["data"]
        box_size = int(request.form.get("box_size", 10))
        border = int(request.form.get("border", 4))
        fill_color = request.form.get("fill_color", "#000000")
        back_color = request.form.get("back_color", "#ffffff")

        # Fayl adı üçün icazəli versiyanı yaradırıq
        key = sanitize_filename(qr_name if qr_name else data)  # Əgər istifadəçi ad yazmayıbsa, data istifadə olunur
        file_path = os.path.join(QR_FOLDER, f"{key}.png")

        # QR kodu yaradıb yadda saxlayırıq
        qr = qrcode.QRCode(box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(file_path)

        qr_codes[key] = file_path

    # QR kodları göstərmək üçün siyahını qaytarırıq
    qr_files = {file[:-4]: os.path.join(QR_FOLDER, file) for file in os.listdir(QR_FOLDER)}
    return render_template("index.html", qr_codes=qr_files)

@app.route("/download/<key>")
def download_qr(key):
    file_path = os.path.join(QR_FOLDER, f"{key}.png")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{key}.png")
    else:
        return "QR kod tapılmadı!", 404

if __name__ == "__main__":
    app.run(debug=True)
