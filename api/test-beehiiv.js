// Diagnostic endpoint — test Beehiiv integration
// GET /api/test-beehiiv?email=josten.kuhn@gmail.com
// DELETE THIS FILE after debugging

export default async function handler(req, res) {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Pass ?email=...' });

  const API_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const PUB_ID = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  const results = {
    env: {
      has_api_key: !!API_KEY,
      api_key_prefix: API_KEY ? API_KEY.substring(0, 8) + '...' : 'MISSING',
      has_pub_id: !!PUB_ID,
      pub_id: PUB_ID || 'MISSING',
    },
    steps: {},
  };

  if (!API_KEY || !PUB_ID) {
    return res.status(200).json(results);
  }

  // Step 1: Find subscriber
  try {
    const findResp = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions?email=${encodeURIComponent(email)}`,
      { headers: { 'Authorization': `Bearer ${API_KEY}` } }
    );
    const findData = await findResp.json();
    results.steps.find_subscriber = {
      status: findResp.status,
      found: findData.data?.length > 0,
      subscriber_id: findData.data?.[0]?.id || null,
      subscriber_status: findData.data?.[0]?.status || null,
    };
  } catch (err) {
    results.steps.find_subscriber = { error: err.message };
  }

  // Step 2: List all tags
  try {
    const tagsResp = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/tags`,
      { headers: { 'Authorization': `Bearer ${API_KEY}` } }
    );
    const tagsData = await tagsResp.json();
    results.steps.list_tags = {
      status: tagsResp.status,
      tags: tagsData.data?.map(t => ({ id: t.id, name: t.name })) || [],
      purchased_tag_exists: tagsData.data?.some(t => t.name === 'purchased') || false,
    };
  } catch (err) {
    results.steps.list_tags = { error: err.message };
  }

  // Step 3: Try to apply tag if subscriber + tag both exist
  const subId = results.steps.find_subscriber?.subscriber_id;
  const purchasedTag = results.steps.list_tags?.tags?.find(t => t.name === 'purchased');

  if (subId && purchasedTag) {
    try {
      const tagResp = await fetch(
        `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions/${subId}/tags`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ tag_ids: [purchasedTag.id] }),
        }
      );
      const tagBody = await tagResp.text();
      results.steps.apply_tag = {
        status: tagResp.status,
        response: tagBody,
      };
    } catch (err) {
      results.steps.apply_tag = { error: err.message };
    }
  }

  // Step 4: Try to add to purchase automation
  if (subId) {
    const PURCHASE_AUTO = 'aut_e2df2f26-4ff3-4cce-9c7a-4ef7fbf7f74c';
    try {
      const autoResp = await fetch(
        `https://api.beehiiv.com/v2/publications/${PUB_ID}/automations/${PURCHASE_AUTO}/subscriptions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ subscriber_id: subId }),
        }
      );
      const autoBody = await autoResp.text();
      results.steps.add_to_automation = {
        status: autoResp.status,
        response: autoBody,
      };
    } catch (err) {
      results.steps.add_to_automation = { error: err.message };
    }
  }

  return res.status(200).json(results);
}
