type P = { className?: string };
const S = ({ className = 'ic', children }: P & { children: React.ReactNode }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
);
export const WhatsAppIcon = ({ className = 'ic' }: P) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>
);
export const InstagramIcon = ({ className = 'ic' }: P) => (<S className={className}><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.3" cy="6.7" r=".6" fill="currentColor" /></S>);
export const PhoneIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.9.34 1.78.66 2.62a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.46-1.23a2 2 0 0 1 2.11-.45c.84.32 1.72.54 2.62.66A2 2 0 0 1 22 16.92z" /></S>);
export const MailIcon = ({ className = 'ic' }: P) => (<S className={className}><rect x="2.5" y="4.5" width="19" height="15" rx="2" /><path d="m3 7 9 6 9-6" /></S>);
export const PinIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z" /><circle cx="12" cy="10" r="3" /></S>);
export const ArrowRightIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="M5 12h14M13 6l6 6-6 6" /></S>);
export const ArrowUpRightIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="M7 17 17 7M8 7h9v9" /></S>);
export const ChevronLeftIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="m15 18-6-6 6-6" /></S>);
export const ChevronRightIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="m9 18 6-6-6-6" /></S>);
export const SparkIcon = ({ className = 'ic' }: P) => (<S className={className}><path d="M12 3v18M4.2 7.5l15.6 9M19.8 7.5l-15.6 9" /></S>);
