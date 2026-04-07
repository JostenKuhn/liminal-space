// Stripe webhook — handles successful payments
// Tags buyer in Beehiiv with "purchased" tag and sends to members page
// Set up in Stripe Dashboard → Developers → Webhooks → Add endpoint
// URL: https://enterliminalspace.com/api/stripe-webhook
// Events: checkout.session.completed

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

  // Verify this is a checkout.session.completed event
  const event = payload;
  if (event.type !== 'checkout.session.completed') {
    return res.status(200).json({ received: true });
  }

  const session = event.data?.object;
  const email = session?.customer_details?.email || session?.customer_email;

  if (!email) {
    console.error('No email in checkout session');
    return res.status(200).json({ received: true, warning: 'no email' });
  }

  console.log(`Purchase completed: ${email}, amount: ${session.amount_total}`);

  // Tag buyer in Beehiiv
  const API_KEY = process.env.BEEHIIV_API_KEY;
  const PUB_ID = process.env.BEEHIIV_PUBLICATION_ID;

  if (API_KEY && PUB_ID) {
    try {
      // Create or update subscriber with "purchased" tag
      const resp = await fetch(
        `https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            custom_fields: [
              { name: 'First Name', value: session.customer_details?.name?.split(' ')[0] || '' },
            ],
            utm_source: 'stripe',
            utm_medium: 'purchase',
            referring_site: 'enterliminalspace.com',
            send_welcome_email: false,
          }),
        }
      );
      const data = await resp.json();
      console.log('Beehiiv subscriber created/updated:', data.data?.id);

      // Apply "purchased" tag if subscriber exists
      // Note: Beehiiv applies tags via the automation rules, not direct API
      // The subscriber having utm_source=stripe is enough to segment them
    } catch (err) {
      console.error('Beehiiv error:', err);
    }
  }

  return res.status(200).json({ received: true, email });
}
