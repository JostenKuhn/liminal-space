// Diagnostic v5 — test custom fields
// DELETE after debugging

export default async function handler(req, res) {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Pass ?email=...' });

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  // Find subscriber
  const findResp = await fetch(
    `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions?email=${encodeURIComponent(email)}`,
    { headers: { 'Authorization': `Bearer ${API_KEY}` } }
  );
  const findData = await findResp.json();
  const subId = findData.data?.[0]?.id;
  if (!subId) return res.status(200).json({ error: 'not found' });

  // Try PATCH with custom_fields
  const patchResp = await fetch(
    `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions/${subId}`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        custom_fields: [{ name: 'purchased', value: 'true' }],
      }),
    }
  );
  const patchBody = await patchResp.text();

  return res.status(200).json({
    subscriber_id: subId,
    patch_status: patchResp.status,
    patch_response: patchBody.substring(0, 800),
  });
}
