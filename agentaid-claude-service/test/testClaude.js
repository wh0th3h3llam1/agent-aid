const testInputs = [
  "We need 50 tents and 200 bottles of water at the community center on Main Street. This is urgent, we have 75 people here!",
  "My family needs baby food and diapers. We're at 456 Oak Avenue. Please help soon.",
  "CRITICAL: Medical supplies needed immediately at County Hospital. Multiple injuries.",
  "Hola, necesitamos comida y agua en el refugio de la escuela. Somos 30 personas."
];

async function testExtraction() {
  for (const input of testInputs) {
    console.log('\n--- Testing Input ---');
    console.log(input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input, source: 'test' })
    });

    const result = await response.json();
    console.log('\n--- Extracted Data ---');
    console.log(JSON.stringify(result, null, 2));
  }
}

testExtraction();