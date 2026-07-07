
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# 1️⃣ FIRST: Configure page layout
st.set_page_config(page_title="Enterprise Logistics Dashboard", page_icon="📦", layout="wide")

DB_URL = st.secrets["DB_URL"]

# --- NEW DATA READ/WRITE FUNCTIONS ---

def load_sql_data():
    try:
        conn = psycopg2.connect(DB_URL)
        # 🛒 UPDATED: Added price and stock_quantity to the query selector
        query = "SELECT record_id, name, status, price, stock_quantity, details, last_updated FROM inventory;"
        df_raw = pd.read_sql_query(query, conn)
        conn.close()
        
        if df_raw.empty: return pd.DataFrame()
        
        rows = []
        for _, row in df_raw.iterrows():
            status_str = str(row["status"])
            if "out" in status_str.lower(): emoji = "🔴 Out of Stock"
            elif "low" in status_str.lower(): emoji = "🟡 Low Stock"
            else: emoji = "🟢 In Stock"
            
            # 🛒 UPDATED: Appended Commercial fields directly into your layout structure
            rows.append({
                "SKU / Record ID": row["record_id"],
                "Asset Name": row["name"],
                "Logistics Status": emoji,
                "Price ($)": float(row["price"] or 0.0),
                "Stock Qty": int(row["stock_quantity"] or 0),
                "Warehouse Location / Notes": row["details"],
                "Synchronization Timestamp": row["last_updated"]
            })
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"❌ Error de conexión o consulta SQL: {e}")
        return pd.DataFrame()

# Updated to read live from your new Supabase audit_logs table!
def load_logs():
    try:
        conn = psycopg2.connect(DB_URL)
        query = "SELECT timestamp, event FROM audit_logs ORDER BY timestamp DESC LIMIT 10;"
        df_logs = pd.read_sql_query(query, conn)
        conn.close()
        return df_logs.to_dict(orient="records")
    except:
        return []

# New function to write state updates back to Supabase and log the event!
# 🛒 UPDATED: Accepting pricing and stock counts directly to pass down the server pipeline
def update_inventory_item(sku, status, price, stock, details):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # 🛒 UPDATED: Altered update parameters to handle numeric stock items
        cur.execute(
            "UPDATE inventory SET status = %s, price = %s, stock_quantity = %s, details = %s, last_updated = NOW() WHERE record_id = %s;",
            (status, price, stock, details, sku)
        )
        
        # Write the transaction event into your fresh audit_logs table
        log_msg = f"SKU updated to '{status}' (Price: ${price}, Stock: {stock}) with notes: '{details}'"
        cur.execute(
            "INSERT INTO audit_logs (event, sku) VALUES (%s, %s);",
            (log_msg, sku)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.sidebar.error(f"Write-back failed: {e}")
        return False

# Pull initial cluster state
df = load_sql_data()
logs = load_logs()

# --- INTERFACE STRUCTURING ---
st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><h1>🏭 Production Logistics SQL Ledger Control Panel</h1></div>", unsafe_allow_html=True)
st.caption("Active Production Node linked live via Supabase PostgreSQL Cloud Cluster Datamesh Engine.")

st.markdown("---")

# --- NEW SIDEBAR WRITE-BACK HUB ---
with st.sidebar:
    st.markdown("### 🔄 Operational Command Hub")
    with st.form("inventory_update_form", clear_on_submit=True):
        sku_to_update = st.text_input("Target SKU / Record ID", placeholder="e.g. SKU101")
        new_status = st.selectbox("New Status Value", ["In Stock", "Low Stock", "Out of Stock"])
        
        # 🛒 UPDATED: Added interactive retail field components to the sidebar form layout
        new_price = st.number_input("Unit Selling Price ($)", min_value=0.00, value=0.00, step=0.01, format="%.2f")
        new_stock = st.number_input("Physical Units in Stock", min_value=0, value=0, step=1)
        
        new_notes = st.text_area("Update Warehouse Notes", placeholder="Include location adjustments or alerts...")
        
        submit_update = st.form_submit_button("Commit Changes to Cluster")
        
        if submit_update:
            if not sku_to_update:
                st.error("Please provide a valid Target SKU ID.")
            else:
                with st.spinner("Synchronizing transaction metrics..."):
                    # 🛒 UPDATED: Pushed variables to database engine wrapper function
                    success = update_inventory_item(sku_to_update, new_status, new_price, new_stock, new_notes)
                    if success:
                        st.success(f"SKU {sku_to_update} successfully mutated.")
                        st.rerun() # Refresh layout instantly to showcase changes

if df.empty:
    st.info("👋 Supabase Cloud Database is initialized but empty. Command Claude via your local tool config to inject live elements.")
else:
    # --- STATS ROW ---
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        # 🛒 UPDATED: Total pipeline value inventory metric tracker!
        total_val = (df["Price ($)"] * df["Stock Qty"]).sum()
        with col1: st.metric("Cloud Assets Indexed", len(df))
        with col2: st.metric("Total Warehouse Value", f"${total_val:,.2f}")
        with col3: st.metric("Depleted Supply Nodes", len(df[df['Logistics Status'].str.contains('🔴')]))
        with col4: st.metric("Database Health", "Supabase Connected ✅")

    st.markdown("### 📊 Real-time Relational Data Mesh")
    c_col1, c_col2 = st.columns([1, 1])
    
    with c_col1:
        status_counts = df['Logistics Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', hole=0.4,
                     color_discrete_map={"🟢 In Stock":"#2ecc71","🟡 Low Stock":"#f1c40f","🔴 Out of Stock":"#e74c3c"})
        fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=230)
        st.plotly_chart(fig, use_container_width=True)
        
    with c_col2:
        st.write("**⚠️ High Metric Supply Risk Priority Matrix**")
        watchlist = df[df['Logistics Status'].str.contains('🟡|🔴')]
        if not watchlist.empty:
            st.dataframe(watchlist[['SKU / Record ID', 'Asset Name', 'Logistics Status', 'Stock Qty']], hide_index=True, use_container_width=True)
        else:
            st.success("✨ Supply chains optimal. Zero cloud network latency anomalies recorded.")

    st.markdown("---")
    
    # --- DATA GRID ---
    st.markdown("### 🗂️ Live Supabase Data Engine Registry View")
    search = st.text_input("🔍 Filter row indexes instantaneously...", "")
    filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)

# --- AUDIT STREAM TRAIL PANEL ---
st.markdown("---")
st.markdown("### 📜 Real-Time SQL Engine Transaction Logs")
if logs:
    with st.container(height=180, border=True):
        for log in logs:
            st.markdown(f"⏱️ `{log['timestamp']}` — **{log['event']}**")
else:
    st.text("No data logs recorded in the session cloud pathway yet.")

if st.button("🔄 Force Interface Redraw"): st.rerun()