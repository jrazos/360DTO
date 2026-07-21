import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Reporte 360°", page_icon="📈", layout="centered")

# --- 2. MOSTRAR LOGO EN LA PÁGINA WEB ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)

st.title("📈 Generador de Clima Laboral 360°")
st.write("Ingresa los datos del reporte y sube tu archivo CSV para generar el informe ejecutivo.")

# --- 3. INTERFAZ PARA SUCURSAL Y ARCHIVO ---
nombre_sucursal = st.text_input("Ingresa el nombre de la Sucursal (Ej. ZPA, Iztapalapa, Coacalco):", "ZPA")
archivo_subido = st.file_uploader("Sube el archivo CSV de Google Forms", type=["csv"])

# --- 4. DICCIONARIO ESTRATÉGICO DE RECOMENDACIONES ---
diccionario_recomendaciones = {
    "Liderazgo de Apoyo": "Actividad: Sesiones de mentoría 1 a 1.\nEstrategia: Programa 'Líder Sombra' para observar y corregir actitudes en piso.",
    "Comunicación Asertiva": "Actividad: Taller práctico de comunicación no violenta.\nEstrategia: Breves reuniones de inicio de turno (5 min) para alinear objetivos.",
    "Toma de Decisiones": "Actividad: Simuladores de casos reales en sucursal.\nEstrategia: Fomentar el uso de árboles de decisión para problemas operativos comunes.",
    "Inteligencia Emocional": "Actividad: Taller de manejo de estrés y empatía.\nEstrategia: Creación de un 'espacio seguro' para feedback sin represalias.",
    "Orientación a Resultados": "Actividad: Revisión semanal de KPIs operativos.\nEstrategia: Tableros visuales de metas alcanzadas en áreas comunes (competencia sana).",
    "Trabajo en Equipo": "Actividad: Dinámicas de team building mensuales.\nEstrategia: Metas compartidas entre Cajas y Piso para forzar colaboración interdepartamental.",
    "Enfoque al Cliente": "Actividad: Role-play de atención a clientes difíciles.\nEstrategia: Reconocimiento público al 'Empleado del Mes' basado en encuestas de salida.",
    "Gestión de RRHH": "Actividad: Capacitación en liderazgo motivacional y retención.\nEstrategia: Encuestas de pulso quincenales para medir el ánimo y forzar retroalimentación.",
    "Aprendizaje Ágil": "Actividad: Sesiones de 'Lecciones Aprendidas' post-errores.\nEstrategia: Rotación temporal de puestos para entender la operación integral."
}

# --- 5. GENERADOR DE PÁRRAFOS EXPLICATIVOS DETALLADOS ---
def obtener_diagnostico_detallado(competencia, score):
    comp_lower = competencia.lower()
    if score >= 2.45:
        return (
            f"El equipo demuestra un dominio destacado en {comp_lower} con un nivel de desempeño superior al promedio. "
            f"Esta competencia representa una fortaleza sólida en la sucursal, generando un impacto muy positivo en el clima laboral "
            f"y la continuidad operativa. Se recomienda mantener esquemas de reconocimiento e incentivar a los líderes a apadrinar a otros colaboradores."
        )
    elif score >= 2.35:
        return (
            f"Se percibe un desempeño funcional y aceptable en {comp_lower}, aunque existen variaciones entre distintos turnos o puestos. "
            f"Si bien los procesos se ejecutan adecuadamente, persisten áreas de oportunidad para estandarizar conductas. "
            f"Se sugiere dar seguimiento quincenal y realizar breves talleres de alineación para consolidar esta habilidad como pilar del equipo."
        )
    else:
        return (
            f"ALERTA OPERATIVA: La competencia {comp_lower} registra una evaluación crítica que requiere intervención prioritaria. "
            f"La percepción del equipo denota fricciones o inconsistencias que están afectando directamente la dinámica de trabajo y la moral del personal. "
            f"Es urgente implementar el plan de acción sugerido, abrir canales de diálogo directo e involucrar activamente a la gerencia."
        )

