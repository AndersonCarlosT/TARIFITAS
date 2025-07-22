import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Comparativa BT5B - BT5F - BT5I", layout="centered")

# Leer el Excel desde GitHub (o local si corres en dev)
df = pd.read_excel("datos_base/tarifas_bt5.xlsx")

# Input de usuario
consumo_kwh = st.number_input("🔢 Ingresa tu consumo mensual en kWh:", min_value=1, value=150)

# Escenarios de Punta / Fuera de Punta
escenarios = {
    "100% fuera de punta": (0, 1),
    "20% punta / 80% fuera de punta": (0.2, 0.8),
    "40% punta / 60% fuera de punta": (0.4, 0.6),
    "50% punta / 50% fuera de punta": (0.5, 0.5),
}

def calcular_bt5b(consumo, df_tarifa):
    if consumo <= 30:
        fijo = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        energia = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'] == 'Cargo por Energía Activa')]['PRECIO'].values[0]
        total = fijo + (consumo * energia / 100)
    elif consumo <= 140:
        fijo = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        primeros_30 = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Primeros 30'))]['PRECIO'].values[0]
        exceso = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Exceso'))]['PRECIO'].values[0]
        total = fijo + primeros_30 + ((consumo - 30) * exceso / 100)
    else:
        fijo = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        energia = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'].str.contains('Energía Activa'))]['PRECIO'].values[0]
        total = fijo + (consumo * energia / 100)
    return total

def calcular_tarifa_puntual(consumo, df_tarifa, porcentaje_punta, porcentaje_fuera):
    if consumo <= 30:
        fijo = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        punta = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'].str.contains('Punta'))]['PRECIO'].values[0]
        fuera = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'].str.contains('Fuera'))]['PRECIO'].values[0]
        total = fijo + (consumo * ((porcentaje_punta * punta) + (porcentaje_fuera * fuera)) / 100)
    elif consumo <= 140:
        fijo = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        punta_30 = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Punta - Primeros'))]['PRECIO'].values[0]
        fuera_30 = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Fuera de Punta - Primeros'))]['PRECIO'].values[0]
        punta_exceso = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Punta - Exceso'))]['PRECIO'].values[0]
        fuera_exceso = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Fuera de Punta - Exceso'))]['PRECIO'].values[0]
        total = fijo + (30 * ((porcentaje_punta * punta_30) + (porcentaje_fuera * fuera_30)) / 100) + \
                ((consumo - 30) * ((porcentaje_punta * punta_exceso) + (porcentaje_fuera * fuera_exceso)) / 100)
    else:
        fijo = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'] == 'Cargo Fijo Mensual')]['PRECIO'].values[0]
        punta = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'].str.contains('Punta'))]['PRECIO'].values[0]
        fuera = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'].str.contains('Fuera'))]['PRECIO'].values[0]
        total = fijo + (consumo * ((porcentaje_punta * punta) + (porcentaje_fuera * fuera)) / 100)
    return total

# Generar la tabla comparativa
tabla_resultados = []

for escenario, (p_punta, p_fuera) in escenarios.items():
    bt5b = calcular_bt5b(consumo_kwh, df[df['TARIFA'] == 'TARIFA BT5B'])
    bt5f = calcular_tarifa_puntual(consumo_kwh, df[df['TARIFA'] == 'TARIFA BT5F'], p_punta, p_fuera)
    bt5i = calcular_tarifa_puntual(consumo_kwh, df[df['TARIFA'] == 'TARIFA BT5I'], p_punta, p_fuera)
    tabla_resultados.append([escenario, round(bt5b,2), round(bt5f,2), round(bt5i,2)])

# Mostrar tabla
df_resultado = pd.DataFrame(tabla_resultados, columns=["Escenario", "BT5B S/", "BT5F S/", "BT5I S/"])
st.dataframe(df_resultado, use_container_width=True)

# Gráfico de barras
fig, ax = plt.subplots(figsize=(8,5))
df_plot = df_resultado.set_index('Escenario')
df_plot.plot(kind='bar', ax=ax)
plt.ylabel("S/ Total")
plt.title(f"Comparación de Tarifas para {consumo_kwh} kWh")
plt.xticks(rotation=45)
st.pyplot(fig)
