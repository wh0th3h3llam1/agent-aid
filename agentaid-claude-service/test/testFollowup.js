async function testFollowupSystem() {
  console.log('🧪 Testing Follow-up System\n');
  console.log('='.repeat(80));

  // Test 1: Vague medicine request
  console.log('\n1️⃣ Test: Vague Medicine Request\n');
  
  const vagueRequest = await fetch('http://localhost:3000/api/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: 'We need medicine urgently',
      source: 'test'
    })
  });

  const vagueResult = await vagueRequest.json();
  
  if (vagueResult.needs_followup) {
    console.log('✅ Follow-up triggered correctly');
    console.log(`   Completeness: ${vagueResult.completeness_score}%`);
    console.log(`   Session ID: ${vagueResult.session_id}`);
    console.log(`   Issues: ${vagueResult.issues.length}`);
    console.log('\n   Follow-up Message:');
    console.log(`   "${vagueResult.followup_message}"`);
    
    // Test follow-up response
    console.log('\n   Simulating follow-up response...\n');
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const followupResponse = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: 'We need insulin and bandages, about 50 units of insulin and 100 bandages. Contact: 555-1234. Location: 123 Main Street, Room 5',
        source: 'test',
        session_id: vagueResult.session_id
      })
    });

    const followupResult = await followupResponse.json();
    
    if (followupResult.follow_up_completed) {
      console.log('✅ Follow-up completed successfully');
      console.log('   Final Data:');
      console.log(JSON.stringify(followupResult.data, null, 2));
    }
  }

  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test 2: Missing contact info
  console.log('\n\n2️⃣ Test: Missing Contact Info\n');
  
  const noContactRequest = await fetch('http://localhost:3000/api/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: 'Need 50 tents at shelter',
      source: 'test'
    })
  });

  const noContactResult = await noContactRequest.json();
  
  if (noContactResult.needs_followup) {
    console.log('✅ Follow-up triggered for missing contact');
    console.log(`   Completeness: ${noContactResult.completeness_score}%`);
    console.log('\n   Follow-up Message:');
    console.log(`   "${noContactResult.followup_message}"`);
  }

  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test 3: Complete information (no follow-up)
  console.log('\n\n3️⃣ Test: Complete Information\n');
  
  const completeRequest = await fetch('http://localhost:3000/api/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: 'URGENT: Need 50 tents and 200 bottles of water at Main Street Community Center, 123 Main St. Contact John at 555-1234. 75 people here.',
      source: 'test'
    })
  });

  const completeResult = await completeRequest.json();
  
  if (!completeResult.needs_followup) {
    console.log('✅ No follow-up needed - data is complete');
    console.log(`   Request ID: ${completeResult.data.request_id}`);
    console.log(`   Items: ${completeResult.data.items}`);
    console.log(`   Contact: ${completeResult.data.contact}`);
    console.log(`   Location: ${completeResult.data.location}`);
  }

  console.log('\n' + '='.repeat(80));
  console.log('\n✨ Follow-up System Test Complete!\n');
}

testFollowupSystem();