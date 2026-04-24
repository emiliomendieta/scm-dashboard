import streamlit as st
import pandas as pd
import plotly.express as px

# ── Configuración ────────────────────────────────────────────
st.set_page_config(
    page_title="SCM Dashboard Emilio",
    page_icon="🥸",
    layout="wide"
)

# ── Datos embebidos (modo demo para deploy público) ──────────
def get_demo_data():
    inventario = pd.DataFrame({
        'sku': ['PAN-CELL-200','PAN-CELL-400','INV-SOL-3K','INV-SOL-5K','BAT-LIT-10','MIC-ENP-01','PAN-JNK-350','BAT-SOL-20'],
        'descripcion': ['Panel Solar 200W','Panel Solar 400W Bifacial','Inversor Solar 3kW','Inversor Solar 5kW','Batería Litio 10kWh','Microinversor Enphase IQ8','Panel Solar 350W Jinko','Batería Solar 20kWh'],
        'categoria': ['Paneles','Paneles','Inversores','Inversores','Baterías','Microinversores','Paneles','Baterías'],
        'stock_actual': [45, 120, 8, 22, 3, 67, 15,2],
        'stock_minimo': [50, 40, 15, 10, 5, 30, 20,8],
        'stock_maximo': [200, 180, 60, 50, 20, 150, 100,30],
        'precio_unitario': [150, 280, 420, 680, 3200, 185, 210,5800]
    })
    inventario['diferencia'] = inventario['stock_actual'] - inventario['stock_minimo']
    inventario['valor_inventario'] = inventario['stock_actual'] * inventario['precio_unitario']

    categorias = inventario.groupby('categoria').agg(
        num_productos=('sku','count'),
        valor_total=('valor_inventario','sum')
    ).reset_index().sort_values('valor_total', ascending=False)

    proveedores = pd.DataFrame({
        'proveedor': ['Panasonic Energy','BYD Solar','SolarTech Europe','Enphase Energy','Jinko Solar'],
        'calificacion': [9.2, 8.1, 8.7, 9.5, 7.9],
        'num_ordenes': [2, 1, 2, 1, 1],
        'valor_total': [37400, 32000, 18600, 9250, 12600]
    })

    return inventario, categorias, proveedores

# ── Cargar datos ─────────────────────────────────────────────
df_inv, df_cat, df_prov = get_demo_data()

# ── Header ───────────────────────────────────────────────────
st.title("SCM Dashboard — Inventario & Proveedores")
st.markdown("Dashboard interactivo de Supply Chain | **Emilio Mendieta**")
st.info("Portafolio SCM Analytics - Emilio Mendieta")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Productos", len(df_inv))
col2.metric("Valor Inventario", f"${df_cat['valor_total'].sum():,.0f}")
col3.metric("Productos Bajo Mínimo", len(df_inv[df_inv['diferencia'] < 0]))
col4.metric("Proveedores Activos", len(df_prov))

st.divider()

# ── Alertas de Stockout ───────────────────────────────────────
st.subheader("🚨 Alertas de Stockout")
df_alertas = df_inv[df_inv['diferencia'] < 0][['sku','descripcion','categoria','stock_actual','stock_minimo','diferencia']]
if len(df_alertas) > 0:
    st.dataframe(df_alertas, use_container_width=True)
else:
    st.success("✅ No hay productos bajo el stock mínimo")

st.divider()

# ── Gráficas ──────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Valor de Inventario por Categoría")
    fig1 = px.bar(df_cat, x='categoria', y='valor_total',
                  color='categoria', text_auto=True)
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("🏭 Valor de Órdenes por Proveedor")
    fig2 = px.bar(df_prov, x='proveedor', y='valor_total',
                  color='proveedor', text_auto=True)
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Tabla completa ────────────────────────────────────────────
st.subheader("📋 Inventario Completo")
st.dataframe(df_inv, use_container_width=True)
