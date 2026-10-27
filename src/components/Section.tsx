export default function Section({ tone = '', children, id, center = false, decor }: { tone?: '' | 'alt' | 'dark'; children: React.ReactNode; id?: string; center?: boolean; decor?: React.ReactNode }) {
  return <section id={id} className={`section ${tone}`}>{decor}<div className={`wrap rv ${center ? 'center' : ''}`}>{children}</div></section>;
}
