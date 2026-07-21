import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF, HTMLMixin
import tempfile
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Reporte 360°", page_icon="📈", layout="centered")

# --- 2. MOSTRAR LOGO EN LA PÁGINA WEB ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)

st.title("📈 Generador de Clima Laboral 360°")
st.write("Sube tu archivo de respuestas para generar el reporte estratégico.")

# --- 3. INTERFAZ PARA SUBIR ARCHIVOS ---
archivo_subido = st.file_uploader("Sube el archivo CSV de Google Forms", type=["csv"])

# --- 4. DICCIONARIO ESTRATÉGICO ---
diccionario_recomendaciones = {
    "Liderazgo": "Actividad: Sesiones de mentoría 1 a 1.\nEstrategia: Programa 'Líder Sombra' para observar y corregir actitudes en piso.",
    "Com. Asertiva": "Actividad: Taller práctico de comunicación no violenta.\nEstrategia: Breves reuniones de inicio de turno (5 min) para alinear objetivos.",
    "Toma Decisiones": "Actividad: Simuladores de casos reales en sucursal.\nEstrategia: Fomentar el uso de árboles de decisión para problemas operativos comunes.",
    "Int. Emocional": "Actividad: Taller de manejo de estrés y empatía.\nEstrategia: Creación de un 'espacio seguro' para feedback sin represalias.",
    "Resultados": "Actividad: Revisión semanal de KPIs operativos.\nEstrategia: Tableros visuales de metas alcanzadas en áreas comunes (competencia sana).",
    "Trabajo en Equipo": "Actividad: Dinámicas de team building mensuales.\nEstrategia: Metas compartidas entre Cajas y Piso para forzar colaboración interdepartamental.",
    "Enfoque Cliente": "Actividad: Role-play de atención a clientes difíciles.\nEstrategia: Reconocimiento público al 'Empleado del Mes' basado en encuestas de salida.",
    "Gestion RRHH": "Actividad: Capacitación en liderazgo motivacional y retención.\nEstrategia: Encuestas de pulso quincenales para medir el ánimo y forzar retroalimentación.",
    "Aprendizaje Agil": "Actividad: Sesiones de 'Lecciones Aprendidas' post-errores.\nEstrategia: Rotación temporal de puestos para entender la operación integral."
}

class MyFPDF(FPDF, HTMLMixin):
    pass

