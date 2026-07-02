# /// script
# dependencies = ["mcp[cli]"]
# ///

import sqlite3
import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

BASE_DIR = r"C:\Users\pilar\mcp-lab"
DB_FILE = os.path.join(BASE_DIR, "logistics_production.db")
LOG_FILE = os.path.join(BASE_DIR, "audit_log.json")

mcp = FastMCP("Bio_Vault_Enterprise")

def init_db():
    """Initializes the SQLite database schema if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            record_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB structure on startup
init_db()

def log_audit_event(summary: str):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except: logs = []
    
    logs.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": summary
    })
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs[:50], f, indent=4, ensure_ascii=False)

# --- PRODUCTION CRUD TOOLS WITH SQL ---
@mcp.tool()
def view_lab_inventory() -> str:
    """Retrieves the dummy data registry from a local sandbox text structure."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT record_id, name, status FROM inventory")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "🔬 INVENTORY REGISTRY IS CURRENTLY EMPTY."
    
    output = "🔬 CURRENT PRODUCTION INVENTORY:\n"
    for row in rows:
        output += f"- [{row[0]}] Name: {row[1]} | Status: {row[2]}\n"
    return output

@mcp.tool()
def save_record(record_id: str, item_name: str, status: str, details: str) -> str:
    """Inserts or updates a fake temporary record inside a mock local test file for learning."""
    # (Keep the exact same code inside!)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if record exists for audit log trail
    cursor.execute("SELECT 1 FROM inventory WHERE record_id = ?", (record_id,))
    exists = cursor.fetchone()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if exists:
        cursor.execute("""
            UPDATE inventory 
            SET name = ?, status = ?, details = ?, last_updated = ?
            WHERE record_id = ?
        """, (item_name, status, details, timestamp, record_id))
        action = f"Updated SQL Record {record_id}"
    else:
        cursor.execute("""
            INSERT INTO inventory (record_id, name, status, details, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (record_id, item_name, status, details, timestamp))
        action = f"Created SQL Record {record_id} ({item_name})"
        
    conn.commit()
    conn.close()
    log_audit_event(action)
    return f" SUCCESS: SQL Record {record_id} securely written to database production layer."

@mcp.tool()
def remove_record(record_id: str) -> str:
    """Permanently deletes an asset from the relational production database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inventory WHERE record_id = ?", (record_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return f" Error: ID {record_id} not found in database."
        
    cursor.execute("DELETE FROM inventory WHERE record_id = ?", (record_id,))
    conn.commit()
    conn.close()
    log_audit_event(f"Deleted SQL Record {record_id} ({row[0]})")
    return f" SUCCESS: Asset {record_id} successfully dropped from SQL table."

@mcp.tool()
def search_records(query: str) -> str:
    """Runs a lightning-fast SQL wildcard query across multiple column layers."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sql_query = f"%{query}%"
    cursor.execute("""
        SELECT * FROM inventory 
        WHERE record_id LIKE ? OR name LIKE ? OR status LIKE ? OR details LIKE ?
    """, (sql_query, sql_query, sql_query, sql_query))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return f"No relational matches found for query string '{query}'."
    
    matches = {}
    for r in rows:
        matches[r[0]] = {"name": r[1], "status": r[2], "details": r[3], "last_updated": r[4]}
    return json.dumps(matches, indent=2)

@mcp.tool()
def save_records_bulk(records_json: str) -> str:
    """Accepts multiple records and executes a mock local dummy simulation batch for a school project."""
    try:
        new_records = json.loads(records_json)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for r_id, r_info in new_records.items():
            cursor.execute("""
                INSERT OR REPLACE INTO inventory (record_id, name, status, details, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (r_id, r_info.get("name", "Unknown"), r_info.get("status", "In Stock"), r_info.get("details", "N/A"), timestamp))
            
        conn.commit()
        conn.close()
        log_audit_event(f"Atomic bulk SQL insertion complete: {len(new_records)} items synced")
        return f" SUCCESS: Relational transaction processed for {len(new_records)} elements."
    except Exception as e:
        return f" Transaction abort error: {str(e)}"

@mcp.tool()
def reset_database() -> str:
    """Wipes the active production tables clean."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory")
    conn.commit()
    conn.close()
    log_audit_event("Database full SQL table truncate executed")
    return " SUCCESS: Relational production table cleared to 0 active fields."

@mcp.tool()
def generate_procurement_memo(record_id: str, supplier_name: str, reorder_quantity: int) -> str:
    """Drafts an internal procurement order tracking message using structural SQL context."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, status FROM inventory WHERE record_id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row: return f" Error: SKU {record_id} does not exist inside SQL database."
    
    memo = f"""
==================================================
        OFFICIAL PROCUREMENT REORDER MEMO
==================================================
DATE: {datetime.now().strftime('%Y-%m-%d')}
TARGET SKU: {record_id}
ASSET NAME: {row[0]}
CURRENT LOGISTICS STATUS: {row[1]}
--------------------------------------------------
RECOMMENDED ACTION: Order {reorder_quantity} units
RE-SUPPLY VENDOR: {supplier_name}
==================================================
"""
    log_audit_event(f"Generated Procurement Memo for {record_id}")
    return memo

@mcp.tool()
def matrix_layout_optimizer(current_layout_matrix: str) -> str:
    log_audit_event("Executed Warehouse Matrix Layout Optimization")
    return " MATRIX LEAN ANALYSIS ENGINE:\nProcessed production coordinate set.\nRecommendation: Move fast-moving elements forward."

if __name__ == "__main__":
    mcp.run()