import { Product } from '@/data/products';
import { productMessage, waLink } from '@/lib/whatsapp';
import Img from './Img';
import Tilt from './Tilt';
import WaButton from './WaButton';
export default function ProductCard({ p, index = 0 }: { p: Product; index?: number }) {
  return (
    <article className="card">
      <Tilt>
        <Img src={p.image} alt={p.name} ratio="3/2" />
        {/* The real pack, as designed. Never edit it with AI. */}
        <img className="pack" src={p.pack} alt={`Real Rich ${p.name} ${p.size} pack`} width="480" height="690" loading="lazy" decoding="async" />
        <span className="image-index" aria-hidden="true">0{index + 1}</span>
      </Tilt>
      <div className="meta"><h3>{p.name} {p.hindi && <span className="hi">/ {p.hindi}</span>}</h3><span className="muted">{p.size}</span></div>
      <p className="muted">{p.blurb}</p>
      <WaButton href={waLink(productMessage(p.wa))} where={`card_${p.slug}`}>Message for price</WaButton>
    </article>
  );
}
