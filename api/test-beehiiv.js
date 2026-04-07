// Diagnostic v3 — test creating subscriber WITH automation_ids
// GET /api/test-beehiiv?email=test@example.com
// DELETE after debugging

export default async function handler(req, res) {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Pass ?email=...' });

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();
  const PURCHASE_AUTO = 'aut_e2df2f26-4ff3-4cce-9c7a-4ef7fbf7f74c';

  const results = {};

  // Test: Create/update subscriber with automation_ids in the body
  try {
    const r = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          utm_source: 'stripe',
          utm_medium: 'purchase',
          referring_site: 'enterliminalspace.com',
          send_welcome_email: false,
          automation_ids: [PURCHASE_AUTO],
        }),
      }
    );
    const raw = await r.text();
    results.create_with_automation = { status: r.status, body: raw.substring(0, 800) };
  } catch (err) {
    results.create_with_automation = { error: err.message };
  }

  return res.status(200).json(results);
}
