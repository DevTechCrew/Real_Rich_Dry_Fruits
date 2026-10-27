export const site = {
  name: 'Real Rich Dry Fruits',
  short: 'Real Rich',
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://real-rich.vercel.app',
  tagline: 'Snacks of the real rich.', // confirm vs "Real Ingredients. Real Rich."
  subline: 'Hand-picked, premium dry fruits from Khandwa.',
  phone: '9302000286',
  whatsapp: '919302000286', // CONFIRM with client that this is the WhatsApp number
  email: 'realrichdryfruit@gmail.com',
  address: '241, Ward No. 38, Gali No. 5, Sindhi Colony, Khandwa, Madhya Pradesh, India',
  fssai: '21426950000998',
  instagram: 'https://www.instagram.com/real_rich_india/',
  instagramHandle: '@real_rich_india',
  mapLink: 'https://share.google/Bp9zqtGAb9ez7d8Ty',
  hours: '', // PENDING from client, e.g. "Mon to Sat, 10 am to 8 pm". Hidden while empty.
  originsConfirmed: true, // confirmed in the Oct 2026 change request; hides the draft note on Quality
};
export const noindex = process.env.NEXT_PUBLIC_NOINDEX === '1';
