import io
import os
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
from docx2pdf import convert
import tempfile

def generar_pdf_desde_plantilla(solicitud):
    """
    Genera un PDF basado en una plantilla y datos proporcionados.
    Esta es una implementación básica. Para una solución más completa,
    considera usar bibliotecas como WeasyPrint, xhtml2pdf o docxtpl.
    """
    plantilla = solicitud.plantilla
    datos = solicitud.datos_documento
    
    # Determinar el tipo de plantilla y procesarla adecuadamente
    if plantilla.archivo.name.endswith('.docx'):
        return generar_desde_docx(plantilla, datos, solicitud)
    else:
        # Implementación básica para otros tipos de plantillas
        return generar_pdf_basico(plantilla, datos, solicitud)

def generar_desde_docx(plantilla, datos, solicitud):
    """
    Genera un PDF a partir de una plantilla DOCX, reemplazando marcadores
    con los datos proporcionados.
    """
    # Crear un archivo temporal para el DOCX modificado
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
        temp_docx_path = temp_docx.name
    
    # Crear un archivo temporal para el PDF resultante
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf_path = temp_pdf.name
    
    try:
        # Abrir el documento DOCX
        doc = Document(plantilla.archivo.path)
        
        # Reemplazar marcadores en el texto
        for paragraph in doc.paragraphs:
            for key, value in datos.items():
                if f"{{{{ {key} }}}}" in paragraph.text:
                    paragraph.text = paragraph.text.replace(f"{{{{ {key} }}}}", str(value))
        
        # Guardar el documento modificado
        doc.save(temp_docx_path)
        
        # Convertir DOCX a PDF
        convert(temp_docx_path, temp_pdf_path)
        
        # Guardar el PDF en el modelo
        with open(temp_pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            
        # Generar un nombre de archivo único
        filename = f"{solicitud.plantilla.nombre}_{solicitud.solicitante.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Guardar el archivo en el campo documento_generado
        solicitud.documento_generado.save(filename, ContentFile(pdf_content), save=True)
        
        # Actualizar el estado de la solicitud
        solicitud.estado = 'generado'
        solicitud.fecha_generacion = datetime.now()
        solicitud.save()
        
        return True
    
    finally:
        # Limpiar archivos temporales
        if os.path.exists(temp_docx_path):
            os.unlink(temp_docx_path)
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

def generar_pdf_basico(plantilla, datos, solicitud):
    """
    Genera un PDF básico con los datos proporcionados.
    Esta es una implementación simple para demostración.
    """
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Añadir título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, plantilla.nombre)
    
    # Añadir fecha
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Añadir datos
    y_position = 700
    p.setFont("Helvetica", 12)
    for key, value in datos.items():
        p.drawString(100, y_position, f"{key}: {value}")
        y_position -= 20
    
    # Cerrar el PDF
    p.showPage()
    p.save()
    
    # Generar un nombre de archivo único
    filename = f"{plantilla.nombre}_{solicitud.solicitante.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    
    # Guardar el archivo en el campo documento_generado
    buffer.seek(0)
    solicitud.documento_generado.save(filename, ContentFile(buffer.getvalue()), save=True)
    
    # Actualizar el estado de la solicitud
    solicitud.estado = 'generado'
    solicitud.fecha_generacion = datetime.now()
    solicitud.save()
    
    return True