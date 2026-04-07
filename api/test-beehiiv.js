// Diagnostic endpoint — test Beehiiv integration
// GET /api/test-beehiiv?email=josten.kuhn@gmail.com
// DELETE THIS FILE after debugging

export default async function handler(req, res) {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Pass ?email=...' });

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  const results = { env: { api_key_len: API_KEY.length, pub_id: PUB_ID }, steps: {} };

  if (!API_KEY || !PUB_ID) return res.status(200).json(results);

  // Step 1: Find subscriber
  try {
    const r = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions?email=${encodeURIComponent(email)}`,
      { headers: { 'Authorization': `Bearer ${API_KEY}` } }
    );
    const raw = await r.text();
    results.steps.find_subscriber = { status: r.status, body: raw.substring(0, 500) };
  } catch (err) {
    results.steps.find_subscriber = { error: err.message };
  }

  // Step 2: List tags — show raw response
  try {
    const url = `https://api.beehiiv.com/v2/publications/${PUB_ID}/tags`;
    const r = await fetch(url, { headers: { 'Authorization': `Bearer ${API_KEY}` } });
    const raw = await r.text();
    results.steps.list_tags = { url, status: r.status, body: raw.substring(0, 500) };
  } catch (err) {
    results.steps.list_tags = { error: err.message };
  }

  // Step 3: Try automation with full ID
  try {
    const url1 = `https://api.beehiiv.com/v2/publications/${PUB_ID}/automations/aut_e2df2f26-4ff3-4cce-9c7a-4ef7fbf7f74c/subscriptions`;
    const r1 = await fetch(url1, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ subscriber_id: 'sub_4fe1a3d3-3fa2-4c99-842c-7fb3d927f067' }),
    });
    const raw1 = await r1.text();
    results.steps.automation_full_id = { url: url1, status: r1.status, body: raw1.substring(0, 500) };
  } catch (err) {
    results.steps.automation_full_id = { error: err.message };
  }

  // Step 4: Try automation with just UUID (no aut_ prefix)
  try {
    const url2 = `https://api.beehiiv.com/v2/publications/${PUB_ID}/automations/e2df2f26-4ff3-4cce-9c7a-4ef7fbf7f74c/subscriptions`;
    const r2 = await fetch(url2, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ subscriber_id: 'sub_4fe1a3d3-3fa2-4c99-842c-7fb3d927f067' }),
    });
    const raw2 = await r2.text();
    results.steps.automation_no_prefix = { url: url2, status: r2.status, body: raw2.substring(0, 500) };
  } catch (err) {
    results.steps.automation_no_prefix = { error: err.message };
  }

  // Step 5: List automations to see what's available
  try {
    const url3 = `https://api.beehiiv.com/v2/publications/${PUB_ID}/automations`;
    const r3 = await fetch(url3, { headers: { 'Authorization': `Bearer ${API_KEY}` } });
    const raw3 = await r3.text();
    results.steps.list_automations = { status: r3.status, body: raw3.substring(0, 1000) };
  } catch (err) {
    results.steps.list_automations = { error: err.message };
  }

  return res.status(200).json(results);
}
