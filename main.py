import streamlit as st
from PIL import Image
import requests
import io
import time

# 🔥 URL Cloud Run de ton API de segmentation
FLASK_URL = "https://imgsysemb-981732829562.us-central1.run.app/segment"

st.set_page_config(page_title="Segmentation d'image", layout="wide")

st.title("🖼️ Segmentation d'image")

# Upload image
uploaded_file = st.file_uploader("Choisissez une image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.subheader("Image originale")
    st.image(image, width=300)

    if st.button("Segmenter l'image"):
        with st.spinner("Segmentation en cours..."):
            # Mesure du temps d'inférence
            start_time = time.time()

            # Préparer l'image en bytes
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

                    st.success(f"Segmentation terminée en {inference_time:.2f} secondes")

                    # 🔥 Affichage côte à côte
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
