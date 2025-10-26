#!/usr/bin/env python3
"""
Setup fresh suppliers with inventory
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "agentaid-marketplace"))

from services.inventory_db import connect, add_inventory_item, get_supplier_config

DB_PATH = "agentaid-marketplace/db/agent_aid.db"

def setup_suppliers():
    """Setup two suppliers with inventory"""
    conn = connect(DB_PATH)
    
    print("🏥 Setting up Supplier 1: Medical Emergency Depot")
    medical = get_supplier_config(conn, "medical_emergency_depot")
    
    if medical:
        medical_id = medical["id"]
        
        # Add medical supplies
        add_inventory_item(conn, medical_id, "blankets", 300, "unit", 30.0, "emergency")
        add_inventory_item(conn, medical_id, "first aid kit", 100, "kit", 50.0, "medical")
        add_inventory_item(conn, medical_id, "water bottles", 500, "bottle", 2.0, "supplies")
        add_inventory_item(conn, medical_id, "flashlight", 150, "unit", 15.0, "equipment")
        
        print("   ✅ Added inventory:")
        print("      - 300 blankets @ $30 each")
        print("      - 100 first aid kits @ $50 each")
        print("      - 500 water bottles @ $2 each")
        print("      - 150 flashlights @ $15 each")
    
    print("\n🏪 Setting up Supplier 2: Community Relief Center")
    community = get_supplier_config(conn, "community_relief_center")
    
    if community:
        community_id = community["id"]
        
        # Add community supplies
        add_inventory_item(conn, community_id, "blankets", 150, "unit", 25.0, "emergency")
        add_inventory_item(conn, community_id, "food packages", 200, "package", 20.0, "food")
        add_inventory_item(conn, community_id, "water bottles", 300, "bottle", 1.5, "supplies")
        add_inventory_item(conn, community_id, "clothing sets", 80, "set", 35.0, "clothing")
        
        print("   ✅ Added inventory:")
        print("      - 150 blankets @ $25 each")
        print("      - 200 food packages @ $20 each")
        print("      - 300 water bottles @ $1.50 each")
        print("      - 80 clothing sets @ $35 each")
    
    # Verify
    print("\n📊 Verification:")
    cursor = conn.execute("""
        SELECT s.label, COUNT(i.id) as item_types, SUM(i.qty) as total_units
        FROM suppliers s
        LEFT JOIN items i ON s.id = i.supplier_id
        GROUP BY s.id
        ORDER BY s.label
    """)
    
    for row in cursor.fetchall():
        print(f"   {row['label']}: {row['item_types']} types, {row['total_units']} units")
    
    conn.close()
    print("\n✅ Suppliers setup complete!")
    return True

if __name__ == "__main__":
    success = setup_suppliers()
    sys.exit(0 if success else 1)
