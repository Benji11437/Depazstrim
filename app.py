from flask import Flask, request, render_template_string
from PIL import Image
import io
import requests
import base64  # 🔑 important pour encoder correctement en base64

app = Flask(__name__)

# 🔥 URL Cloud Run de ton API de segmentation
FLASK_URL = "https://imgsysemb-981732829562.us-central1.run.app/segment"

# Template HTML simple pour uploader l'image et afficher le masque
HTML_TEMPLATE = """
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8">
    <title>Segmentation d'image</title>
  </head>
  <body>
    <h1>Segmentation d'image</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="image" accept="image/*" required>
      <input type="submit" value="Segmenter">
    </form>

    {% if original %}
      <h2>Image originale</h2>
      <img src="{{ original }}" width="400">
    {% endif %}

    {% if mask %}
      <h2>Masque segmenté</h2>
      <img src="{{ mask }}" width="400">
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    original_data = None
    mask_data = None

    if request.method == "POST" and "image" in request.files:
        file = request.files["image"]
        img = Image.open(file.stream).convert("RGB")

        # Convertir l'image originale en base64 pour affichage
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        original_data = "data:image/png;base64," + base64.b64encode(img_bytes.getvalue()).decode()

        # Envoyer l'image à l'API Cloud Run
        try:
            # On remet le curseur au début avant l'envoi
            img_bytes.seek(0)
            response = requests.post(
                FLASK_URL,
                files={"image": ("image.png", img_bytes, "image/png")},
                timeout=300
            )
            if response.status_code == 200:
                mask_img = Image.open(io.BytesIO(response.content))
                mask_bytes = io.BytesIO()
                mask_img.save(mask_bytes, format="PNG")
                mask_bytes.seek(0)
                mask_data = "data:image/png;base64," + base64.b64encode(mask_bytes.getvalue()).decode()
            else:
                return f"Erreur API : {response.status_code}<br>{response.text}"
        except Exception as e:
            return f"Impossible de contacter l'API : {e}"

    return render_template_string(HTML_TEMPLATE, original=original_data, mask=mask_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)