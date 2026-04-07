export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, first_name } = req.body || {};

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  if (!API_KEY || !PUB_ID) {
    console.error('Missing BEEHIIV_API_KEY or BEEHIIV_PUBLICATION_ID');
    return res.status(500).json({ error: 'Server configuration error' });
  }

  try {
    const response = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          ...(first_name && { custom_fields: [{ name: 'First Name', value: first_name }] }),
          utm_source: 'website',
          utm_medium: 'landing_page',
          referring_site: 'enterliminalspace.com',
          send_welcome_email: true,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error('Beehiiv error:', data);
      return res.status(response.status).json({ error: data.message || 'Subscription failed' });
    }

    return res.status(200).json({ success: true, id: data.data?.id });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
