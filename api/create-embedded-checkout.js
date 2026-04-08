// Stripe Embedded Checkout — returns clientSecret for on-page checkout
// No redirect to Stripe or Stan Store — payment form appears inline

export default async function handler(req, res) {
  // CORS headers for embedded checkout
  res.setHeader('Access-Control-Allow-Origin', 'https://enterliminalspace.com');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    return res.status(500).json({ error: 'STRIPE_SECRET_KEY not configured' });
  }

  try {
    const params = new URLSearchParams();
    params.append('mode', 'payment');
    params.append('ui_mode', 'embedded');
    params.append('line_items[0][price_data][currency]', 'usd');
    params.append('line_items[0][price_data][product_data][name]', 'First Contact — Consciousness Exploration Kit');
    params.append('line_items[0][price_data][product_data][description]', '3 guided audio sessions + field manual + 7-day protocol. Instant download.');
    params.append('line_items[0][price_data][unit_amount]', '3700');
    params.append('line_items[0][quantity]', '1');
    params.append('allow_promotion_codes', 'true');
    params.append('return_url', 'https://enterliminalspace.com/checkout-return.html?session_id={CHECKOUT_SESSION_ID}');
    params.append('metadata[product]', 'first_contact');
    params.append('metadata[source]', req.body?.source || 'embedded');

    // Pre-fill email if provided — makes Apple Pay one-tap
    if (req.body?.email) {
      params.append('customer_email', req.body.email);
    }

    const resp = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    const data = await resp.json();

    if (!resp.ok) {
      console.error('Stripe embedded checkout error:', data);
      return res.status(resp.status).json({ error: data.error?.message || 'Checkout failed' });
    }

    return res.status(200).json({ clientSecret: data.client_secret });
  } catch (err) {
    console.error('Stripe embedded checkout error:', err);
    return res.status(500).json({ error: err.message });
  }
}
