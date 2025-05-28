# %% [markdown]
# # Web Scraping y Análisis de Licitaciones Públicas
# 
# En este cuaderno realizamos un proceso completo de extracción, transformación y carga (ETL) de datos sobre licitaciones públicas del portal oficial de contratación del Estado. Concretamente de la A Coruña.
# 
# ## Flujo de trabajo
# 
# 1. **Configuración del entorno**:
#     - Instalación de librerías necesarias (pandas y selenium)
#     - Importación de dependencias para web scraping y manejo de datos
# 
# 2. **Web Scraping con Selenium**:
#     - Configuración del navegador Firefox para la automatización
#     - Navegación por el portal de contratación del estado
#     - Extracción de datos de licitaciones del Ayuntamiento de A Coruña
#     - Captura de screenshots de los expedientes
# 
# 3. **Procesamiento de datos**:
#     - Conversión de datos extraídos a DataFrame de pandas
#     - Normalización de columnas y textos
#     - Limpieza de valores nulos en tablas importantes
#     - Exportación a CSV como respaldo

# %% [markdown]
# ## Instalacion de las librerias necesarias

# %%
# %conda install -c conda-forge -y selenium 
# %conda install -y pandas

# %% [markdown]
# ## Importaciones necesarias

# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

import os
import time
import concurrent.futures
import unicodedata
import pandas as pd

# %% [markdown]
# ## Inicializamos el driver de Selenium

# %%
driver = webdriver.Firefox()

# %% [markdown]
# ## Funciones Selenium

# %%
def waitUntil(by, path):
    try:
        return WebDriverWait(driver, 15).until(EC.presence_of_element_located((by, path)))
    except TimeoutError:
        print(f"Element with {by}='{path}' not found within the timeout.")
    return None

def tryClickIfClickable(by, path):
    try:
        element = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((by, path)))
        element.click()
        return True
    except:
        return False

def search_into_tree(text_searched, table_searched_tag, last=False):
    """ Busca un texto específico en una tabla y hace clic en la fila correspondiente."""
    table = driver.find_elements(By.CLASS_NAME, table_searched_tag)
    if last:
        # Iteramos en la fila desde atrás, cogiendo como primer elemento el que tenemos que clickar
        for row in reversed(table):
            if text_searched == row.text:
                row.click()
                break
    else:
        for row in table:
            if text_searched in row.text:
                act_div = row.find_element(By.XPATH, "./../..")
                son_rows = act_div.find_elements(By.TAG_NAME, "td")
                for son_row in son_rows:
                    row = son_row.get_attribute("class").strip()
                    if "multiline" in str(row):
                        son_row.click()
                break

