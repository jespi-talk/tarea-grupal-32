# Importamos las bibliotecas necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

##########################################################
# CONFIGURACIÓN DEL DASHBOARD
##########################################################

# Configuración básica de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Configuración simple para los gráficos
sns.set_style("whitegrid")

##################################################
# CARGA DE DATOS
##################################################

# Función para cargar datos con cache para mejorar rendimiento
@st.cache_data
def cargar_datos():
    # Carga el archivo CSV con datos macroeconómicos
    df = pd.read_csv("data.csv")

    #Transformamos el campo fecha a tipo Datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    #Creamos 2 campos nuevos con el dato del año y el mes
    df['agno'] = df['Date'].dt.year
    df['mes'] = df['Date'].dt.month

    return df

# Cargamos los datos
df = cargar_datos()

##############################################
# CONFIGURACIÓN DE LA BARRA LATERAL
##############################################

# Simplificamos la barra lateral con solo lo esencial
st.sidebar.header('Filtros del Dashboard')
st.sidebar.write(f"Filtro para Gráficos Totales por Mes")
# Selector de rango de meses, ya que todas las fechas son del año 2019
mes_inicio, mes_fin = st.sidebar.slider(
    'Rango de Meses', 
    int(df['mes'].min()), 
    int(df['mes'].max()), 
    (1, 3)
)

st.sidebar.write(f"Filtro para Gráficos por fecha")
# Crea un control deslizante de fecha con rango diario
start_date = df["Date"].min()
end_date = df["Date"].max()

selected_date1,selected_date2 = st.sidebar.slider(
    "Selecciona un rango de fechas",
    min_value=start_date.date(),
    max_value=end_date.date(),
    value=(start_date.date(), end_date.date()),
    step=timedelta(days=1),
)

st.sidebar.write(f"Filtro para todos los gráficos")
ciudades = list(df["City"].unique())
filtro_1 = st.sidebar.multiselect(    
    'Filtro por ciudades', 
    options=ciudades,
    default=ciudades,
    help="Selecciona los Tipos de Pago para visualizar en el gráfico de área"
)

##################################################
# FILTRADO DE DATOS
##################################################

df_filtrado = df[(df['mes'] >= mes_inicio) & (df['mes'] <= mes_fin)]
df_filtrado2 = df[(df['Date'] >= pd.to_datetime(selected_date1)) & (df['Date'] <= pd.to_datetime(selected_date2))]
# Título principal del dashboard
st.title('📊 Dashboard Tarea Grupal - Grupo 32')
st.subheader('Gráficos solicitados')


######################################################
# SECCIÓN DE MÉTRICAS (PRIMERA FILA)
#######################################################
df_filtro_ciudad = df_filtrado[df.City.isin(filtro_1)]

total_ventas = df_filtro_ciudad["Total"].sum()

promedio_rating = df_filtro_ciudad["Rating"].mean()

mas_vendido = df_filtro_ciudad.groupby('Product line')['Quantity'].sum().reset_index()
mas_vendido = mas_vendido.sort_values(by ='Quantity', ascending=False)
articulo = mas_vendido.iloc[0,:].tolist()


# Creamos tres columnas para las métricas principales
col1, col2, col3 = st.columns((2, 2, 6))

# Mostramos las métricas con formato adecuado
col1.metric("Ventas Totales", f"${total_ventas:,.0f} ", help=f"Total de ventas en {filtro_1}")
col2.metric("Promedio Rating", f"{promedio_rating:.1f}", help=f"Promedio Rating en {filtro_1}")
col3.metric("Línea de Productos más vendido", f"{articulo[0]} con {int(articulo[1])} Unidades", help=f"Artículo más vendido en {filtro_1}")

#########################################################
# SECCIÓN DE Evolución de las Ventas Totales
#########################################################
st.subheader('Evolución de las Ventas Totales')
# Dividimos la pantalla en dos columnas (proporción 5:5)
c1_f1, c2_f1 = st.columns((5, 5))

# Columna 1: Gráfico de líneas para ver la evolución de la ventas diarias
with c1_f1:
    st.write(f"Ingresos Totales por día ({selected_date1}-{selected_date2})")
    
    # Creamos un gráfico de líneas para ver la evolución de la ventas diarias
    fig, ax = plt.subplots(figsize=(10, 4))
    
    if filtro_1:
        # Definimos el grupo de datos filtrado para el gráfico
        df_filtro_ciudad = df_filtrado2[df.City.isin(filtro_1)]
        dayly_sales = df_filtro_ciudad.groupby('Date')['Total'].sum().reset_index()
    
        # Graficamos los ingresos agrupados por Día
        sns.lineplot(
            data=dayly_sales, 
            x='Date', 
            y='Total', 
            color='#1f77b4',
            ax=ax
        )

        # Configuración del gráfico
        ax.set_ylabel('Total de Ventas')
        ax.set_title("Ingresos Totales por Día")
        ax.grid(True, alpha=0.3)
    
        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("El gráfico muestra la evolución de ingresos en el periodo de tiempo entregado")
    else:
        st.info("Selecciona al menos una Ciudad.")
