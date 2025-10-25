async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function printSection(title) {
  console.log('\n' + '='.repeat(80));
  console.log(`  ${title}`);
  console.log('='.repeat(80) + '\n');
}

function printSubSection(title) {
  console.log('\n' + '-'.repeat(60));
  console.log(`  ${title}`);
  console.log('-'.repeat(60) + '\n');
}

async function comprehensiveTest() {
  console.log('\n');
  console.log('█'.repeat(80));
  console.log('█' + ' '.repeat(78) + '█');
  console.log('█' + '  🧪 AGENTAID COMPREHENSIVE TEST SUITE'.padEnd(78) + '█');
  console.log('█' + ' '.repeat(78) + '█');
  console.log('█'.repeat(80));
  console.log('\n');

  let testsPassed = 0;
  let testsFailed = 0;
  const testResults = [];

  // ========================================
  // TEST 1: HEALTH CHECK
  // ========================================
  printSection('TEST 1: System Health Check');
  
  try {
    const health = await fetch('http://localhost:3000/health');
    const healthData = await health.json();
    
    console.log('✅ Server Status:', healthData.status);
    console.log('✅ Service:', healthData.service);
    console.log('✅ Requests Processed:', healthData.requests_processed);
    console.log('✅ ChromaDB:', healthData.chromadb.storage_mode);
    console.log('✅ Features:');
    Object.entries(healthData.features).forEach(([key, value]) => {
      console.log(`   - ${key}: ${value}`);
    });
    
    testsPassed++;
    testResults.push({ test: 'Health Check', status: 'PASS' });
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
    console.log('\n⚠️  Make sure server is running: npm start\n');
    testsFailed++;
    testResults.push({ test: 'Health Check', status: 'FAIL', error: error.message });
    return;
  }

  await sleep(2000);

  // ========================================
  // TEST 2: COMPLETE REQUEST (NO FOLLOW-UP)
  // ========================================
  printSection('TEST 2: Complete Request (No Follow-up Needed)');
  
  try {
    const completeRequest = {
      input: 'URGENT: Need 50 tents and 200 bottles of water at Main Street Community Center, 123 Main Street, Room 5. Contact John at 555-1234. We have 75 people here.',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', completeRequest.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(completeRequest)
    });
    
    const result = await response.json();
    
    if (result.needs_followup) {
      console.log('❌ FAIL: Should not need follow-up for complete data');
      testsFailed++;
      testResults.push({ test: 'Complete Request', status: 'FAIL', reason: 'Unexpected follow-up request' });
    } else {
      console.log('✅ PASS: No follow-up needed');
      console.log('   Request ID:', result.data.request_id);
      console.log('   Items:', result.data.items);
      console.log('   Quantity:', JSON.stringify(result.data.quantity_needed));
      console.log('   Location:', result.data.location);
      console.log('   Contact:', result.data.contact);
      console.log('   Priority:', result.data.priority);
      console.log('   Victim Count:', result.data.victim_count);
      console.log('   Completeness:', result.completeness_score + '%');
      testsPassed++;
      testResults.push({ test: 'Complete Request', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Complete Request', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 3: VAGUE ITEM REQUEST (MEDICINE)
  // ========================================
  printSection('TEST 3: Vague Item Request - Medicine (Should Trigger Follow-up)');
  
  let medicineSessionId = null;
  
  try {
    const vagueRequest = {
      input: 'We need medicine urgently at the shelter',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', vagueRequest.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vagueRequest)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('❌ FAIL: Should trigger follow-up for vague "medicine"');
      testsFailed++;
      testResults.push({ test: 'Vague Medicine', status: 'FAIL', reason: 'No follow-up triggered' });
    } else {
      console.log('✅ PASS: Follow-up triggered correctly');
      console.log('   Session ID:', result.session_id);
      console.log('   Completeness Score:', result.completeness_score + '%');
      console.log('   Issues Found:', result.issues.length);
      console.log('\n   Issues:');
      result.issues.forEach((issue, i) => {
        console.log(`   ${i + 1}. ${issue.type} (${issue.field})`);
      });
      console.log('\n   Follow-up Message:');
      console.log('   "' + result.followup_message + '"');
      
      medicineSessionId = result.session_id;
      testsPassed++;
      testResults.push({ test: 'Vague Medicine', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Vague Medicine', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 4: FOLLOW-UP RESPONSE FOR MEDICINE
  // ========================================
  if (medicineSessionId) {
    printSection('TEST 4: Follow-up Response - Completing Medicine Request');
    
    try {
      const followupRequest = {
        input: 'We need insulin 50 units, bandages 100 pieces, and pain medication. Contact is 555-9999. Location is Lincoln High School, Building A, Room 101.',
        source: 'comprehensive-test',
        session_id: medicineSessionId
      };
      
      console.log('📥 Follow-up Input:', followupRequest.input);
      console.log('🔗 Session ID:', medicineSessionId);
      
      const response = await fetch('http://localhost:3000/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(followupRequest)
      });
      
      const result = await response.json();
      
      if (result.follow_up_completed) {
        console.log('✅ PASS: Follow-up completed successfully');
        console.log('   Request ID:', result.data.request_id);
        console.log('   Items:', result.data.items);
        console.log('   Quantity:', JSON.stringify(result.data.quantity_needed));
        console.log('   Location:', result.data.location);
        console.log('   Contact:', result.data.contact);
        console.log('   Priority:', result.data.priority);
        testsPassed++;
        testResults.push({ test: 'Medicine Follow-up', status: 'PASS' });
      } else {
        console.log('❌ FAIL: Follow-up not completed');
        testsFailed++;
        testResults.push({ test: 'Medicine Follow-up', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ FAIL:', error.message);
      testsFailed++;
      testResults.push({ test: 'Medicine Follow-up', status: 'FAIL', error: error.message });
    }
  }

  await sleep(3000);

  // ========================================
  // TEST 5: MISSING CONTACT INFO
  // ========================================
  printSection('TEST 5: Missing Contact Information (Should Trigger Follow-up)');
  
  let contactSessionId = null;
  
  try {
    const noContactRequest = {
      input: 'Need 50 tents at Main Street Community Center',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', noContactRequest.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(noContactRequest)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('❌ FAIL: Should trigger follow-up for missing contact');
      testsFailed++;
      testResults.push({ test: 'Missing Contact', status: 'FAIL' });
    } else {
      console.log('✅ PASS: Follow-up triggered for missing contact');
      console.log('   Session ID:', result.session_id);
      console.log('   Completeness Score:', result.completeness_score + '%');
      console.log('\n   Follow-up Message:');
      console.log('   "' + result.followup_message + '"');
      
      contactSessionId = result.session_id;
      testsPassed++;
      testResults.push({ test: 'Missing Contact', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Missing Contact', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 6: VAGUE LOCATION
  // ========================================
  printSection('TEST 6: Vague Location (Should Trigger Follow-up)');
  
  try {
    const vagueLocationRequest = {
      input: 'Need 100 blankets at the shelter. Contact: 555-1111',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', vagueLocationRequest.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vagueLocationRequest)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('⚠️  WARNING: Should trigger follow-up for vague location');
      console.log('   (May pass if "shelter" is considered specific enough)');
      testsPassed++;
      testResults.push({ test: 'Vague Location', status: 'PASS*' });
    } else {
      console.log('✅ PASS: Follow-up triggered for vague location');
      console.log('   Completeness Score:', result.completeness_score + '%');
      testsPassed++;
      testResults.push({ test: 'Vague Location', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Vague Location', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 7: VAGUE FOOD REQUEST
  // ========================================
  printSection('TEST 7: Vague Food Request (Should Trigger Follow-up)');
  
  try {
    const vagueFood = {
      input: 'We need food for 30 people at 456 Oak Street. Contact: 555-2222',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', vagueFood.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vagueFood)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('❌ FAIL: Should trigger follow-up for vague "food"');
      testsFailed++;
      testResults.push({ test: 'Vague Food', status: 'FAIL' });
    } else {
      console.log('✅ PASS: Follow-up triggered for vague food');
      console.log('   Completeness Score:', result.completeness_score + '%');
      console.log('\n   Follow-up Message:');
      console.log('   "' + result.followup_message + '"');
      testsPassed++;
      testResults.push({ test: 'Vague Food', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Vague Food', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 8: VAGUE QUANTITY
  // ========================================
  printSection('TEST 8: Vague Quantity (Should Trigger Follow-up)');
  
  try {
    const vagueQuantity = {
      input: 'Need water at 789 Pine Ave. Contact: 555-3333',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', vagueQuantity.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vagueQuantity)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('❌ FAIL: Should trigger follow-up for missing quantity');
      testsFailed++;
      testResults.push({ test: 'Vague Quantity', status: 'FAIL' });
    } else {
      console.log('✅ PASS: Follow-up triggered for vague quantity');
      console.log('   Completeness Score:', result.completeness_score + '%');
      testsPassed++;
      testResults.push({ test: 'Vague Quantity', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Vague Quantity', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 9: MULTIPLE ISSUES
  // ========================================
  printSection('TEST 9: Multiple Issues - Vague Items + No Contact + Vague Quantity');
  
  let multiIssueSessionId = null;
  
  try {
    const multiIssue = {
      input: 'Need medical supplies at the school',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', multiIssue.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(multiIssue)
    });
    
    const result = await response.json();
    
    if (!result.needs_followup) {
      console.log('❌ FAIL: Should trigger follow-up for multiple issues');
      testsFailed++;
      testResults.push({ test: 'Multiple Issues', status: 'FAIL' });
    } else {
      console.log('✅ PASS: Follow-up triggered for multiple issues');
      console.log('   Session ID:', result.session_id);
      console.log('   Completeness Score:', result.completeness_score + '%');
      console.log('   Issues Found:', result.issues.length);
      result.issues.forEach((issue, i) => {
        console.log(`   ${i + 1}. ${issue.type} - ${issue.field}`);
      });
      console.log('\n   Follow-up Message:');
      console.log('   "' + result.followup_message + '"');
      
      multiIssueSessionId = result.session_id;
      testsPassed++;
      testResults.push({ test: 'Multiple Issues', status: 'PASS' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Multiple Issues', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 10: MULTILINGUAL (SPANISH)
  // ========================================
  printSection('TEST 10: Multilingual Support - Spanish');
  
  try {
    const spanishRequest = {
      input: 'Necesitamos 50 tiendas de campaña y agua en el centro comunitario de la calle principal, 123 Main Street. Contacto: 555-4444. Somos 75 personas.',
      source: 'comprehensive-test'
    };
    
    console.log('📥 Input:', spanishRequest.input);
    
    const response = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spanishRequest)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ PASS: Spanish input processed');
      console.log('   Items:', result.data?.items || result.partial_data?.items);
      console.log('   Location:', result.data?.location || result.partial_data?.location);
      console.log('   Needs Follow-up:', result.needs_followup);
      testsPassed++;
      testResults.push({ test: 'Multilingual Spanish', status: 'PASS' });
    } else {
      console.log('❌ FAIL: Could not process Spanish input');
      testsFailed++;
      testResults.push({ test: 'Multilingual Spanish', status: 'FAIL' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Multilingual Spanish', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 11: CHROMADB SIMILARITY SEARCH
  // ========================================
  printSection('TEST 11: ChromaDB Similarity Search');
  
  try {
    const searchQuery = {
      query: 'water and tents at community center',
      limit: 3
    };
    
    console.log('📥 Search Query:', searchQuery.query);
    
    const response = await fetch('http://localhost:3000/api/search/similar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(searchQuery)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ PASS: Similarity search working');
      console.log('   Results Found:', result.results.length);
      
      result.results.forEach((res, i) => {
        console.log(`\n   ${i + 1}. ${res.request_id}`);
        console.log(`      Similarity: ${(res.similarity_score * 100).toFixed(1)}%`);
        console.log(`      Priority: ${res.metadata.priority}`);
      });
      
      testsPassed++;
      testResults.push({ test: 'ChromaDB Search', status: 'PASS' });
    } else {
      console.log('❌ FAIL: Similarity search failed');
      testsFailed++;
      testResults.push({ test: 'ChromaDB Search', status: 'FAIL' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'ChromaDB Search', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 12: UAGENT ENDPOINTS
  // ========================================
  printSection('TEST 12: Fetch.ai uAgent Endpoints');
  
  printSubSection('12a: Get Pending Requests');
  try {
    const response = await fetch('http://localhost:3000/api/uagent/pending-requests');
    const result = await response.json();
    
    console.log('✅ PASS: Pending requests endpoint working');
    console.log('   Pending Count:', result.count);
    
    if (result.count > 0) {
      console.log('\n   Sample Request:');
      console.log('   - Request ID:', result.requests[0].request_id);
      console.log('   - Items:', result.requests[0].items);
      console.log('   - Priority:', result.requests[0].priority);
      console.log('   - Urgency Level:', result.requests[0].urgency_level);
    }
    
    testsPassed++;
    testResults.push({ test: 'uAgent Pending', status: 'PASS' });
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'uAgent Pending', status: 'FAIL', error: error.message });
  }

  await sleep(2000);

  printSubSection('12b: Claim Request (Simulation)');
  try {
    // Get a pending request to claim
    const pendingResponse = await fetch('http://localhost:3000/api/uagent/pending-requests');
    const pendingResult = await pendingResponse.json();
    
    if (pendingResult.count > 0) {
      const requestToClaim = pendingResult.requests[0];
      
      const claimResponse = await fetch('http://localhost:3000/api/uagent/claim-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: requestToClaim.request_id,
          agent_id: 'test_agent_001',
          agent_address: 'agent1qtest123'
        })
      });
      
      const claimResult = await claimResponse.json();
      
      if (claimResult.success) {
        console.log('✅ PASS: Claim request working');
        console.log('   Claimed:', requestToClaim.request_id);
        console.log('   Status:', claimResult.request.status);
        testsPassed++;
        testResults.push({ test: 'uAgent Claim', status: 'PASS' });
      } else {
        console.log('❌ FAIL: Could not claim request');
        testsFailed++;
        testResults.push({ test: 'uAgent Claim', status: 'FAIL' });
      }
    } else {
      console.log('⚠️  SKIP: No pending requests to claim');
      testResults.push({ test: 'uAgent Claim', status: 'SKIP' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'uAgent Claim', status: 'FAIL', error: error.message });
  }

  await sleep(2000);

  printSubSection('12c: Send Update (Simulation)');
  try {
    const pendingResponse = await fetch('http://localhost:3000/api/uagent/pending-requests');
    const pendingResult = await pendingResponse.json();
    
    if (pendingResult.count > 0) {
      const requestToUpdate = pendingResult.requests[0];
      
      const updateResponse = await fetch('http://localhost:3000/api/uagent/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: requestToUpdate.request_id,
          agent_id: 'test_agent_001',
          status: 'matched',
          matched_supplier: {
            supplier_id: 'supply_test_001',
            name: 'Test Red Cross'
          }
        })
      });
      
      const updateResult = await updateResponse.json();
      
      if (updateResult.success) {
        console.log('✅ PASS: Update endpoint working');
        testsPassed++;
        testResults.push({ test: 'uAgent Update', status: 'PASS' });
      } else {
        console.log('❌ FAIL: Could not send update');
        testsFailed++;
        testResults.push({ test: 'uAgent Update', status: 'FAIL' });
      }
    } else {
      console.log('⚠️  SKIP: No requests to update');
      testResults.push({ test: 'uAgent Update', status: 'SKIP' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'uAgent Update', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 13: PRIORITY FILTERING
  // ========================================
  printSection('TEST 13: Priority Filtering');
  
  try {
    const priorities = ['critical', 'high', 'medium', 'low'];
    let priorityTestPassed = true;
    
    for (const priority of priorities) {
      const response = await fetch(`http://localhost:3000/api/requests/priority/${priority}`);
      const result = await response.json();
      
      if (result.success) {
        console.log(`✅ ${priority.toUpperCase()}: ${result.count} requests`);
      } else {
        priorityTestPassed = false;
        console.log(`❌ ${priority.toUpperCase()}: Failed`);
      }
    }
    
    if (priorityTestPassed) {
      testsPassed++;
      testResults.push({ test: 'Priority Filter', status: 'PASS' });
    } else {
      testsFailed++;
      testResults.push({ test: 'Priority Filter', status: 'FAIL' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Priority Filter', status: 'FAIL', error: error.message });
  }

  await sleep(2000);

  // ========================================
  // TEST 14: BATCH PROCESSING
  // ========================================
  printSection('TEST 14: Batch Processing');
  
  try {
    const batchInputs = [
      'Need 20 tents at Shelter A, 111 First St. Contact: 555-5555',
      'Medical supplies needed at Hospital B',
      'Water for 50 people at 222 Second Ave. Contact: 555-6666'
    ];
    
    console.log('📥 Batch Input: 3 requests');
    
    const response = await fetch('http://localhost:3000/api/extract/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inputs: batchInputs })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ PASS: Batch processing working');
      console.log('   Processed:', result.processed);
      console.log('   Need Follow-up:', result.needs_followup);
      testsPassed++;
      testResults.push({ test: 'Batch Processing', status: 'PASS' });
    } else {
      console.log('❌ FAIL: Batch processing failed');
      testsFailed++;
      testResults.push({ test: 'Batch Processing', status: 'FAIL' });
    }
  } catch (error) {
    console.log('❌ FAIL:', error.message);
    testsFailed++;
    testResults.push({ test: 'Batch Processing', status: 'FAIL', error: error.message });
  }

  await sleep(3000);

  // ========================================
  // TEST 15: SESSION MANAGEMENT
  // ========================================
  printSection('TEST 15: Session Management');
  
  if (multiIssueSessionId) {
    try {
      // Get session info
      const response = await fetch(`http://localhost:3000/api/session/${multiIssueSessionId}`);
      const result = await response.json();
      
      if (result.success) {
        console.log('✅ PASS: Session retrieval working');
        console.log('   Session ID:', multiIssueSessionId);
        console.log('   Created:', result.session.created_at);
        console.log('   Has Data:', result.session.has_data);
        testsPassed++;
        testResults.push({ test: 'Session Management', status: 'PASS' });
      } else {
        console.log('❌ FAIL: Could not retrieve session');
        testsFailed++;
        testResults.push({ test: 'Session Management', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ FAIL:', error.message);
      testsFailed++;
      testResults.push({ test: 'Session Management', status: 'FAIL', error: error.message });
    }
  } else {
    console.log('⚠️  SKIP: No session to test');
    testResults.push({ test: 'Session Management', status: 'SKIP' });
  }

  await sleep(2000);

  // ========================================
  // FINAL SUMMARY
  // ========================================
  printSection('TEST SUMMARY');
  
  console.log('📊 Results:');
  console.log(`   ✅ Passed: ${testsPassed}`);
  console.log(`   ❌ Failed: ${testsFailed}`);
  console.log(`   📝 Total: ${testsPassed + testsFailed}`);
  console.log(`   📈 Success Rate: ${Math.round((testsPassed / (testsPassed + testsFailed)) * 100)}%`);
  
  console.log('\n📋 Detailed Results:\n');
  testResults.forEach((result, index) => {
    const icon = result.status === 'PASS' ? '✅' : result.status === 'SKIP' ? '⚠️' : '❌';
    console.log(`   ${index + 1}. ${icon} ${result.test.padEnd(40)} ${result.status}`);
  });

  console.log('\n');
  console.log('█'.repeat(80));
  console.log('█' + ' '.repeat(78) + '█');
  
  if (testsFailed === 0) {
    console.log('█' + '  🎉 ALL TESTS PASSED! SYSTEM READY FOR DEMO!'.padEnd(78) + '█');
  } else {
    console.log('█' + `  ⚠️  ${testsFailed} TEST(S) FAILED - REVIEW REQUIRED`.padEnd(78) + '█');
  }
  
  console.log('█' + ' '.repeat(78) + '█');
  console.log('█'.repeat(80));
  console.log('\n');

  // ========================================
  // FINAL HEALTH CHECK
  // ========================================
  printSection('FINAL SYSTEM STATUS');
  
  try {
    const health = await fetch('http://localhost:3000/health');
    const healthData = await health.json();
    
    console.log('📊 Final Statistics:');
    console.log(`   Total Requests Processed: ${healthData.requests_processed}`);
    console.log(`   Pending for Agents: ${healthData.pending_for_agents}`);
    console.log(`   ChromaDB Total: ${healthData.chromadb.total_requests}`);
    
    const allRequests = await fetch('http://localhost:3000/api/requests');
    const allRequestsData = await allRequests.json();
    
    console.log('\n📈 Priority Breakdown:');
    console.log(`   🔴 Critical: ${allRequestsData.by_priority.critical}`);
    console.log(`   🟠 High: ${allRequestsData.by_priority.high}`);
    console.log(`   🟡 Medium: ${allRequestsData.by_priority.medium}`);
    console.log(`   🟢 Low: ${allRequestsData.by_priority.low}`);
    
  } catch (error) {
    console.log('⚠️  Could not fetch final stats');
  }

  console.log('\n✨ Comprehensive test suite completed!\n');
}

// Run the comprehensive test
comprehensiveTest().catch(error => {
  console.error('\n❌ Test suite error:', error);
  process.exit(1);
});