import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from io import BytesIO
import tempfile
import os

def generar_pdf(texto):
    # Crear un buffer en memoria para el PDF
    buffer = BytesIO()
    
    # Configurar el tamaño de la etiqueta: 4x3 pulgadas
    ancho = 4 * inch
    alto = 3 * inch
    
    c = canvas.Canvas(buffer, pagesize=(ancho, alto))
    
    # 1. Generar la imagen del código de barras
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        # Usamos ImageWriter para que genere una imagen limpia sin texto abajo
        options = {'write_text': False}
        barcode = Code128(texto, writer=ImageWriter())
        barcode.save(tmp.name[:-4], options=options)
        path_imagen = tmp.name
    
    # --- MODIFICACIONES DE ESPACIO AQUÍ ---
    
    # Definimos alturas para mantener el codigo limpio
    altura_barcode = 1.5 * inch
    posicion_y_barcode = 1.1 * inch  # Subimos el barcode (antes estaba en 0.5)
    posicion_y_texto = 0.4 * inch    # Posicionamos el texto abajo
    
    # 2. Dibujar el código de barras (Subido)
    # drawImage(path, x, y, width, height)
    # La 'y' determina dónde empieza la parte de abajo de la imagen
    c.drawImage(path_imagen, 0.5 * inch, posicion_y_barcode, width=3 * inch, height=altura_barcode)
    
    # 3. Dibujar el texto (Centrado abajo con espacio)
    c.setFont("Courier-Bold", 18) # Usé Courier para que parezca más "código"
    # drawCentredString(x_centro, y_base, texto)
    c.drawCentredString(ancho / 2, posicion_y_texto, texto)
    
    # --------------------------------------
    
    c.showPage()
    c.save()
    
    # Limpiar el archivo temporal
    if os.path.exists(path_imagen):
        os.remove(path_imagen)
        
    buffer.seek(0)
    return buffer

# --- INTERFAZ DE STREAMLIT (Sin cambios) ---
st.set_page_config(page_title="Generador de Etiquetas", page_icon="🏷️")
st.title("🏷️ Generador de Etiquetas 4x3")

with st.container():
    texto_input = st.text_input("Introduce el texto o código:", placeholder="Ej. LUIS-12345")
    boton_generar = st.button("Generar Etiqueta")

if boton_generar:
    if texto_input:
        with st.spinner('Generando PDF...'):
            pdf_data = generar_pdf(texto_input)
            st.success("¡Etiqueta generada con éxito! Revisa el PDF.")
            st.download_button(
                label="⬇️ Descargar Etiqueta PDF",
                data=pdf_data,
                file_name=f"etiqueta_{texto_input}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Por favor, ingresa un texto.")