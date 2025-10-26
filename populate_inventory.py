#!/usr/bin/env python3
"""
Populate inventory for dummy suppliers
"""
import sys
from pathlib import Path

# Add the marketplace to the path
sys.path.insert(0, str(Path(__file__).parent / "agentaid-marketplace"))

from services.inventory_db import connect, add_inventory_item, get_supplier_config

DB_PATH = "agentaid-marketplace/db/agent_aid.db"

def populate_inventory():
    """Add inventory items to the dummy suppliers"""
    conn = connect(DB_PATH)
    
    # Get supplier IDs
    emergency_supplier = get_supplier_config(conn, "emergency_medical_fire")
    family_supplier = get_supplier_config(conn, "family_child_emergency")
    
    if not emergency_supplier:
        print("❌ Emergency Medical supplier not found!")
        return False
    
    if not family_supplier:
        print("❌ Family & Child supplier not found!")
        return False
    
    print("🏥 Adding inventory to Emergency Medical & Fire Response Depot...")
    emergency_id = emergency_supplier["id"]
    
    # Emergency Medical inventory
    add_inventory_item(conn, emergency_id, "blankets", 500, "unit", 25.0, "emergency")
    add_inventory_item(conn, emergency_id, "ambulance", 10, "unit", 50000.0, "vehicle")
    add_inventory_item(conn, emergency_id, "burn medicine", 200, "bottle", 45.0, "medical")
    add_inventory_item(conn, emergency_id, "first aid kit", 100, "kit", 35.0, "medical")
    add_inventory_item(conn, emergency_id, "oxygen tank", 50, "tank", 150.0, "medical")
    add_inventory_item(conn, emergency_id, "stretcher", 25, "unit", 200.0, "equipment")
    
    print("✅ Emergency Medical inventory added")
    
    print("👶 Adding inventory to Family & Child Emergency Supplies...")
    family_id = family_supplier["id"]
    
    # Family & Child inventory
    add_inventory_item(conn, family_id, "blankets", 50, "unit", 20.0, "emergency")
    add_inventory_item(conn, family_id, "baby food", 10, "case", 50.0, "food")
    add_inventory_item(conn, family_id, "diapers", 20, "pack", 30.0, "childcare")
    add_inventory_item(conn, family_id, "baby formula", 15, "container", 25.0, "food")
    add_inventory_item(conn, family_id, "baby clothes", 30, "set", 15.0, "clothing")
    add_inventory_item(conn, family_id, "toys", 40, "unit", 10.0, "entertainment")
    
    print("✅ Family & Child inventory added")
    
    # Verify
    print("\n📊 Inventory Summary:")
    cursor = conn.execute("""
        SELECT s.label, COUNT(i.id) as item_count, SUM(i.qty) as total_qty
        FROM suppliers s
        LEFT JOIN items i ON s.id = i.supplier_id
        GROUP BY s.id
        ORDER BY s.label
    """)
    
    for row in cursor.fetchall():
        print(f"   {row['label']}: {row['item_count']} item types, {row['total_qty']} total units")
    
    conn.close()
    print("\n✅ Inventory populated successfully!")
    return True

if __name__ == "__main__":
    success = populate_inventory()
    sys.exit(0 if success else 1)
