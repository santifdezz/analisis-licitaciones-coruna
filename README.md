# Análisis de Licitaciones Públicas en A Coruña

Este proyecto combina **web scraping** y **análisis de datos** para estudiar las licitaciones públicas realizadas en A Coruña. El objetivo es identificar patrones, irregularidades y características relevantes en los procesos de contratación pública.

## Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Flujo de Trabajo](#flujo-de-trabajo)
3. [Requisitos](#requisitos)
4. [Instalación](#instalación)
5. [Uso](#uso)
6. [Resultados](#resultados)
7. [Contribuciones](#contribuciones)
8. [Licencia](#licencia)

---

## Descripción del Proyecto

El proyecto consta de dos partes principales:

1. **Scraping de Datos**: Utilizando Selenium, se extraen datos de licitaciones públicas del portal de contratación del Estado. Los datos incluyen información como el expediente, el objeto del contrato, el presupuesto base, el importe adjudicado, entre otros.

2. **Análisis de Datos**: Los datos extraídos se procesan y analizan para identificar patrones, irregularidades y características clave de las licitaciones. Se generan gráficos y estadísticas descriptivas para facilitar la interpretación de los resultados.

---

## Flujo de Trabajo

1. **Configuración del entorno**:
   - Instalación de librerías necesarias como `pandas` y `selenium`.
   - Configuración del navegador Firefox para la automatización.

2. **Extracción de datos**:
   - Navegación por el portal de contratación del Estado.
   - Extracción de datos de licitaciones del Ayuntamiento de A Coruña.
   - Captura de capturas de pantalla de los expedientes.

3. **Procesamiento de datos**:
   - Limpieza y normalización de los datos.
   - Conversión de datos a un formato estructurado (DataFrame de pandas).
   - Exportación de los datos a un archivo CSV.

4. **Análisis de datos**:
   - Comparación entre presupuesto base y adjudicación.
   - Identificación de contratos con características atípicas.
   - Análisis de participación de licitadores y procedimientos de contratación.

---

## Requisitos

- Python 3.8 o superior
- Navegador Firefox
- Geckodriver (para Selenium)

### Librerías de Python

- `selenium`
- `pandas`
- `matplotlib`
- `seaborn`
- `unicodedata`

---

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/santifdezz/analisis-licitaciones-coruna.git
   cd analisis-licitaciones-coruna
   ```

2. Instala las dependencias (o con un entorno conda utilizando los comandos en los notebooks):
   ```bash
   pip install -r requirements.txt
   ```
3. Asegúrate de tener Firefox y Geckodriver instalados y configurados en tu sistema.

## Uso
1. Ejecuta el script de scraping para extraer los datos:
   ```bash
   python scrapping_licitaciones_coruna.py
    ```
2. Procesa y analiza los datos utilizando el cuaderno de análisis:
   pip install -r requirements.txt
3. Los resultados se exportarán a un archivo CSV y se generarán gráficos para su interpretación.

## Resultados
El análisis realizado incluye:

 - Comparación entre presupuesto base y adjudicación.
 - Identificación de contratos con un solo licitador.
 - Análisis de contratos urgentes y su impacto en los costos.
 - Visualización de los procedimientos de contratación más comunes.
