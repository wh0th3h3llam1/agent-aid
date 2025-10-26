/**
 * Mock Supplier - Simulates supply agent responses for local testing
 */

import express from 'express';

const app = express();
app.use(express.json());

const PORT = 8001;

// Mock inventory
const inventory = {
  'blankets': { available: 500, price: 15, unit: 'each' },
  'water bottles': { available: 1000, price: 2, unit: 'bottle' },
  'medical supplies': { available: 200, price: 50, unit: 'kit' },
  'food supplies': { available: 800, price: 10, unit: 'meal' },
  'tents': { available: 50, price: 150, unit: 'each' },
  'clothing': { available: 300, price: 20, unit: 'set' }
};

// Generate mock quote
function generateQuote(items, location, priority) {
  const quotes = [];
  
  items.forEach(item => {
    const itemLower = item.toLowerCase();
    let itemData = null;
    
    // Find matching item in inventory
    for (const [key, value] of Object.entries(inventory)) {
      if (itemLower.includes(key) || key.includes(itemLower)) {
        itemData = { name: key, ...value };
        break;
      }
    }
    
    if (itemData) {
      const quantity = Math.min(100, itemData.available); // Offer up to 100 units
      const basePrice = itemData.price * quantity;
      
      // Priority discount
      const priorityMultiplier = {
        'critical': 0.90,
        'high': 0.95,
        'medium': 1.00,
        'low': 1.05
      }[priority.toLowerCase()] || 1.00;
      
      const totalPrice = basePrice * priorityMultiplier;
      
      // Calculate ETA (mock)
      const distance = 25; // km
      const eta = 1.5 + (distance / 40); // hours
      
      quotes.push({
        supplier: 'Mock Supplier - SF Depot',
        item: itemData.name,
        quantity_offered: quantity,
        unit_price: itemData.price,
        total_price: totalPrice.toFixed(2),
        delivery_location: location,
        eta_hours: eta.toFixed(1),
        priority: priority,
        coverage: '100%',
        available: itemData.available
      });
    }
  });
  
  return quotes;
}

// Endpoint to receive quote requests
app.post('/quote', (req, res) => {
  const { items, location, priority, request_id } = req.body;
  
  console.log(`\n📦 Quote Request Received:`);
  console.log(`   Request ID: ${request_id}`);
  console.log(`   Items: ${items.join(', ')}`);
  console.log(`   Location: ${location}`);
  console.log(`   Priority: ${priority}`);
  
  // Generate quotes
  const quotes = generateQuote(items, location, priority);
  
  console.log(`✅ Generated ${quotes.length} quote(s)`);
  
  // Send quotes back
  res.json({
    success: true,
    supplier: 'Mock Supplier',
    request_id,
    quotes,
    timestamp: new Date().toISOString()
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', supplier: 'Mock Supplier', inventory_items: Object.keys(inventory).length });
});

// Inventory endpoint
app.get('/inventory', (req, res) => {
  res.json({ inventory });
});

app.listen(PORT, () => {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`📦 Mock Supplier Service`);
  console.log(`${'='.repeat(70)}`);
  console.log(`   Port: ${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Inventory: http://localhost:${PORT}/inventory`);
  console.log(`   Quote: POST http://localhost:${PORT}/quote`);
  console.log(`${'='.repeat(70)}`);
  console.log(`✅ Ready to provide quotes!\n`);
});
