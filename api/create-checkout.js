import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: 'First Contact — Consciousness Exploration Kit',
              description: '3 guided audio sessions + field manual + 7-day plan. Instant download.',
              images: ['https://enterliminalspace.com/web-images/v8-deep.jpg'],
            },
            unit_amount: 3700, // $37.00 in cents
          },
          quantity: 1,
        },
      ],
      payment_method_types: ['card'],
      allow_promotion_codes: true,
      success_url: 'https://enterliminalspace.com/members.html?purchased=true',
      cancel_url: 'https://enterliminalspace.com/?checkout=cancelled',
      metadata: {
        product: 'first_contact',
        source: req.body?.source || 'website',
      },
    });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('Stripe checkout error:', err);
    return res.status(500).json({ error: err.message });
  }
}
