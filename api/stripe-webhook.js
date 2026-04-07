// Stripe webhook — handles successful payments
// Sends purchase event + profile to Klaviyo
// Stripe Dashboard → Developers → Webhooks → checkout.session.completed

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

  if (payload.type !== 'checkout.session.completed') {
    return res.status(200).json({ received: true });
  }

  const session = payload.data?.object;
  const email = session?.customer_details?.email || session?.customer_email;

  if (!email) {
    console.error('No email in checkout session');
    return res.status(200).json({ received: true, warning: 'no email' });
  }

  const fullName = session?.customer_details?.name || '';
  const firstName = fullName.split(' ')[0] || '';
  const lastName = fullName.split(' ').slice(1).join(' ') || '';
  const amount = (session.amount_total || 3700) / 100;

  console.log(`Purchase completed: ${email} (${fullName}), $${amount}`);

  const KLAVIYO_KEY = (process.env.KLAVIYO_PRIVATE_KEY || '').trim();
  if (!KLAVIYO_KEY) {
    console.error('Missing KLAVIYO_PRIVATE_KEY');
    return res.status(200).json({ received: true, warning: 'klaviyo not configured' });
  }

  try {
    // Step 1: Create/update profile in Klaviyo
    const profileResult = await upsertProfile(KLAVIYO_KEY, email, firstName, lastName);

    // Step 2: Track purchase event in Klaviyo (triggers automations)
    const eventResult = await trackPurchaseEvent(KLAVIYO_KEY, email, amount, session.id);

    console.log(`Klaviyo: profile=${profileResult}, event=${eventResult}`);

    return res.status(200).json({
      received: true,
      email,
      klaviyo_profile: profileResult,
      klaviyo_event: eventResult,
    });
  } catch (err) {
    console.error('Webhook error:', err);
    return res.status(200).json({ received: true, warning: err.message });
  }
}

async function upsertProfile(apiKey, email, firstName, lastName) {
  try {
    const resp = await fetch('https://a.klaviyo.com/api/profile-import/', {
      method: 'POST',
      headers: {
        'Authorization': `Klaviyo-API-Key ${apiKey}`,
        'Content-Type': 'application/json',
        'revision': '2024-10-15',
      },
      body: JSON.stringify({
        data: {
          type: 'profile',
          attributes: {
            email,
            first_name: firstName || undefined,
            last_name: lastName || undefined,
            properties: {
              purchased: true,
              product: 'First Contact',
              source: 'stripe_checkout',
            },
          },
        },
      }),
    });

    if (!resp.ok) {
      console.error('Klaviyo profile error:', await resp.text());
      return false;
    }
    return true;
  } catch (err) {
    console.error('Klaviyo profile error:', err);
    return false;
  }
}

async function trackPurchaseEvent(apiKey, email, amount, sessionId) {
  try {
    const resp = await fetch('https://a.klaviyo.com/api/events/', {
      method: 'POST',
      headers: {
        'Authorization': `Klaviyo-API-Key ${apiKey}`,
        'Content-Type': 'application/json',
        'revision': '2024-10-15',
      },
      body: JSON.stringify({
        data: {
          type: 'event',
          attributes: {
            metric: {
              data: {
                type: 'metric',
                attributes: { name: 'Placed Order' },
              },
            },
            profile: {
              data: {
                type: 'profile',
                attributes: { email },
              },
            },
            properties: {
              product_name: 'First Contact — Consciousness Exploration Kit',
              value: amount,
              currency: 'USD',
              stripe_session_id: sessionId,
              members_url: 'https://enterliminalspace.com/members.html',
            },
            value: amount,
            unique_id: sessionId || 'stripe_' + Date.now(),
          },
        },
      }),
    });

    if (!resp.ok) {
      console.error('Klaviyo event error:', await resp.text());
      return false;
    }
    return true;
  } catch (err) {
    console.error('Klaviyo event error:', err);
    return false;
  }
}
