// Email opt-in — adds subscriber to Klaviyo + Beehiiv (temporary dual-send)
// Beehiiv handles nurture emails until Klaviyo flows are built
// TODO: Remove Beehiiv once Klaviyo flows are live

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, first_name } = req.body || {};

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  const KLAVIYO_KEY = (process.env.KLAVIYO_PRIVATE_KEY || '').trim();
  const BEEHIIV_KEY = (process.env.BEEHIIV_API_KEY || '').trim();
  const BEEHIIV_PUB = (process.env.BEEHIIV_PUBLICATION_ID || '').trim();

  try {
    // Send to Klaviyo (future primary)
    if (KLAVIYO_KEY) {
      await fetch('https://a.klaviyo.com/api/profile-import/', {
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
              properties: { source: 'website_optin', optin_page: 'landing_page' },
            },
          },
        }),
      });

      // Track opt-in event for Klaviyo flows
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
              metric: { data: { type: 'metric', attributes: { name: 'Email Opt-In' } } },
              profile: { data: { type: 'profile', attributes: { email } } },
              properties: { source: 'landing_page', free_audio_url: 'https://enterliminalspace.com/free-audio.html' },
            },
          },
        }),
      });
    }

    // Send to Beehiiv (temporary — handles nurture emails until Klaviyo flows are live)
    if (BEEHIIV_KEY && BEEHIIV_PUB) {
      await fetch(`https://api.beehiiv.com/v2/publications/${BEEHIIV_PUB}/subscriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${BEEHIIV_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          ...(first_name && { custom_fields: [{ name: 'First Name', value: first_name }] }),
          utm_source: 'website',
          utm_medium: 'landing_page',
          referring_site: 'enterliminalspace.com',
          send_welcome_email: true,
        }),
      });
    }

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
