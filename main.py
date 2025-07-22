import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Comparativa BT5B - BT5F - BT5I", layout="centered")

# Leer el Excel desde la carpeta (coloca tu Excel en datos_base/tarifas_bt5.xlsx)
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

# Función para BT5B (no depende de punta/fuera)
def calcular_bt5b(consumo, df_tarifa):
    fijo = df_tarifa[df_tarifa['CARGO'].str.contains('Fijo')]['PRECIO'].values[0]
    
    if consumo <= 30:
        energia = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h') & (df_tarifa['CARGO'].str.contains('Energía Activa'))]['PRECIO'].values[0]
        total = fijo + consumo * energia / 100
    elif consumo <= 140:
        energia_30 = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Primeros 30'))]['PRECIO'].values[0]
        energia_exceso = df_tarifa[(df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h') & (df_tarifa['CARGO'].str.contains('Exceso de 30'))]['PRECIO'].values[0]
        total = fijo + (30 * energia_30 / 100) + ((consumo - 30) * energia_exceso / 100)
    else:
        energia = df_tarifa[(df_tarifa['CONSUMO'].str.contains('mayor a 140')) & (df_tarifa['CARGO'].str.contains('Energía Activa'))]['PRECIO'].values[0]
        total = fijo + consumo * energia / 100
    
    return round(total, 2)

# Función para BT5F y BT5I
def calcular_tarifa_puntual(consumo, df_tarifa, porcentaje_punta, porcentaje_fuera):
    fijo = df_tarifa[df_tarifa['CARGO'].str.contains('Fijo')]['PRECIO'].values[0]
    
    if consumo <= 30:
        energia = df_tarifa[df_tarifa['CONSUMO'] == 'Consumo de 0 - 30 kW.h']
        if 'Punta' in energia['CARGO'].values[0]:
            precio_punta = energia[energia['CARGO'].str.contains('Punta')]['PRECIO'].values[0]
            precio_fuera = energia[energia['CARGO'].str.contains('Fuera de Punta')]['PRECIO'].values[0]
            total = fijo + consumo * (precio_punta * porcentaje_punta + precio_fuera * porcentaje_fuera) / 100
        elif 'Media' in energia['CARGO'].values[0]:  # BT5I
            media = energia[energia['CARGO'].str.contains('Media')]['PRECIO'].values[0]
            base = energia[energia['CARGO'].str.contains('Base')]['PRECIO'].values[0]
            punta = energia[energia['CARGO'].str.contains('Punta')]['PRECIO'].values[0]
            total = fijo + consumo * ((media + base)/2)  * porcentaje_fuera / 100 + consumo * punta * porcentaje_punta / 100
    elif consumo <= 140:
        energia = df_tarifa[df_tarifa['CONSUMO'] == 'Consumo de 31 - 140 kW.h']
        if 'Punta' in energia['CARGO'].values[0] and 'Fuera de Punta' in energia['CARGO'].values[1]:
            pta_30 = energia[energia['CARGO'].str.contains('Punta - Primeros')]['PRECIO'].values[0]
            fdp_30 = energia[energia['CARGO'].str.contains('Fuera de Punta - Primeros')]['PRECIO'].values[0]
            pta_exc = energia[energia['CARGO'].str.contains('Punta - Exceso')]['PRECIO'].values[0]
            fdp_exc = energia[energia['CARGO'].str.contains('Fuera de Punta - Exceso')]['PRECIO'].values[0]
            total = fijo + 30 * (pta_30 * porcentaje_punta + fdp_30 * porcentaje_fuera) / 100 + (consumo - 30) * (pta_exc * porcentaje_punta + fdp_exc * porcentaje_fuera) / 100
        elif 'Media' in energia['CARGO'].values[0]:  # BT5I
            media_30 = energia[energia['CARGO'].str.contains('Media - Primeros')]['PRECIO'].values[0]
            base_30 = energia[energia['CARGO'].str.contains('Base - Primeros')]['PRECIO'].values[0]
            media_exc = energia[energia['CARGO'].str.contains('Media - Exceso')]['PRECIO'].values[0]
            base_exc = energia[energia['CARGO'].str.contains('Base - Exceso')]['PRECIO'].values[0]
            punta_30 = energia[energia['CARGO'].str.contains('Punta - Primeros')]['PRECIO'].values[0]
            punta_exc = energia[energia['CARGO'].str.contains('Punta - Exceso')]['PRECIO'].values[0]
            
            total = fijo + 30 * ( (media_30 + base_30)/2 * porcentaje_fuera + punta_30 * porcentaje_punta) / 100 + \
                    (consumo - 30) * ( (media_exc + base_exc)/2 * porcentaje_fuera + punta_exc * porcentaje_punta) / 100
    else:
        energia = df_tarifa[df_tarifa['CONSUMO'].str.contains('mayor a 140', na=False)]
        if 'Punta' in energia['CARGO'].values[0] and 'Fuera de Punta' in energia['CARGO'].values[1]:
            pta = energia[energia['CARGO'].str.contains('Punta')]['PRECIO'].values[0]
            fdp = energia[energia['CARGO'].str.contains('Fuera de Punta')]['PRECIO'].values[0]
            total = fijo + consumo * (pta * porcentaje_punta + fdp * porcentaje_fuera) / 100
        elif 'Media' in energia['CARGO'].values[0]:  # BT5I
            media = energia[energia['CARGO'].str.contains('Media')]['PRECIO'].values[0]
            base = energia[energia['CARGO'].str.contains('Base')]['PRECIO'].values[0]
            punta = energia[energia['CARGO'].str.contains('Punta')]['PRECIO'].values[0]
            total = fijo + consumo * ((media + base)/2 * porcentaje_fuera + punta * porcentaje_punta) / 100
    
    return round(total, 2)

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

# Gráfico de barras horizontal
fig, ax = plt.subplots(figsize=(8,5))
df_plot = df_resultado.set_index('Escenario')
df_plot.plot(kind='barh', ax=ax)
plt.xlabel("S/ Total")
plt.title(f"Comparación de Tarifas para {consumo_kwh} kWh")
plt.grid(axis='x', linestyle='--', alpha=0.5)
st.pyplot(fig)
