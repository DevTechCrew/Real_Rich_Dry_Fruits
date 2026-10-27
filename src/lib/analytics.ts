export const track = (name: string, params: Record<string, unknown> = {}) => {
  if (typeof window === 'undefined') return;
  const g = (window as unknown as { gtag?: (...a: unknown[]) => void }).gtag;
  if (g) g('event', name, params);
};