# Columna 2: # Columna 1: Gráfico de barras para ver la evolución de la ventas mensuales
with c2_f1:
    fig, ax = plt.subplots(figsize=(10, 4))
    st.write(f"Ingresos Totales por mes ({mes_inicio}-{mes_fin})")
    if filtro_1:
        # Graficamos los ingresos agrupados por mes
        df_filtro_ciudad = df_filtrado[df.City.isin(filtro_1)]
        monthly_sales = df_filtro_ciudad.groupby('mes')['Total'].sum().reset_index()

        sns.barplot(
            data=monthly_sales, 
            x='mes', 
            y='Total',
            palette = "muted",
            ax=ax
        )

        # Obtener los valores de las barras
        for p in ax.patches:
            height = p.get_height()
            text_x = p.get_x() + p.get_width() / 2
            text_y = height - 10000
            ax.text(text_x, text_y, f'{height:.0f}', ha='center', va='bottom')
        
        # Configuración del gráfico
        ax.set_ylabel('Total de Ventas')
        ax.set_title("Ingresos Totales por Mes")
        ax.grid(True, alpha=0.3)
    
        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("El gráfico muestra la evolución de ingresos en el periodo de tiempo entregado")
    else:
        st.info("Selecciona al menos una Ciudad.")

##########################################################################################
# SECCIÓN DE Ingresos por Línea de Producto y Distribución de la Calificación de Clientes
##########################################################################################
# Dividimos la pantalla en dos columnas (proporción 5:5)
c1_f2, c2_f2 = st.columns((5, 5))

# Ingresos por Línea de Producto
################################
with c1_f2:
    st.subheader('Ingresos por Línea de Producto')

    fig, ax = plt.subplots(figsize=(6, 3))

    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]
        ventas_lp = df_filtro_ciudad.groupby('Product line')['Total'].sum().reset_index()

        ax = sns.barplot(x="Total", y="Product line", data=ventas_lp, palette = "muted", errorbar=None, order=ventas_lp.sort_values('Total')['Product line'])
        ax.set(title="Ventas por línea de Producto", xlabel="Ventas", ylabel="Líneas de Producto")

        # Obtener los valores de las barras
        for p in ax.patches:
            height = p.get_height()
            width = p.get_width()
            text_x = width - 3000
            text_y = p.get_y() + height / 2 + 0.2
            ax.text(text_x, text_y, f'{width:.0f}', ha='center', va='bottom')

        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("*El gráfico indica que todas las líneas de producto tienen ingresos similares, aunque " \
                "'Sports and travel' y 'Food and beverages' destacan como las categorías con mayores ventas, " \
                "mientras que 'Health and beauty' presenta el ingreso más bajo, lo que podría sugerir diferencias " \
                "en la demanda o estrategia de ventas entre líneas.*")
    else:
        st.info("Selecciona al menos una Ciudad.")

# Distribución de la Calificación de Clientes
#############################################
with c2_f2:
    st.subheader('Distribución de la Calificación de Clientes')

    fig, ax = plt.subplots(figsize=(6, 3))
    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]
        sns.boxplot(data=df_filtro_ciudad, x='City', y='Rating', ax=ax, palette = "muted")
        
        # Configuración del gráfico
        ax.set_xlabel('Ciudad del Cliente')
        ax.set_ylabel('Rating Cliente')
        ax.set_title('Gráficos de Caja - Análisis Rating')
        ax.grid(True, alpha=0.3)
        
        # Mostrar gráfico
        st.pyplot(fig)
        st.write("*Explora los puntajes de los distintos Clientes, separados por su Ciudad. Según lo que se muestra, los Clientes " \
        "de \"Mandalay\" están más mal evaluados que sus pares de otras ciudades*")
    else:
        st.info("Selecciona al menos una Ciudad.")

##############################################################################################
# SECCIÓN DE Comparación del Gasto por Tipo de Cliente & Relación entre Costo y Ganancia Bruta
##############################################################################################
# Dividimos la pantalla en dos columnas (proporción 5:5)
c1_f3, c2_f3 = st.columns((5, 5))

# Comparación del Gasto por Tipo de Cliente
###########################################
with c1_f3:
    st.subheader('Comparación del Gasto por Tipo de Cliente')

    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]
        pie_data = df_filtro_ciudad.groupby('Customer type')['Total'].sum()
        labels=[f'{q}' for q in pie_data.index]

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.pie(
            pie_data, 
            labels=labels,
            autopct='%1.1f%%',  # Mostrar porcentajes
        )

        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("*El gráfico muestra los gastos totales por Tipo de Cliente. Se puede apreciar que el cliente \"Member\" gasta más que el cliente \"Normal\"*")
    else:
        st.info("Selecciona al menos una Ciudad.")

