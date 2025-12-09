import streamlit as st
from PIL import Image
import requests
import io
import time
import os

# 🚀 URL Cloud Run de ton API
FLASK_URL = "https://imgsysemb-981732829562.us-central1.run.app/segment"

# Dossier optionnel contenant des images de test
IMAGE_DIR = "images"

st.set_page_config(page_title="Segmentation d'image", layout="wide")
st.title("Segmentation d'image")

# ===============================
# 🎚️ Barre latérale : sélection ou upload
# ===============================
st.sidebar.header("📁 Sélection d'image")

# Liste des images locales disponibles
images = []
if os.path.exists(IMAGE_DIR):
    images = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

selected_image = st.sidebar.selectbox(
    "Choisissez une image existante :", ["(Aucune)"] + images
)

uploaded_file = st.sidebar.file_uploader(
    "Ou télécharger votre image :", type=["png", "jpg", "jpeg"]
)

run_button = st.sidebar.button("Lancer la segmentation")

# ===============================
# 🔍 Chargement de l'image choisie
# ===============================
image = None

if uploaded_file is not None:
    # L'image uploadée a priorité
    image = Image.open(uploaded_file).convert("RGB")

elif selected_image != "(Aucune)":
    image_path = os.path.join(IMAGE_DIR, selected_image)
    image = Image.open(image_path).convert("RGB")


# ===============================
# 🚀 Si une image est sélectionnée : l'afficher
# ===============================
if image is not None:
    st.subheader("Image à segmenter")
    st.image(image, width=350)

# ===============================
# 🚀 Lancer la segmentation
# ===============================
if run_button:
    if image is None:
        st.error("Veuillez d'abord sélectionner ou télécharger une image.")
        st.stop()

    with st.spinner("Segmentation en cours..."):
        start_time = time.time()

        # Convertir en bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        try:
            # Envoi à l’API Cloud Run
            response = requests.post(
                FLASK_URL,
                files={"image": ("image.png", img_bytes, "image/png")},
                timeout=300
            )

            inference_time = time.time() - start_time

            if response.status_code == 200:
                mask_img = Image.open(io.BytesIO(response.content))

                st.success(f"✨ Segmentation terminée en {inference_time:.2f} secondes")

                # ===============================
                # 🖼️ Affichage côte à côte
                # ===============================
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Image originale")
                    st.image(image, use_container_width=True)

                with col2:
                    st.subheader("Masque segmenté")
                    st.image(mask_img, use_container_width=True)

            else:
                st.error(f"Erreur API : {response.status_code}")
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ Impossible de contacter l'API : {e}")
