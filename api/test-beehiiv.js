// Diagnostic v4 — test PATCH utm_source on existing subscriber
// GET /api/test-beehiiv?email=josten.kuhn@gmail.com
// DELETE after debugging

export default async function handler(req, res) {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Pass ?email=...' });

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  // Step 1: Find subscriber
  const findResp = await fetch(
    `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions?email=${encodeURIComponent(email)}`,
    { headers: { 'Authorization': `Bearer ${API_KEY}` } }
  );
  const findData = await findResp.json();
  const subId = findData.data?.[0]?.id;

  if (!subId) return res.status(200).json({ error: 'subscriber not found' });

  // Step 2: PATCH utm_source to 'stripe'
  const patchResp = await fetch(
    `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions/${subId}`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ utm_source: 'stripe', utm_medium: 'purchase' }),
    }
  );
  const patchBody = await patchResp.text();

  return res.status(200).json({
    subscriber_id: subId,
    patch_status: patchResp.status,
    patch_response: patchBody.substring(0, 500),
  });
}