# Relación entre Costo y Ganancia Bruta
#######################################
with c2_f3:
    st.subheader('Relación entre Costo y Ganancia Bruta')
    #Relación entre Costo y Ganancia Bruta (cogs, gross income)

    # Asegurar un estilo limpio
    fig, ax = plt.subplots(figsize=(8, 6))

    if filtro_1:
        #Un gráfico de dispersión (scatterplot) es adecuado para visualizar la relación entre dos variables numéricas.
        df_filtro_ciudad = df[df.City.isin(filtro_1)]

        sns.scatterplot(data=df_filtro_ciudad, x='cogs', y='gross income')
        plt.title("Relación entre Costo de Bienes Vendidos (cogs) e Ingreso Bruto")
        plt.xlabel("Costo de Bienes Vendidos (cogs)")
        plt.ylabel("Ingreso Bruto")
        plt.tight_layout()

        st.pyplot(fig)
        st.write("*El gráfico refleja una relación lineal esperada , donde a mayores costos están asociados a mayores ingresos, " \
                "es decir a medida que aumenta el COGS (eje X), el Ingreso Bruto (eje Y) también tiende a aumentar. La disposición " \
                "de los puntos parece seguir una tendencia lineal, lo que indica una correlación positiva entre ambas variables*")
    else:
        st.info("Selecciona al menos una Ciudad.")

##########################################################################
# SECCIÓN DE Métodos de Pago Preferidos & Análisis de Correlación Numérica
##########################################################################
# Dividimos la pantalla en dos columnas (proporción 5:5)
c1_f4, c2_f4 = st.columns((5, 5))

# SECCIÓN DE Métodos de Pago Preferidos
#######################################
with c1_f4:
    st.subheader('Métodos de Pago Preferidos')

    fig, ax = plt.subplots(figsize=(6, 3))
    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]

        pagos_preferidos = df_filtro_ciudad.groupby('Payment')['Total'].count()
        labels=[f'{q}' for q in pagos_preferidos.index]

        ax.pie(
            pagos_preferidos, 
            labels=labels,
            autopct='%1.1f%%',  # Mostrar porcentajes
        )

        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("*El gráfico muestra que el uso de medio de pago es parejo, aunque se ve que EWallet es la más usada.*")
    else:
        st.info("Selecciona al menos una Ciudad.")

# Análisis de Correlación Numérica
##################################
with c2_f4:
    st.subheader('Análisis de Correlación Numérica')

    fig, ax = plt.subplots(figsize=(6, 3))
    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]

        # Seleccionar solo las columnas numéricas relevantes
        numeric_cols = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']
        correlation_matrix = df_filtro_ciudad[numeric_cols].corr()

        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title("Matriz de Correlación de Variables Numéricas")
        plt.tight_layout()


        st.pyplot(fig)
        st.write("*La matriz de correlación muestra una fuerte relación positiva entre las variables asociadas a " \
        "las ventas, como 'Total', 'cogs', 'Tax 5%' y 'gross income', lo que indica que estas crecen juntas. " \
        "En cambio, variables como 'Unit price' y 'Quantity' tienen una correlación baja entre sí, y 'Rating' " \
        "presenta una correlación muy débil o nula con todas las demás variables, lo que sugiere que la satisfacción " \
        "del cliente no está directamente influenciada por los factores económicos analizados.*")
    else:
        st.info("Selecciona al menos una Ciudad.")

########################################################
# SECCIÓN DE Composición del Ingreso Bruto por Sucursal y Línea de Producto
########################################################
# Dividimos la pantalla en dos columnas (proporción 5:5)
c1_f5, c2_f5, c3_f5 = st.columns((2, 6, 2))

with c2_f5:
    st.subheader('Composición del Ingreso Bruto por Sucursal y Línea de Producto')

    fig, ax = plt.subplots(figsize=(6, 3))
    if filtro_1:
        df_filtro_ciudad = df[df.City.isin(filtro_1)]

        sns.barplot(data=df_filtro_ciudad, x='Branch', y='gross income', hue='Product line')
        
        plt.title("Ingreso Bruto por Sucursal y Línea de Producto")
        plt.xlabel("Sucursal")
        plt.ylabel("Ingreso Bruto")
        plt.xticks(rotation=0) # Mantener etiquetas verticales si es posible
        plt.legend(title="Línea de Producto", bbox_to_anchor=(1.05, 1), loc='upper left') # Mover leyenda fuera del gráfico
        plt.tight_layout()

        st.pyplot(fig)
        st.write("*El gráfico compara el ingreso bruto generado por diferentes líneas de producto (como accesorios electrónicos, moda, " \
                "alimentos, belleza, hogar y deportes) en cuatro sucursales distintas (A, B, C, D), permitiendo identificar qué categorías " \
                "tienen mayor contribución en cada ubicación y revelando patrones como posibles preferencias regionales, diferencias en la " \
                "demanda o eficiencia comercial entre sucursales. Alguna(s) sucursal(es) (ej. A o D) destacan en ventas de ciertas líneas " \
                "(ej. electrónicos o alimentos), mientras otras (ej. B o C) muestran menor rendimiento. Las líneas más rentables como \"Food " \
                "and beverages\" o \"Health and beauty\" podrían dominar en ingresos frente a otras (ej. \"Sports and travel\").")
    else:
        st.info("Selecciona al menos una Ciudad.")