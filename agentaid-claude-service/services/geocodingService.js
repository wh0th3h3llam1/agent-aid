import dotenv from 'dotenv';

dotenv.config();

// You can use OpenCage (free) or Google Maps
const GEOCODING_PROVIDER = process.env.GEOCODING_PROVIDER || 'opencage'; // or 'google'
const OPENCAGE_API_KEY = process.env.OPENCAGE_API_KEY;
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

// OpenCage Geocoding (Free tier: 2,500 requests/day)
async function geocodeWithOpenCage(address) {
  try {
    const encodedAddress = encodeURIComponent(address);
    const url = `https://api.opencagedata.com/geocode/v1/json?q=${encodedAddress}&key=${OPENCAGE_API_KEY}&limit=1`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      const result = data.results[0];
      return {
        latitude: result.geometry.lat,
        longitude: result.geometry.lng,
        formatted_address: result.formatted,
        confidence: result.confidence,
        components: {
          city: result.components.city || result.components.town,
          state: result.components.state,
          country: result.components.country,
          postcode: result.components.postcode
        }
      };
    }
    
    return null;
  } catch (error) {
    console.error('OpenCage geocoding error:', error);
    return null;
  }
}

// Google Maps Geocoding (Paid, but more accurate)
async function geocodeWithGoogle(address) {
  try {
    const encodedAddress = encodeURIComponent(address);
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodedAddress}&key=${GOOGLE_MAPS_API_KEY}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      const result = data.results[0];
      return {
        latitude: result.geometry.location.lat,
        longitude: result.geometry.location.lng,
        formatted_address: result.formatted_address,
        place_id: result.place_id,
        components: {
          city: result.address_components.find(c => c.types.includes('locality'))?.long_name,
          state: result.address_components.find(c => c.types.includes('administrative_area_level_1'))?.long_name,
          country: result.address_components.find(c => c.types.includes('country'))?.long_name,
          postcode: result.address_components.find(c => c.types.includes('postal_code'))?.long_name
        }
      };
    }
    
    return null;
  } catch (error) {
    console.error('Google geocoding error:', error);
    return null;
  }
}

// Fallback: Simple geocoding using Nominatim (OpenStreetMap - Free, no API key)
async function geocodeWithNominatim(address) {
  try {
    const encodedAddress = encodeURIComponent(address);
    const url = `https://nominatim.openstreetmap.org/search?q=${encodedAddress}&format=json&limit=1`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'AgentAid-DisasterResponse/1.0' // Required by Nominatim
      }
    });
    
    const data = await response.json();
    
    if (data && data.length > 0) {
      const result = data[0];
      return {
        latitude: parseFloat(result.lat),
        longitude: parseFloat(result.lon),
        formatted_address: result.display_name,
        confidence: 0.8, // Nominatim doesn't provide confidence
        components: {
          city: result.address?.city || result.address?.town,
          state: result.address?.state,
          country: result.address?.country,
          postcode: result.address?.postcode
        }
      };
    }
    
    return null;
  } catch (error) {
    console.error('Nominatim geocoding error:', error);
    return null;
  }
}

// Main geocoding function
export async function geocodeAddress(address) {
  if (!address || address.trim().length < 5) {
    console.log('⚠️  Address too short for geocoding');
    return null;
  }
  
  console.log(`🌍 Geocoding address: "${address}"`);
  
  try {
    let result = null;
    
    // Try primary provider
    if (GEOCODING_PROVIDER === 'google' && GOOGLE_MAPS_API_KEY) {
      result = await geocodeWithGoogle(address);
    } else if (GEOCODING_PROVIDER === 'opencage' && OPENCAGE_API_KEY) {
      result = await geocodeWithOpenCage(address);
    } else {
      // Fallback to free Nominatim
      console.log('📍 Using Nominatim (free, no API key)');
      result = await geocodeWithNominatim(address);
    }
    
    if (result) {
      console.log(`✅ Geocoded: ${result.latitude}, ${result.longitude}`);
      return result;
    }
    
    console.log('⚠️  Could not geocode address');
    return null;
    
  } catch (error) {
    console.error('❌ Geocoding error:', error);
    return null;
  }
}

// Calculate distance between two coordinates (in kilometers)
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  
  return distance;
}

function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

// Find nearest location from a list
export function findNearestLocation(targetLat, targetLon, locations) {
  if (!locations || locations.length === 0) return null;
  
  let nearest = null;
  let minDistance = Infinity;
  
  for (const location of locations) {
    if (location.latitude && location.longitude) {
      const distance = calculateDistance(
        targetLat,
        targetLon,
        location.latitude,
        location.longitude
      );
      
      if (distance < minDistance) {
        minDistance = distance;
        nearest = { ...location, distance };
      }
    }
  }
  
  return nearest;
}

// Batch geocode multiple addresses
export async function batchGeocode(addresses) {
  const results = [];
  
  for (const address of addresses) {
    const result = await geocodeAddress(address);
    results.push({
      address: address,
      geocoded: result
    });
    
    // Rate limiting: wait 1 second between requests (for free APIs)
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  return results;
}