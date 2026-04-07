// Use Stripe REST API directly — no SDK dependency issues on Vercel

export default async function handler(req, res) {
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
    params.append('line_items[0][price_data][currency]', 'usd');
    params.append('line_items[0][price_data][product_data][name]', 'First Contact — Consciousness Exploration Kit');
    params.append('line_items[0][price_data][product_data][description]', '3 guided audio sessions + field manual + 7-day plan. Instant download.');
    params.append('line_items[0][price_data][unit_amount]', '3700');
    params.append('line_items[0][quantity]', '1');
    params.append('payment_method_types[0]', 'card');
    params.append('allow_promotion_codes', 'true');
    params.append('success_url', 'https://enterliminalspace.com/members.html?purchased=true');
    params.append('cancel_url', 'https://enterliminalspace.com/?checkout=cancelled');
    params.append('metadata[product]', 'first_contact');
    params.append('metadata[source]', req.body?.source || 'website');

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
      console.error('Stripe error:', data);
      return res.status(resp.status).json({ error: data.error?.message || 'Checkout failed' });
    }

    return res.status(200).json({ url: data.url });
  } catch (err) {
    console.error('Stripe checkout error:', err);
    return res.status(500).json({ error: err.message });
  }
}
