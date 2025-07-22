import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df_tarifas = pd.read_excel("datos_base/tarifas_bt5.xlsx")

st.set_page_config(page_title="Comparador BT5", layout="wide")
st.title("🔌 Comparador Tarifas BT5B, BT5F y BT5I")

# Ingreso de consumo
consumo_kwh = st.number_input("🔢 Ingresa el consumo en kWh:", min_value=1, value=150)

# Filtrar datos de tarifas residenciales (puedes modificar a no residencial si prefieres)
df_residencial = df_tarifas[df_tarifas['USUARIO'].str.contains("Residencial", na=False)]

# Función para calcular el total por tarifa
def calcular_total(tarifa, consumo):
    df_tarifa = df_residencial[df_residencial['TARIFA'] == tarifa]
    fijo = df_tarifa[df_tarifa['CARGO'].str.contains("Fijo")]['PRECIO'].values[0]

    if consumo <= 30:
        energia_punta = df_tarifa[df_tarifa['CARGO'].str.contains("Punta")]['PRECIO'].values[0]
        energia_fp = df_tarifa[df_tarifa['CARGO'].str.contains("Fuera de Punta")]['PRECIO'].values[0]
        energia = ((consumo * 0.4) * energia_punta + (consumo * 0.6) * energia_fp) / 100
    elif consumo <= 140:
        primer_tramo = 30
        exceso = consumo - 30

        energia_punta = df_tarifa[df_tarifa['CARGO'].str.contains("Punta - Primeros 30")]['PRECIO'].values[0]
        energia_fp = df_tarifa[df_tarifa['CARGO'].str.contains("Fuera de Punta - Primeros 30")]['PRECIO'].values[0]
        energia_punta_exceso = df_tarifa[df_tarifa['CARGO'].str.contains("Punta - Exceso")]['PRECIO'].values[0]
        energia_fp_exceso = df_tarifa[df_tarifa['CARGO'].str.contains("Fuera de Punta - Exceso")]['PRECIO'].values[0]

        energia = ((primer_tramo * 0.4) * energia_punta + (primer_tramo * 0.6) * energia_fp +
                   (exceso * 0.4) * energia_punta_exceso + (exceso * 0.6) * energia_fp_exceso) / 100
    else:
        energia_punta = df_tarifa[df_tarifa['CARGO'].str.contains("Punta")]['PRECIO'].values[0]
        energia_fp = df_tarifa[df_tarifa['CARGO'].str.contains("Fuera de Punta")]['PRECIO'].values[0]

        energia = ((consumo * 0.4) * energia_punta + (consumo * 0.6) * energia_fp) / 100

    return round(fijo + energia, 2)

# Calcular para cada tarifa
tarifas = ['TARIFA BT5B', 'TARIFA BT5F', 'TARIFA BT5I']
resultados = []

for t in tarifas:
    total = calcular_total(t, consumo_kwh)
    resultados.append({'Tarifa': t, 'Total S/': total})

df_resultado = pd.DataFrame(resultados)

# Mostrar tabla
st.subheader("🧾 Comparativo de Facturación")
st.dataframe(df_resultado, use_container_width=True)

# Gráfico de barras
fig = px.bar(df_resultado, x='Tarifa', y='Total S/', color='Tarifa', text='Total S/',
             title=f"Comparativo de Costo por {consumo_kwh} kWh",
             color_discrete_sequence=px.colors.qualitative.Set2)

st.plotly_chart(fig, use_container_width=True)

# Gráfico de pastel
fig2 = px.pie(df_resultado, names='Tarifa', values='Total S/',
              title="Distribución porcentual por tarifa",
              color_discrete_sequence=px.colors.qualitative.Set2)

st.plotly_chart(fig2, use_container_width=True)
