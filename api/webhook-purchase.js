/**
 * POST /api/webhook-purchase
 *
 * Called by Stan Store after a successful purchase.
 * Expects JSON body with at least { email: "buyer@example.com" }
 *
 * What it does:
 * 1. Finds or creates the subscriber in Beehiiv
 * 2. Adds the "purchased" tag
 * 3. Removes them from the welcome/nurture automation
 *
 * Security: validates a shared secret via ?key= query param or x-webhook-secret header
 */

const API_KEY = process.env.BEEHIIV_API_KEY;
const PUB_ID = process.env.BEEHIIV_PUBLICATION_ID;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const AUTOMATION_ID = '76426619-2bc5-49fb-99c8-73c47bc59e16';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Validate webhook secret
  const key = req.query.key || req.headers['x-webhook-secret'];
  if (!WEBHOOK_SECRET || key !== WEBHOOK_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const email = extractEmail(req.body);
  if (!email) {
    return res.status(400).json({ error: 'No email found in payload' });
  }

  if (!API_KEY || !PUB_ID) {
    console.error('Missing BEEHIIV_API_KEY or BEEHIIV_PUBLICATION_ID');
    return res.status(500).json({ error: 'Server configuration error' });
  }

  try {
    // Step 1: Find or create the subscriber
    let subscriber = await findSubscriber(email);

    if (!subscriber) {
      console.log(`No subscriber found for ${email} — creating one`);
      subscriber = await createSubscriber(email, req.body);
      if (!subscriber) {
        return res.status(500).json({ error: 'Failed to create subscriber' });
      }
    }

    // Step 2: Add "purchased" tag
    const tagResult = await addPurchasedTag(subscriber.id);

    // Step 3: Remove from nurture automation
    const automationResult = await removeFromAutomation(subscriber.id);

    return res.status(200).json({
      success: true,
      email,
      subscriber_id: subscriber.id,
      tag_added: tagResult,
      removed_from_automation: automationResult,
    });
  } catch (err) {
    console.error('Webhook error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * Extract email from various Stan Store payload formats
 */
function extractEmail(body) {
  if (!body) return null;
  if (body.email) return body.email;
  if (body.customer?.email) return body.customer.email;
  if (body.data?.email) return body.data.email;
  if (body.data?.customer?.email) return body.data.customer.email;
  return null;
}

/**
 * Find subscriber in Beehiiv by email
 */
async function findSubscriber(email) {
  const response = await fetch(
    `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions?email=${encodeURIComponent(email)}`,
    {
      headers: { 'Authorization': `Bearer ${API_KEY}` },
    }
  );

  if (!response.ok) {
    console.error('Find subscriber error:', await response.text());
    return null;
  }

  const data = await response.json();
  return data.data?.[0] || null;
}

/**
 * Create a new subscriber in Beehiiv (for buyers who never opted in)
 */
async function createSubscriber(email, body) {
  try {
    const firstName = body?.customer?.first_name || body?.data?.customer?.first_name || null;

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
          ...(firstName && { custom_fields: [{ name: 'First Name', value: firstName }] }),
          utm_source: 'stan_store',
          utm_medium: 'purchase',
          referring_site: 'stan.store/liminalspace',
          send_welcome_email: false,
        }),
      }
    );

    if (!response.ok) {
      console.error('Create subscriber error:', await response.text());
      return null;
    }

    const data = await response.json();
    return data.data || null;
  } catch (err) {
    console.error('Create subscriber error:', err);
    return null;
  }
}

/**
 * Add "purchased" tag to subscriber
 */
async function addPurchasedTag(subscriberId) {
  try {
    const tagsResponse = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/tags`,
      {
        headers: { 'Authorization': `Bearer ${API_KEY}` },
      }
    );

    if (!tagsResponse.ok) {
      console.error('Get tags error:', await tagsResponse.text());
      return false;
    }

    const tagsData = await tagsResponse.json();
    const purchasedTag = tagsData.data?.find(t => t.name === 'purchased');

    if (!purchasedTag) {
      console.error('No "purchased" tag found in Beehiiv — create it manually');
      return false;
    }

    const assignResponse = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions/${subscriberId}/tags`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tag_ids: [purchasedTag.id] }),
      }
    );

    if (!assignResponse.ok) {
      console.error('Assign tag error:', await assignResponse.text());
      return false;
    }

    return true;
  } catch (err) {
    console.error('Tag error:', err);
    return false;
  }
}

/**
 * Remove subscriber from the nurture automation
 */
async function removeFromAutomation(subscriberId) {
  try {
    const response = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUB_ID}/automations/${AUTOMATION_ID}/subscriptions/${subscriberId}`,
      {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${API_KEY}` },
      }
    );

    if (!response.ok) {
      if (response.status === 404) return true;
      console.error('Remove from automation error:', await response.text());
      return false;
    }

    return true;
  } catch (err) {
    console.error('Automation removal error:', err);
    return false;
  }
}