# --- 6. FUNCIÓN PARA LIMPIAR TEXTOS (EVITA ERRORES DE CODIFICACIÓN) ---
def san(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# --- 7. GENERACIÓN DEL DOCUMENTO PDF ---
def generar_pdf_completo(df_competencias, top_3, bottom_3, comentarios, lowest_3_comps, sucursal):
    means_sorted = df_competencias.mean().round(2).sort_values(ascending=True)
    
    # 1. Gráfica Lollipop Minimalista
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

    # 2. Inicialización de FPDF
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15) 
    pdf.add_page()
    
    # Encabezado Rojo Oficial con Nombre de Sucursal
    pdf.set_fill_color(192, 0, 0)
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_xy(15, 8)
    pdf.set_font("Arial", style="B", size=20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(180, 10, san(f"Reporte {sucursal.upper()} - Clima Laboral 360°"), align="C", ln=1)
    
    y_actual = 35 
    
    # Inserción de Logo si existe
    if os.path.exists('logo.png'):
        w_logo = 35
        x_logo = (210 - w_logo) / 2 
        pdf.image('logo.png', x=x_logo, y=y_actual, w=w_logo) 
        y_actual += 25 
    
    # Insertar Gráfica
    pdf.image(temp_img.name, x=15, y=y_actual, w=180)
    pdf.set_xy(15, y_actual + 105) 
    
    # Título Sección
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0) 
    pdf.cell(180, 10, san("Análisis Detallado por Competencia"), ln=1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    means_original = df_competencias.mean().round(2)
    labels_original = df_competencias.columns
    
    # Imprimir Análisis con Párrafos Detallados
    for comp in labels_original:
        score = means_original[comp]
        if score >= 2.45:
            color, estado = (42, 157, 143), "FORTALEZA"
        elif score >= 2.35:
            color, estado = (244, 162, 97), "EN DESARROLLO"
        else:
            color, estado = (231, 111, 81), "ÁREA CRÍTICA"
            
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(50, 50, 50)
        pdf.set_x(15)
        pdf.cell(100, 5, san(comp), ln=0)
        
        pdf.set_font("Arial", style="B", size=10)
        pdf.set_text_color(*color)
        pdf.cell(80, 5, san(f"{score:.2f} / 3.0 ({estado})"), ln=1, align="R")
        
        # Párrafo explicativo detallado
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(15) 
        parrafo_explicativo = obtener_diagnostico_detallado(comp, score)
        pdf.multi_cell(180, 4.2, san(f"Diagnóstico: {parrafo_explicativo}"))
        pdf.ln(3)

    # --- PÁGINA DE RANKING Y PLAN DE ACCIÓN ---
    pdf.add_page()
    
    # Ranking
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0)
    pdf.set_x(15)
    pdf.cell(180, 10, san(f"Ranking de Personal - Sucursal {sucursal.upper()}"), ln=1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=11)
    pdf.set_text_color(42, 157, 143)
    pdf.set_x(15)
    pdf.cell(100, 8, san("Top 3 - Mejores Evaluados"), ln=0)
    pdf.set_text_color(231, 111, 81)
    pdf.cell(80, 8, san("Top 3 - Áreas de Oportunidad"), ln=1)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(50, 50, 50)
    for top, bot in zip(top_3.iterrows(), bottom_3.iterrows()):
        n_top = " ".join(top[1]['Selecciona el nombre del evaluado'].split()[:2]).title()
        n_bot = " ".join(bot[1]['Selecciona el nombre del evaluado'].split()[:2]).title()
        pdf.set_x(15)
        pdf.cell(100, 6, san(f"* {n_top} - {top[1]['mean']:.2f}"), ln=0)
        pdf.cell(80, 6, san(f"* {n_bot} - {bot[1]['mean']:.2f}"), ln=1)

    pdf.ln(8)
    
    # Plan de Acción Estratégico
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0) 
    pdf.set_x(15)
    pdf.cell(180, 10, san("Plan de Acción Estratégico"), ln=1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(15)
    pdf.cell(180, 8, san(f"Acciones prioritarias recomendadas para {sucursal.upper()} (Basado en áreas críticas):"), ln=1)
    pdf.ln(2)
    
    for comp in lowest_3_comps:
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(231, 76, 60)
        pdf.set_x(15)
        pdf.cell(180, 6, san(f"Objetivo Prioritario: {comp}"), ln=1)
        
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(50, 50, 50)
        recomendacion = diccionario_recomendaciones.get(comp, "Reforzar capacitación técnica y comunicación constante.")
        for linea in recomendacion.split('\n'):
            pdf.set_x(15)
            pdf.multi_cell(180, 4.5, san(f"- {linea}"))
        pdf.ln(2)
        
    pdf.ln(4)
    
    # Comentarios Reales
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(192, 0, 0)
    pdf.set_x(15)
    pdf.cell(180, 10, san("Voces del Equipo (Comentarios Reales)"), ln=1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font("Arial", style="I", size=9)
    pdf.set_text_color(80, 80, 80)
    for c in comentarios:
        pdf.set_x(15)
        pdf.multi_cell(180, 4.5, san(f'"{c}"'))
        pdf.ln(2)

    os.remove(temp_img.name)
        
    return bytes(pdf.output())

# --- 8. PROCESAMIENTO PRINCIPAL ---
if archivo_subido is not None:
    try:
        df = pd.read_csv(archivo_subido)
        col_nombres = 'Selecciona el nombre del evaluado'
        columnas_competencias = df.columns[5:14]
        
        nombres_cortos = [
            "Liderazgo de Apoyo", "Comunicación Asertiva", "Toma de Decisiones", 
            "Inteligencia Emocional", "Orientación a Resultados", "Trabajo en Equipo", 
            "Enfoque al Cliente", "Gestión de RRHH", "Aprendizaje Ágil"
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

        # Generar el PDF incluyendo el nombre de la sucursal
        pdf_bytes = generar_pdf_completo(df_competencias, top_3, bottom_3, comentarios_muestra, lowest_3_comps, nombre_sucursal)
        
        st.success(f"¡Reporte estratégico de sucursal {nombre_sucursal.upper()} generado correctamente!")
        st.download_button(
            "📄 Descargar Reporte Final (PDF)", 
            data=pdf_bytes, 
            file_name=f"Reporte_Clima_Laboral_{nombre_sucursal.upper()}.pdf", 
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Error procesando el archivo CSV. Detalle técnico: {e}")