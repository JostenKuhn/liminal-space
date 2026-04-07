// Email opt-in — 3-step process:
// 1. profile-import (synchronous — creates profile immediately)
// 2. subscription (grants consent on existing profile)
// 3. event (triggers nurture flow)

const KLAVIYO_LIST_ID = 'RrUgf6'; // "Email List"

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, first_name } = req.body || {};

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  const KLAVIYO_KEY = (process.env.KLAVIYO_PRIVATE_KEY || '').trim();

  if (!KLAVIYO_KEY) {
    console.error('Missing KLAVIYO_PRIVATE_KEY');
    return res.status(500).json({ error: 'Email service not configured' });
  }

  const headers = {
    'Authorization': `Klaviyo-API-Key ${KLAVIYO_KEY}`,
    'Content-Type': 'application/json',
    'revision': '2024-10-15',
  };

  try {
    // Step 1: Create profile (synchronous — profile exists immediately after this)
    const step1 = await fetch('https://a.klaviyo.com/api/profile-import/', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        data: {
          type: 'profile',
          attributes: {
            email,
            first_name: first_name || undefined,
            properties: { source: 'website_optin', optin_page: 'landing_page' },
          },
        },
      }),
    });
    const step1Body = await step1.text();
    console.log(`[${email}] Step 1 profile-import: ${step1.status} ${step1Body.slice(0, 200)}`);

    // Step 2: Subscribe to list with consent (profile already exists — consent sticks)
    const step2 = await fetch('https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs/', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        data: {
          type: 'profile-subscription-bulk-create-job',
          attributes: {
            profiles: {
              data: [{
                type: 'profile',
                attributes: {
                  email,
                  subscriptions: { email: { marketing: { consent: 'SUBSCRIBED' } } },
                },
              }],
            },
          },
          relationships: {
            list: { data: { type: 'list', id: KLAVIYO_LIST_ID } },
          },
        },
      }),
    });
    console.log(`[${email}] Step 2 subscribe: ${step2.status}`);

    // Step 3: Fire opt-in event (triggers nurture flow)
    const step3 = await fetch('https://a.klaviyo.com/api/events/', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        data: {
          type: 'event',
          attributes: {
            metric: { data: { type: 'metric', attributes: { name: 'Email Opt-In' } } },
            profile: { data: { type: 'profile', attributes: { email } } },
            properties: { source: 'landing_page', free_audio_url: 'https://enterliminalspace.com/free-audio.html' },
          },
        },
      }),
    });
    console.log(`[${email}] Step 3 event: ${step3.status}`);
    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
