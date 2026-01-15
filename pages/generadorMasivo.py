import streamlit as st
import pandas as pd
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from io import BytesIO
import tempfile
import os

def crear_etiqueta_en_pagina(c, texto, ancho, alto):
    """Dibuja una etiqueta en la página actual del canvas."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        options = {'write_text': False, 'module_height': 15.0}
        barcode = Code128(texto, writer=ImageWriter())
        barcode.save(tmp.name[:-4], options=options)
        path_imagen = tmp.name

    # Coordenadas y dimensiones
    posicion_y_barcode = 1.1 * inch
    posicion_y_texto = 0.7 * inch
    
    # Dibujar Barcode
    c.drawImage(path_imagen, 0.5 * inch, posicion_y_barcode, width=3 * inch, height=1.5 * inch)
    
    # Dibujar Texto
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho / 2, posicion_y_texto, str(texto))
    
    # Limpiar imagen temporal
    if os.path.exists(path_imagen):
        os.remove(path_imagen)

def generar_pdf_masivo(lista_datos):
    """Genera un solo PDF con múltiples páginas."""
    buffer = BytesIO()
    ancho = 4 * inch
    alto = 3 * inch
    c = canvas.Canvas(buffer, pagesize=(ancho, alto))
    
    for item in lista_datos:
        if str(item).strip(): # Evitar celdas vacías
            crear_etiqueta_en_pagina(c, str(item), ancho, alto)
            c.showPage() # Crea una nueva página para la siguiente etiqueta
    
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Bulk Label Pro", layout="centered")
st.title("🚀 Generador Masivo de Etiquetas")

tab1, tab2 = st.tabs(["📝 Pegar Lista", "📁 Cargar Archivo"])
lista_final = []

with tab1:
    entrada_texto = st.text_area("Pega aquí tus códigos (uno por línea):", height=200, placeholder="COD-001\nCOD-002\nCOD-003")
    if entrada_texto:
        lista_final = entrada_texto.split('\n')

with tab2:
    archivo_subido = st.file_uploader("Sube un Excel (.xlsx) o CSV", type=['xlsx', 'csv'])
    if archivo_subido:
        try:
            if archivo_subido.name.endswith('.csv'):
                df = pd.read_csv(archivo_subido)
            else:
                df = pd.read_excel(archivo_subido)
            
            columna = st.selectbox("Selecciona la columna que contiene los códigos:", df.columns)
            lista_final = df[columna].tolist()
            st.success(f"Se cargaron {len(lista_final)} registros.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

# --- BOTÓN DE ACCIÓN ---
if lista_final:
    st.divider()
    if st.button(f"Generar {len(lista_final)} Etiquetas"):
        with st.spinner('Procesando lote...'):
            pdf_resultado = generar_pdf_masivo(lista_final)
            st.download_button(
                label="📥 Descargar PDF para Impresión",
                data=pdf_resultado,
                file_name="lote_etiquetas.pdf",
                mime="application/pdf"
            )