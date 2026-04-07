// Email opt-in — creates profile + triggers nurture flow, then subscribes with consent
// Order matters: event first (creates profile), subscription after (grants consent)

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

  try {
    // Step 1: Track opt-in event FIRST (creates profile + triggers nurture flow)
    const eventResp = await fetch('https://a.klaviyo.com/api/events/', {
      method: 'POST',
      headers: {
        'Authorization': `Klaviyo-API-Key ${KLAVIYO_KEY}`,
        'Content-Type': 'application/json',
        'revision': '2024-10-15',
      },
      body: JSON.stringify({
        data: {
          type: 'event',
          attributes: {
            metric: { data: { type: 'metric', attributes: { name: 'Email Opt-In' } } },
            profile: {
              data: {
                type: 'profile',
                attributes: {
                  email,
                  first_name: first_name || undefined,
                  properties: { source: 'website_optin', optin_page: 'landing_page' },
                },
              },
            },
            properties: { source: 'landing_page', free_audio_url: 'https://enterliminalspace.com/free-audio.html' },
          },
        },
      }),
    });

    // Step 2: Subscribe with consent AFTER (updates the profile created by event)
    const subResp = await fetch('https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs/', {
      method: 'POST',
      headers: {
        'Authorization': `Klaviyo-API-Key ${KLAVIYO_KEY}`,
        'Content-Type': 'application/json',
        'revision': '2024-10-15',
      },
      body: JSON.stringify({
        data: {
          type: 'profile-subscription-bulk-create-job',
          attributes: {
            profiles: {
              data: [{
                type: 'profile',
                attributes: {
                  email,
                  first_name: first_name || undefined,
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

    console.log(`Klaviyo: event=${eventResp.status}, subscribe=${subResp.status}, email=${email}`);
    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
