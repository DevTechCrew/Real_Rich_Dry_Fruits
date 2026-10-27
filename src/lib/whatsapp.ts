import { site } from '@/data/site';
export const waLink = (text: string) => `https://wa.me/${site.whatsapp}?text=${encodeURIComponent(text)}`;
export const productMessage = (name: string) => `Hi Real Rich, I'd like the price for ${name} (250 g).`;
export const generalMessage = "Hi Real Rich, I'd like to know the price.";
export const bulkMessage = 'Hi Real Rich, I have a bulk order enquiry.';
