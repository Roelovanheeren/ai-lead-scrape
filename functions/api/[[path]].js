/**
 * Cloudflare Pages Function - API Proxy
 * This function proxies API requests to the Python backend
 */

export async function onRequest(context) {
  const { request, env } = context;
  
  // Get the API backend URL from environment variable or use Railway as fallback
  const BACKEND_URL = env.BACKEND_URL || 'https://ai-lead-scrape-production.up.railway.app';
  
  // Extract the path from the request
  const url = new URL(request.url);
  const apiPath = url.pathname.replace('/api', '');
  const targetUrl = `${BACKEND_URL}${apiPath}${url.search}`;
  
  console.log(`Proxying request to: ${targetUrl}`);
  
  // Forward the request to the backend
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? await request.text() : undefined,
    });
    
    // Clone the response and add CORS headers
    const modifiedResponse = new Response(response.body, response);
    modifiedResponse.headers.set('Access-Control-Allow-Origin', '*');
    modifiedResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    modifiedResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    return modifiedResponse;
  } catch (error) {
    console.error('Proxy error:', error);
    return new Response(JSON.stringify({ 
      error: 'Backend unavailable', 
      message: error.message 
    }), {
      status: 502,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }
}

// Handle OPTIONS requests for CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