def move_to_table():
    """ 
    Navega a la sección de licitaciones en el sitio web de contratación del estado. 
    """
    driver.get("https://www.contrataciondelestado.es")
    waitUntil(By.CLASS_NAME, "quick-access")
    # Entramos en el apartado de Publicaciones
    tryClickIfClickable(By.XPATH, "//a[@title='Buscar publicaciones']")
    # Clickamos en licitaciones
    tryClickIfClickable(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:logoFormularioBusqueda")
    # Clickamos búsqueda avanzada
    tryClickIfClickable(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:textBusquedaAvanzada")
    # Clickamos el elemento Seleccionar Entidad
    tryClickIfClickable(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:idSeleccionarOCLink")
    # Buscar en la tabla
    search_table()

def search_table():
    """ 
    Busca en la tabla de entidades locales y selecciona la entidad deseada. 
    """
    waitUntil(By.CLASS_NAME, "tafelTreecontent")
    search_into_tree("ENTIDADES LOCALES", "tafelTreecontent")
    search_into_tree("Galicia", "tafelTreecontent")
    search_into_tree("A Coruña", "tafelTreecontent")
    search_into_tree("Ayuntamientos", "tafelTreecontent")
    search_into_tree("A Coruña", "tafelTreecanevas", True)

    # Seleccionar la opción de Junta de Gobierno del Ayuntamiento de A Coruña
    options = driver.find_elements(By.TAG_NAME, "select")
    select = Select(options[-1])
    select.select_by_index(0)
    tryClickIfClickable(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:botonAnadirMostrarPopUpArbolEO")
    tryClickIfClickable(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1")

def get_links(driver):
    """
    Obtiene todos los enlaces de una página web paginada.
    """
    try:
        lista_enlaces = []
        while True:
            # Encontrar los enlaces en la página actual
            enlaces = driver.find_elements(By.XPATH, ".//img[@title='Abre en pestaña nueva']/..")
            for enlace in enlaces:
                lista_enlaces.append(enlace.get_attribute("href"))
            
            # Intentar hacer clic en el botón de siguiente
            if not tryClickIfClickable(By.XPATH, ".//input[@title='Siguiente']"):
                # Si no se puede hacer clic, asumimos que no hay más páginas
                break
    except Exception as e:
        print(f"Error: {e}")
        
    driver.quit()
    print("Fin enlaces")
    return lista_enlaces

def process_links(driver, enlaces):
    """
    Procesa una lista de enlaces y extrae la información de cada expediente.
    """
    local_data_objects = []
    # Crear directorio para guardar capturas de pantalla si no existe
    for enlace in enlaces:
        driver.get(enlace)

        # Hacemos un wait con selenium para esperar a que la página cargue al completo
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "capaAtributos")))

        # Pillamos el siguiente span al span que tiene el título Expediente
        expediente = driver.find_element(By.XPATH, "//span[contains(text(),'Expediente')]/following-sibling::span").text

        # Cambia las barras por guiones bajos para evitar problemas con el nombre del archivo
        expediente = expediente.replace("/", "_")

        driver.save_full_page_screenshot(f"./res/{expediente}.png")

        divs = driver.find_elements(By.CLASS_NAME, "capaAtributos")
        
        # Creamos un diccionario para almacenar los datos del objeto actual
        data_object = {"Expediente": expediente}

        # Iteramos por cada div y extraemos los datos
        for div in divs:
            uls = div.find_elements(By.TAG_NAME, "ul")
            for ul in uls:
                lis = ul.find_elements(By.TAG_NAME, "li")
                if len(lis) > 1:
                    # Si el lis[1].text presenta varios textos, los juntamos en uno solo
                    data_object[lis[0].text] = " ".join(lis[1].text.split())
                else:
                    data_object[lis[0].text] = "No disponible"
        
        # Añadimos el objeto a la lista local
        local_data_objects.append(data_object)
    return local_data_objects

def split_list(lst, n):
    """Divide una lista en n partes aproximadamente iguales."""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def process_links_in_parallel(listaEnlaces, num_drivers):
    """
    Procesa una lista de enlaces en paralelo utilizando múltiples instancias de navegadores.
    """
    # Dividimos la lista de enlaces en partes iguales
    chunks = split_list(listaEnlaces, num_drivers)
    # Crear directorio para guardar capturas de pantalla si no existe
    if not os.path.exists('res'):
        os.makedirs('res')
    
    # Creamos las instancias del navegador
    drivers = [
        webdriver.Firefox(service=Service(executable_path=gecko_driver_path, log_output='geckodriver.log'))
        for _ in range(num_drivers)
    ]
    
    data_objects = []
    try:
        # Ejecutamos las tareas en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_drivers) as executor:
            futures = [
                executor.submit(process_links, driver, enlaces)
                for driver, enlaces in zip(drivers, chunks)
            ]
            for future in concurrent.futures.as_completed(futures):
                data_objects.extend(future.result())
    finally:
        # Cerramos todos los navegadores
        for driver in drivers:
            driver.quit()
    
    # Crear un DataFrame con la lista de objetos
    return pd.DataFrame(data_objects)


# %% [markdown]
# ## Ejecución

# %%
move_to_table()
listaEnlaces = get_links(driver)
print("Enlaces obtenidos:", len(listaEnlaces))
# Dividimos la lista de enlaces en 4 partes y sacamos los datos en paralelo
df = process_links_in_parallel(listaEnlaces, 4)


# %%
df.head()

# %% [markdown]
# ## Normalización de columnas y datos 
# 
# En esta sección, realizaremos la  normalización de los datos para garantizar su calidad. Esto incluye la normalización de nombres de columnas eliminando espacios, caracteres especiales y acentos, la limpieza de columnas numéricas eliminando caracteres no deseados como puntos, comas y palabras como "Euros", la conversión de datos numéricos a tipo float, la eliminación de valores no válidos como "Ver detalle de la adjudicación", el manejo de valores nulos en columnas clave y la normalización de datos textuales para mantener consistencia en el análisis.
# 
# 

# %% [markdown]
# ## Funciones de Normalización de datos

# %%
file_path = "licitaciones_coruna.csv"
df = pd.read_csv(file_path, delimiter=",", encoding="utf-8")


# %%

def normalize_text_cols(texto):
    """
    Elimina acentos y caracteres especiales de un texto usando unicodedata.
    """
    if isinstance(texto, str):
        texto_normalizado = unicodedata.normalize('NFD', texto)
        texto_sin_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        return texto_sin_acentos.lower()  # Convertir a minúsculas
    return texto


def normalize_numeric_cols(df, numerical_col):
    """
    Limpia las columnas numéricas eliminando caracteres no deseados y convirtiéndolas a float.
    """
    for col in numerical_col:
        df[col] = (
            df[col]
            .str.replace(".", "", regex=False)  # Eliminar puntos como separadores de miles
            .str.replace(r"\s*Euros", "", regex=True)  # Eliminar "Euros" con o sin espacio antes
            .str.replace("Ver detalle de la adjudicación", "", regex=False)  # Eliminar "Ver detalle de la adjudicación"
            .str.replace(",", ".", regex=False)  # Reemplazar comas por puntos (decimales)
            .replace("", pd.NA)  # Reemplazar valores vacíos con NaN
        )
    # Eliminar filas con valores nulos en columnas numéricas
    df = df.dropna(subset=numerical_col)
    # Convertir columnas numéricas a tipo float
    for col in numerical_col:
        df[col] = df[col].astype(float)
    return df

def normalize_cols(df):
    """
    Normaliza los nombres de las columnas del DataFrame.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace(":", "", regex=False)
        .str.replace("º", "o")
    )
    df.columns = [normalize_text_cols(col) for col in df.columns]
    return df

def normalize_text_data(df):
    """
    Normaliza los datos de texto en todas las columnas de tipo texto del DataFrame.
    """
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(normalize_text_cols)
    return df
    
def clean_data(df):
    """
    Limpia y normaliza un DataFrame de pandas.
    """
    # Normalizar nombres de columnas
    df = normalize_cols(df)
    
    # Columnas numéricas a limpiar
    numerical_col = [
        "presupuesto_base_de_licitacion_sin_impuestos",
        "valor_estimado_del_contrato",
        "importe_de_adjudicacion",
    ]
    
    # Limpiar columnas numéricas
    df = normalize_numeric_cols(df, numerical_col)
    
    df = normalize_text_data(df)
    
    return df

# %%
df = clean_data(df)

# %%
df.head()

# %%
df.to_csv('licitaciones_coruna2.csv', index=False, encoding='utf-8-sig')


