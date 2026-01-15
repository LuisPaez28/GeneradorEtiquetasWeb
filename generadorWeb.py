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
    # ReportLab usa puntos (1 pulgada = 72 puntos)
    ancho = 4 * inch
    alto = 3 * inch
    
    c = canvas.Canvas(buffer, pagesize=(ancho, alto))
    
    # 1. Generar la imagen del código de barras
    # Usamos Code128 que es estándar para texto alfanumérico
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        barcode = Code128(texto, writer=ImageWriter())
        barcode.save(tmp.name[:-4]) # La librería añade .png automáticamente
        path_imagen = tmp.name
    
    # 2. Dibujar en el PDF
    # Colocar el texto arriba
    c.setFont("Helvetica-Bold", 14)
    # c.drawCentredString(ancho / 2, alto - 0.5 * inch, f"Producto: {texto}")
    
    # Colocar la imagen del código de barras
    # drawImage(path, x, y, width, height)
    c.drawImage(path_imagen, 0.5 * inch, 0.5 * inch, width=3 * inch, height=1.5 * inch)
    
    c.showPage()
    c.save()
    
    # Limpiar el archivo temporal
    if os.path.exists(path_imagen):
        os.remove(path_imagen)
        
    buffer.seek(0)
    return buffer

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Generador de Etiquetas", page_icon="🏷️")

st.title("🏷️ Generador de Etiquetas QR/Barcode")
st.markdown("Crea etiquetas de **4x3 pulgadas** listas para imprimir.")

with st.container():
    texto_input = st.text_input("Introduce el texto o código:", placeholder="Ej. PRODUCTO-001")
    boton_generar = st.button("Generar Etiqueta")

if boton_generar:
    if texto_input:
        with st.spinner('Generando PDF...'):
            pdf_data = generar_pdf(texto_input)
            
            # Mostrar vista previa (opcional) y botón de descarga
            st.success("¡Etiqueta generada con éxito!")
            
            st.download_button(
                label="⬇️ Descargar Etiqueta PDF",
                data=pdf_data,
                file_name=f"etiqueta_{texto_input}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Por favor, ingresa un texto para el código.")