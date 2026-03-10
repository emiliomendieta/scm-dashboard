import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

# ── Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="SCM Dashboard",
    page_icon="📦",
    layout="wide"
)

# ── Conexión a PostgreSQL ────────────────────────────────────
@st.cache_data(ttl=60)
def get_data(query):
    conn = psycopg2.connect(
        host="host.docker.internal",
        database="scm_db",
        user="emilio",
        password="scmlearning123",
        port="5432"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ── Queries ──────────────────────────────────────────────────
query_inventario = """
    SELECT p.sku, p.descripcion, p.categoria,
           i.stock_actual, i.stock_minimo, i.stock_maximo,
           i.stock_actual - i.stock_minimo AS diferencia,
           i.stock_actual * p.precio_unitario AS valor_inventario
    FROM inventario i
    JOIN productos p ON i.id_producto = p.id_producto
    ORDER BY diferencia ASC;
"""

query_categorias = """
    SELECT p.categoria,
           COUNT(*) AS num_productos,
           SUM(i.stock_actual * p.precio_unitario) AS valor_total
    FROM productos p
    JOIN inventario i ON p.id_producto = i.id_producto
    GROUP BY p.categoria
    ORDER BY valor_total DESC;
"""

query_proveedores = """
    SELECT pr.nombre AS proveedor, pr.calificacion,
           COUNT(*) AS num_ordenes,
           SUM(oc.cantidad * oc.precio_unitario) AS valor_total
    FROM proveedores pr
    JOIN ordenes_compra oc ON pr.id_proveedor = oc.id_proveedor
    GROUP BY pr.nombre, pr.calificacion
    ORDER BY valor_total DESC;
"""

# ── Header ───────────────────────────────────────────────────
st.title("📦 SCM Dashboard — Inventario & Proveedores")
st.markdown("Dashboard interactivo de Supply Chain | Emilio Mendieta")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
df_inv = get_data(query_inventario)
df_cat = get_data(query_categorias)
df_prov = get_data(query_proveedores)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Productos", len(df_inv))
col2.metric("Valor Inventario", f"${df_cat['valor_total'].sum():,.0f}")
col3.metric("Productos Bajo Mínimo", len(df_inv[df_inv['diferencia'] < 0]))
col4.metric("Proveedores Activos", len(df_prov))

st.divider()

# ── Alertas de Stockout ───────────────────────────────────────
st.subheader("🚨 Alertas de Stockout")
df_alertas = df_inv[df_inv['diferencia'] < 0][['sku', 'descripcion', 'categoria', 'stock_actual', 'stock_minimo', 'diferencia']]
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

# ── Tabla completa de inventario ──────────────────────────────
st.subheader("📋 Inventario Completo")
st.dataframe(df_inv, use_container_width=True)