# --- 5. FUNCIÓN PARA LIMPIAR TEXTOS ---
def san(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# --- 6. GENERACIÓN DEL DOCUMENTO ---
def generar_pdf_completo(df_competencias, top_3, bottom_3, comentarios, lowest_3_comps):
    means_sorted = df_competencias.mean().round(2).sort_values(ascending=True)
    
    # Gráfica Lollipop Minimalista
    plt.figure(figsize=(8, 4.5))
    colors = ['#E76F51' if val < 2.35 else '#F4A261' if val < 2.45 else '#2A9D8F' for val in means_sorted.values]
    
    plt.hlines(y=means_sorted.index, xmin=1.5, xmax=means_sorted.values, color='#DDDDDD', linewidth=4, zorder=1)
    plt.scatter(means_sorted.values, means_sorted.index, s=300, color=colors, zorder=2)
    
    for i, val in enumerate(means_sorted.values):
        plt.text(val + 0.05, i, f'{val:.2f}', va='center', fontsize=11, fontweight='bold', color='#333333')
        
    plt.xlim(1.5, 3.2)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_color('#E0E0E0')
    plt.tick_params(axis='y', length=0, labelsize=11)
    plt.tick_params(axis='x', colors='#777777')
    plt.tight_layout()
    
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_img.name, dpi=200, transparent=True, bbox_inches='tight')
    plt.close()

    # Construcción del PDF
    pdf = MyFPDF()
    pdf.set_margins(15, 15, 15) # Asegura márgenes estrictos
    pdf.set_auto_page_break(auto=True, margin=15) 
    pdf.add_page()
    
    # Encabezado Rojo Oficial
    pdf.set_fill_color(192, 0, 0)
    pdf.rect(0, 0, 210, 35, 'F')
    
    # Cursor explícito al inicio
    pdf.set_xy(15, 12)
    pdf.set_font("Arial", style="B", size=22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, san("Reporte Clima Laboral 360°"), align="C", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 6, san("Análisis de Desempeño por Competencias"), align="C", ln=True)
    
    y_actual = 40 
    
    # Insertar Logo en el PDF automáticamente
    if os.path.exists('logo.png'):
        w_logo = 40
        x_logo = (210 - w_logo) / 2 
        pdf.image('logo.png', x=x_logo, y=y_actual, w=w_logo) 
        y_actual += 25 
    
    # Insertar Gráfica
    pdf.image(temp_img.name, x=15, y=y_actual, w=180)
    
    # ====== FIX CRÍTICO DEL ERROR ======
    # Resetea de forma obligatoria el cursor a la izquierda y debajo de la gráfica
    pdf.set_xy(15, y_actual + 110) 
    # ===================================
    
    # Título Análisis Detallado
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0) 
    pdf.cell(0, 10, san("Análisis Detallado por Competencia"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    means_original = df_competencias.mean().round(2)
    labels_original = df_competencias.columns
    
    # Textos Analíticos
    for comp in labels_original:
        score = means_original[comp]
        if score >= 2.45:
            color, estado, texto = (42, 157, 143), "FORTALEZA", f"Sobresale en {comp}."
        elif score >= 2.35:
            color, estado, texto = (244, 162, 97), "EN DESARROLLO", f"Nivel funcional en {comp}."
        else:
            color, estado, texto = (231, 111, 81), "AREA CRITICA", f"ALERTA en {comp}."
            
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(100, 5, san(comp), ln=0)
        
        pdf.set_font("Arial", style="B", size=10)
        pdf.set_text_color(*color)
        pdf.cell(0, 5, san(f"{score:.2f} / 3.0 ({estado})"), ln=True, align="R")
        
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 4.5, san(f"Análisis: {texto}"))
        pdf.ln(2)

    # --- PÁGINA 2 ---
    pdf.add_page()
    
    # Ranking
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0)
    pdf.cell(0, 10, san("Ranking de Personal"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=11)
    pdf.set_text_color(42, 157, 143)
    pdf.cell(100, 8, san("Top 3 - Mejores Evaluados"), ln=0)
    pdf.set_text_color(231, 111, 81)
    pdf.cell(0, 8, san("Top 3 - Áreas de Oportunidad"), ln=True)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(50, 50, 50)
    for top, bot in zip(top_3.iterrows(), bottom_3.iterrows()):
        n_top = " ".join(top[1]['Selecciona el nombre del evaluado'].split()[:2]).title()
        n_bot = " ".join(bot[1]['Selecciona el nombre del evaluado'].split()[:2]).title()
        pdf.cell(100, 6, san(f"* {n_top} - {top[1]['mean']:.2f}"), ln=0)
        pdf.cell(0, 6, san(f"* {n_bot} - {bot[1]['mean']:.2f}"), ln=True)

    pdf.ln(10)
    
    # Plan de Acción
    pdf.set_fill_color(250, 240, 240)
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0) 
    pdf.cell(0, 10, san("Plan de Acción Estratégico"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, san("Acciones sugeridas para las áreas críticas detectadas:"), ln=True)
    pdf.ln(2)
    
    for comp in lowest_3_comps:
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(231, 76, 60)
        pdf.cell(0, 6, san(f"Objetivo: {comp}"), ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(50, 50, 50)
        recomendacion = diccionario_recomendaciones.get(comp, "Reforzar capacitación y seguimiento constante.")
        for linea in recomendacion.split('\n'):
            pdf.multi_cell(0, 5, san(f"- {linea}"))
        pdf.ln(3)
        
    pdf.ln(5)
    
    # Comentarios
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0)
    pdf.cell(0, 10, san("Voces del Equipo"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Arial", style="I", size=9)
    pdf.set_text_color(80, 80, 80)
    for c in comentarios:
        pdf.multi_cell(0, 5, san(f'"{c}"'))
        pdf.ln(2)

    os.remove(temp_img.name)
        
    return pdf.output(dest='S').encode('latin1')

# --- 7. PROCESAMIENTO PRINCIPAL ---
if archivo_subido is not None:
    try:
        df = pd.read_csv(archivo_subido)
        col_nombres = 'Selecciona el nombre del evaluado'
        columnas_competencias = df.columns[5:14]
        
        nombres_cortos = [
            "Liderazgo", "Com. Asertiva", "Toma Decisiones", 
            "Int. Emocional", "Resultados", "Trabajo en Equipo", 
            "Enfoque Cliente", "Gestion RRHH", "Aprendizaje Agil"
        ]
        
        df_competencias = df[columnas_competencias].copy()
        df_competencias.columns = nombres_cortos
        
        df['Promedio_General'] = df_competencias.mean(axis=1)
        agrupado = df.groupby(col_nombres)['Promedio_General'].agg(['mean', 'count']).reset_index()
        agrupado_ordenado = agrupado.sort_values(by='mean', ascending=False)
        top_3 = agrupado_ordenado.head(3)
        bottom_3 = agrupado_ordenado.tail(3).sort_values(by='mean', ascending=True)
        
        lowest_3_comps = df_competencias.mean().sort_values().head(3).index.tolist()
        
        comentarios_raw = df.iloc[:, 14].dropna().tolist()
        comentarios_validos = [str(c).strip() for c in comentarios_raw if len(str(c).strip()) > 10]
        comentarios_muestra = comentarios_validos[:4] if len(comentarios_validos) >= 4 else comentarios_validos

        # Ejecutamos el creador de PDF
        pdf_bytes = generar_pdf_completo(df_competencias, top_3, bottom_3, comentarios_muestra, lowest_3_comps)
        
        st.success(f"¡Reporte generado! Listo para descargar.")
        st.download_button("📄 Descargar Reporte Final (PDF)", data=pdf_bytes, file_name="Reporte_Clima_Laboral.pdf", mime="application/pdf")
        
    except Exception as e:
        st.error(f"Error procesando el archivo. Verifica el CSV. Detalle técnico: {e}")