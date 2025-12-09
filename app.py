import streamlit as st
from PIL import Image
import requests
import io
import time
import os

# 🚀 URL Cloud Run de ton API
FLASK_URL = "https://imgsysemb-981732829562.us-central1.run.app/segment"

# Dossier contenant des images de test
IMAGE_DIR = "images"
st.markdown(
    """
    <h2 style="text-align:center;">
        Application de segmentation d’images
    </h2>
    """,
    unsafe_allow_html=True
)

# ===============================
# 🎚️ Barre latérale : sélection ou upload
# ===============================
st.sidebar.header("📁 Sélection d'image")

# Liste des images locales
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
    "Ou téléverser votre image :", type=["png", "jpg", "jpeg"]
)

run_button = st.sidebar.button("Lancer la segmentation")

# ===============================
# 🏠 PAGE D’ACCUEIL
# ===============================
if uploaded_file is None and selected_image == "(Aucune)":
    st.image(
        "https://plus.unsplash.com/premium_photo-1676637656166-cb7b3a43b81a?fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8YWklMjB0ZWNobG9neXxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=60&w=3000",
        use_container_width=True
    )

    st.markdown(
        """
        <p style='text-align:center; font-size:20px; color:#555; margin-top:20px;'>
            Téléchargez une image ou choisissez-en une dans la barre latérale 👈
        </p>
        """,
        unsafe_allow_html=True,
    )

# ===============================
# 🔍 Chargement de l'image choisie
# ===============================
image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

elif selected_image != "(Aucune)":
    image_path = os.path.join(IMAGE_DIR, selected_image)
    image = Image.open(image_path).convert("RGB")

# ===============================
# 📌 Afficher l'image si chargée
# ===============================
if image is not None:
    st.subheader("Image à segmenter")
    st.image(image, width=350)

# ===============================
# 🚀 Lancer la segmentation
# ===============================
if run_button:
    if image is None:
        st.error("Veuillez sélectionner ou téléverser une image d'abord.")
        st.stop()

    with st.spinner("Segmentation en cours..."):
        start_time = time.time()

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        try:
            response = requests.post(
                FLASK_URL,
                files={"image": ("image.png", img_bytes, "image/png")},
                timeout=300
            )

            inference_time = time.time() - start_time

            if response.status_code == 200:
                mask_img = Image.open(io.BytesIO(response.content))

                st.success(f"✨ Segmentation terminée en {inference_time:.2f} secondes")

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
