// Email opt-in — subscribes to Klaviyo with email consent + triggers nurture flow
// Klaviyo handles all emails via flows

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
    // Subscribe profile to Email List with marketing consent
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
              data: [
                {
                  type: 'profile',
                  attributes: {
                    email,
                    first_name: first_name || undefined,
                    properties: { source: 'website_optin', optin_page: 'landing_page' },
                  },
                },
              ],
            },
            historical_import: false,
          },
          relationships: {
            list: {
              data: {
                type: 'list',
                id: KLAVIYO_LIST_ID,
              },
            },
          },
        },
      }),
    });

    // Track opt-in event (triggers Klaviyo nurture flow)
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
            profile: { data: { type: 'profile', attributes: { email } } },
            properties: { source: 'landing_page', free_audio_url: 'https://enterliminalspace.com/free-audio.html' },
          },
        },
      }),
    });

    console.log(`Klaviyo: subscribe=${subResp.status}, event=${eventResp.status}, email=${email}`);
    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
