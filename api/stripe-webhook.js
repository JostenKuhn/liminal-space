// Stripe webhook — handles successful payments from embedded checkout
// Set up in Stripe Dashboard → Developers → Webhooks → Add endpoint
// URL: https://enterliminalspace.com/api/stripe-webhook
// Events: checkout.session.completed

const AUTOMATION_ID = '76426619-2bc5-49fb-99c8-73c47bc59e16';

export const config = {
  api: { bodyParser: false },
};

async function buffer(readable) {
  const chunks = [];
  for await (const chunk of readable) {
    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk);
  }
  return Buffer.concat(chunks);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const buf = await buffer(req);
  const payload = JSON.parse(buf.toString());

  // Only handle checkout.session.completed
  if (payload.type !== 'checkout.session.completed') {
    return res.status(200).json({ received: true });
  }

  const session = payload.data?.object;
  const email = session?.customer_details?.email || session?.customer_email;

  if (!email) {
    console.error('No email in checkout session');
    return res.status(200).json({ received: true, warning: 'no email' });
  }

  const firstName = session?.customer_details?.name?.split(' ')[0] || '';
  console.log(`Purchase completed: ${email} (${firstName}), amount: ${session.amount_total}`);

  const API_KEY = process.env.BEEHIIV_API_KEY;
  const PUB_ID = process.env.BEEHIIV_PUBLICATION_ID;

  if (!API_KEY || !PUB_ID) {
    console.error('Missing BEEHIIV_API_KEY or BEEHIIV_PUBLICATION_ID');
    return res.status(200).json({ received: true, warning: 'beehiiv not configured' });
  }

  try {
    // Step 1: Find existing subscriber
    let subscriber = await findSubscriber(API_KEY, PUB_ID, email);

    if (!subscriber) {
      // Create new subscriber (buyer who skipped email opt-in)
      console.log(`No subscriber found for ${email} — creating one`);
      subscriber = await createSubscriber(API_KEY, PUB_ID, email, firstName);
    }

    if (!subscriber) {
      console.error('Failed to find or create subscriber');
      return res.status(200).json({ received: true, warning: 'subscriber creation failed' });
    }

    // Step 2: Apply "purchased" tag
    const tagResult = await addPurchasedTag(API_KEY, PUB_ID, subscriber.id);

    // Step 3: Remove from nurture automation (they bought — stop selling)
    const automationResult = await removeFromAutomation(API_KEY, PUB_ID, subscriber.id);

    console.log(`Webhook complete: email=${email}, tagged=${tagResult}, removed_from_automation=${automationResult}`);

    return res.status(200).json({
      received: true,
      email,
      subscriber_id: subscriber.id,
      tag_added: tagResult,
      removed_from_automation: automationResult,
    });
  } catch (err) {
    console.error('Webhook error:', err);
    return res.status(200).json({ received: true, warning: err.message });
  }
}

async function findSubscriber(apiKey, pubId, email) {
  const response = await fetch(
    `https://api.beehiiv.com/v2/publications/${pubId}/subscriptions?email=${encodeURIComponent(email)}`,
    { headers: { 'Authorization': `Bearer ${apiKey}` } }
  );

  if (!response.ok) {
    console.error('Find subscriber error:', await response.text());
    return null;
  }

  const data = await response.json();
  return data.data?.[0] || null;
}

async function createSubscriber(apiKey, pubId, email, firstName) {
  const response = await fetch(
    `https://api.beehiiv.com/v2/publications/${pubId}/subscriptions`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        ...(firstName && { custom_fields: [{ name: 'First Name', value: firstName }] }),
        utm_source: 'stripe',
        utm_medium: 'purchase',
        referring_site: 'enterliminalspace.com',
        send_welcome_email: true,
      }),
    }
  );

  if (!response.ok) {
    console.error('Create subscriber error:', await response.text());
    return null;
  }

  const data = await response.json();
  return data.data || null;
}

async function addPurchasedTag(apiKey, pubId, subscriberId) {
  try {
    // Get all tags to find "purchased"
    const tagsResponse = await fetch(
      `https://api.beehiiv.com/v2/publications/${pubId}/tags`,
      { headers: { 'Authorization': `Bearer ${apiKey}` } }
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
      `https://api.beehiiv.com/v2/publications/${pubId}/subscriptions/${subscriberId}/tags`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
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

async function removeFromAutomation(apiKey, pubId, subscriberId) {
  try {
    const response = await fetch(
      `https://api.beehiiv.com/v2/publications/${pubId}/automations/${AUTOMATION_ID}/subscriptions/${subscriberId}`,
      {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${apiKey}` },
      }
    );

    if (!response.ok) {
      if (response.status === 404) return true; // Not in automation — fine
      console.error('Remove from automation error:', await response.text());
      return false;
    }

    return true;
  } catch (err) {
    console.error('Automation removal error:', err);
    return false;
  }
}
