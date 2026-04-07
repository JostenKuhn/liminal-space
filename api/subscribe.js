// Email opt-in — adds subscriber to Klaviyo list
// Called from landing page + free-audio page forms

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
    return res.status(500).json({ error: 'Server configuration error' });
  }

  try {
    // Create/update profile in Klaviyo
    const profileResp = await fetch('https://a.klaviyo.com/api/profile-import/', {
      method: 'POST',
      headers: {
        'Authorization': `Klaviyo-API-Key ${KLAVIYO_KEY}`,
        'Content-Type': 'application/json',
        'revision': '2024-10-15',
      },
      body: JSON.stringify({
        data: {
          type: 'profile',
          attributes: {
            email,
            first_name: first_name || undefined,
            properties: {
              source: 'website_optin',
              optin_page: 'landing_page',
            },
          },
        },
      }),
    });

    if (!profileResp.ok) {
      const err = await profileResp.text();
      console.error('Klaviyo profile error:', err);
      return res.status(profileResp.status).json({ error: 'Subscription failed' });
    }

    // Track opt-in event (triggers welcome/nurture flow)
    await fetch('https://a.klaviyo.com/api/events/', {
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
            metric: {
              data: {
                type: 'metric',
                attributes: { name: 'Email Opt-In' },
              },
            },
            profile: {
              data: {
                type: 'profile',
                attributes: { email },
              },
            },
            properties: {
              source: 'landing_page',
              free_audio_url: 'https://enterliminalspace.com/free-audio.html',
            },
          },
        },
      }),
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
