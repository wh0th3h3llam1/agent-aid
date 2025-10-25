const testCases = [
  {
    name: "🚨 Critical Medical Emergency",
    input: "URGENT: Building collapsed at 789 Market Street. 15 injured people trapped. Need medical supplies, rescue equipment, ambulances!",
    expectedPriority: "critical"
  },
  {
    name: "👨‍👩‍👧 Family with Baby",
    input: "My family needs baby food, diapers, and formula. We're at 456 Oak Avenue with a 6-month-old baby. Running out of supplies.",
    expectedPriority: "high"
  },
  {
    name: "🏫 School Shelter",
    input: "Community shelter at Lincoln High School needs 100 blankets, food for 50 people. Contact: John at 555-1234",
    expectedPriority: "medium"
  },
  {
    name: "🇪🇸 Spanish Request",
    input: "Necesitamos ayuda urgente. Somos 30 familias sin comida ni agua en la escuela.",
    expectedPriority: "high"
  },
  {
    name: "🎙️ Voice-like Input",
    input: "Hello this is emergency we are at the old warehouse near the river about 20 people here we need water food some people injured please send help",
    expectedPriority: "high"
  }
];

async function runFullDemo() {
  console.log('🚀 Starting AgentAid Claude Service Demo\n');
  console.log('=' .repeat(80));

  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i];
    console.log(`\n${i + 1}. ${testCase.name}`);
    console.log('-'.repeat(80));
    console.log(`📥 Input: "${testCase.input}"\n`);

    try {
      const response = await fetch('http://localhost:3000/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          input: testCase.input,
          source: 'demo'
        })
      });

      const result = await response.json();

      if (result.success) {
        const data = result.data;
        
        console.log('✅ Extraction Successful!');
        console.log(`   Request ID: ${data.request_id}`);
        console.log(`   Priority: ${data.priority.toUpperCase()}`);
        console.log(`   Items: ${data.items.join(', ')}`);
        console.log(`   Location: ${data.location}`);
        console.log(`   Victim Count: ${data.victim_count || 'Not specified'}`);
        
        if (data.priority === testCase.expectedPriority) {
          console.log(`   ✓ Priority matches expected (${testCase.expectedPriority})`);
        }
      } else {
        console.log(`❌ Error: ${result.error}`);
      }

      // Wait 2 seconds between requests
      await new Promise(resolve => setTimeout(resolve, 2000));

    } catch (error) {
      console.log(`❌ Network Error: ${error.message}`);
    }
  }

  console.log('\n' + '='.repeat(80));
  console.log('📊 Fetching summary statistics...\n');

  try {
    const statsResponse = await fetch('http://localhost:3000/api/requests');
    const stats = await statsResponse.json();

    console.log(`Total Requests Processed: ${stats.total}`);
    console.log('\nBy Priority:');
    console.log(`  🔴 Critical: ${stats.by_priority.critical}`);
    console.log(`  🟠 High: ${stats.by_priority.high}`);
    console.log(`  🟡 Medium: ${stats.by_priority.medium}`);
    console.log(`  🟢 Low: ${stats.by_priority.low}`);
  } catch (error) {
    console.log(`❌ Could not fetch stats: ${error.message}`);
  }

  console.log('\n✨ Demo Complete!\n');
}

runFullDemo();