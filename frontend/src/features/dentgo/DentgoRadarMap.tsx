import React, { useMemo } from "react";
import type { DentgoExpressOrder, HubItem } from "./DentgoExpressCockpit";

export interface RadarClinic {
  label: string;
  lat: number;
  lng: number;
}

export interface DentgoRadarMapProps {
  hubs: HubItem[];
  orders: DentgoExpressOrder[];
  clinic?: RadarClinic;
}

const KM_PER_DEG_LAT = 111.32;
const W = 640;
const H = 360;

function haversineKm(aLat: number, aLng: number, bLat: number, bLng: number): number {
  const rad = (d: number) => (d * Math.PI) / 180;
  const dLat = rad(bLat - aLat);
  const dLng = rad(bLng - aLng);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(aLat)) * Math.cos(rad(bLat)) * Math.sin(dLng / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.min(1, Math.sqrt(h)));
}

function hashAngle(id: string): number {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
  return (h % 360) * (Math.PI / 180);
}

/** Radar SVG georreferenciado: micro-hubs, clínicas, anéis Haversine e entregadores em trânsito. */
export const DentgoRadarMap: React.FC<DentgoRadarMapProps> = ({ hubs, orders, clinic }) => {
  const model = useMemo(() => {
    const points: Array<{ lat: number; lng: number }> = hubs.map((h) => ({ lat: h.latitude, lng: h.longitude }));
    if (clinic) points.push({ lat: clinic.lat, lng: clinic.lng });
    if (points.length === 0) return null;

    const centerLat = points.reduce((s, p) => s + p.lat, 0) / points.length;
    const centerLng = points.reduce((s, p) => s + p.lng, 0) / points.length;
    const kmPerDegLng = KM_PER_DEG_LAT * Math.cos((centerLat * Math.PI) / 180);

    const toKm = (lat: number, lng: number) => ({
      x: (lng - centerLng) * kmPerDegLng,
      y: (lat - centerLat) * KM_PER_DEG_LAT,
    });

    const maxRadius = Math.max(10, ...hubs.map((h) => h.coverage_radius_km));
    const extent = Math.max(
      maxRadius,
      ...points.map((p) => {
        const k = toKm(p.lat, p.lng);
        return Math.max(Math.abs(k.x), Math.abs(k.y)) + maxRadius * 0.6;
      }),
    );
    const pxPerKm = Math.min(W, H) / 2 / extent;
    const project = (lat: number, lng: number) => {
      const k = toKm(lat, lng);
      return { x: W / 2 + k.x * pxPerKm, y: H / 2 - k.y * pxPerKm };
    };

    const hubPoints = hubs.map((h) => ({ hub: h, ...project(h.latitude, h.longitude), r: h.coverage_radius_km * pxPerKm }));
    const clinicPoint = clinic ? { ...clinic, ...project(clinic.lat, clinic.lng) } : null;

    const orderPoints = orders
      .map((o) => {
        const hp = hubPoints.find((p) => p.hub.id === o.hub_id) || hubPoints[0];
        if (!hp) return null;
        if (Number.isFinite(o.delivery_lat) && Number.isFinite(o.delivery_lng)) {
          const dest = project(o.delivery_lat as number, o.delivery_lng as number);
          return { order: o, hubX: hp.x, hubY: hp.y, x: dest.x, y: dest.y };
        }
        // Sem coordenadas no pedido: posiciona pela distância real com ângulo determinístico
        const ang = hashAngle(o.id);
        const dist = Math.max(0.5, o.distance_km) * pxPerKm;
        return { order: o, hubX: hp.x, hubY: hp.y, x: hp.x + Math.cos(ang) * dist, y: hp.y + Math.sin(ang) * dist };
      })
      .filter((p): p is NonNullable<typeof p> => p !== null);

    const nearest =
      clinic && hubs.length > 0
        ? hubs
            .map((h) => ({ h, d: haversineKm(clinic.lat, clinic.lng, h.latitude, h.longitude) }))
            .sort((a, b) => a.d - b.d)[0]
        : null;

    return { hubPoints, clinicPoint, orderPoints, nearest };
  }, [hubs, orders, clinic]);

  if (!model) {
    return (
      <div className="p-6 text-center text-xs text-text-secondary border border-border rounded-xl bg-surface-card">
        Cadastre um Hub Urbano para exibir o radar geolocalizado.
      </div>
    );
  }

  const inTransit = model.orderPoints.filter((p) => p.order.status === "IN_TRANSIT_LIVE");

  return (
    <div className="bg-surface-card border border-border rounded-xl p-4 space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-bold text-text-main">Radar de Geolocalização DENTGO (Haversine)</span>
        <span className="text-[10px] text-text-secondary">
          {model.hubPoints.length} hubs - {inTransit.length} entregadores em trânsito
          {model.nearest ? ` - hub mais próximo da clínica: ${model.nearest.h.name} (${model.nearest.d.toFixed(1)} km)` : ""}
        </span>
      </div>

      <svg
        role="img"
        aria-label="Mapa radar de micro-hubs, clínicas cirúrgicas e entregadores"
        viewBox={`0 0 ${W} ${H}`}
        className="w-full h-auto rounded-lg bg-surface-bg border border-border"
      >
        <defs>
          <pattern id="radar-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M40 0H0V40" fill="none" stroke="var(--color-border-subtle)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width={W} height={H} fill="url(#radar-grid)" />

        {model.hubPoints.map(({ hub, x, y, r }) => (
          <g key={hub.id}>
            {[1, 0.66, 0.33].map((f) => (
              <circle
                key={f}
                cx={x}
                cy={y}
                r={r * f}
                fill={f === 1 ? "var(--color-brand-primary-subtle)" : "none"}
                fillOpacity={0.5}
                stroke="var(--color-brand-primary)"
                strokeOpacity={f === 1 ? 0.7 : 0.35}
                strokeDasharray={f === 1 ? "0" : "4 4"}
              />
            ))}
            <rect x={x - 6} y={y - 6} width={12} height={12} fill="var(--color-brand-navy)" />
            <text x={x + 10} y={y - 8} fontSize="10" fill="var(--color-text-main)" fontWeight="600">
              {hub.name}
            </text>
            <text x={x + 10} y={y + 4} fontSize="9" fill="var(--color-text-secondary)">
              raio {hub.coverage_radius_km} km
            </text>
          </g>
        ))}

        {model.orderPoints.map(({ order, hubX, hubY, x, y }) => {
          const live = order.status === "IN_TRANSIT_LIVE";
          const done = order.status === "DELIVERED_VERIFIED";
          return (
            <g key={order.id}>
              <line
                x1={hubX}
                y1={hubY}
                x2={x}
                y2={y}
                stroke={live ? "var(--color-warning)" : "var(--color-border)"}
                strokeWidth={live ? 1.5 : 1}
                strokeDasharray={live ? "6 3" : "2 3"}
              />
              <circle
                cx={x}
                cy={y}
                r={5}
                fill={done ? "var(--color-success)" : "var(--color-surface-card)"}
                stroke="var(--color-brand-navy)"
                strokeWidth="1.5"
              />
              <text x={x + 8} y={y + 3} fontSize="9" fill="var(--color-text-secondary)">
                {order.customer_cro_uf}
              </text>
              {live && (
                <circle r={5} fill="var(--color-warning)" stroke="var(--color-text-main)" strokeWidth="1">
                  <animateMotion dur="4s" repeatCount="indefinite" path={`M${hubX},${hubY} L${x},${y}`} />
                </circle>
              )}
            </g>
          );
        })}

        {model.clinicPoint && (
          <g>
            <circle cx={model.clinicPoint.x} cy={model.clinicPoint.y} r={9} fill="none" stroke="var(--color-danger)" strokeWidth="2">
              <animate attributeName="r" values="6;14;6" dur="2.4s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="1;0.2;1" dur="2.4s" repeatCount="indefinite" />
            </circle>
            <circle cx={model.clinicPoint.x} cy={model.clinicPoint.y} r={4} fill="var(--color-danger)" />
            <text x={model.clinicPoint.x + 10} y={model.clinicPoint.y + 4} fontSize="10" fill="var(--color-danger)" fontWeight="600">
              {model.clinicPoint.label}
            </text>
          </g>
        )}
      </svg>

      <div className="flex flex-wrap gap-3 text-[10px] text-text-secondary">
        <span className="flex items-center gap-1">
          <svg width="10" height="10"><rect width="10" height="10" fill="var(--color-brand-navy)" /></svg> Micro-Hub
        </span>
        <span className="flex items-center gap-1">
          <svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="var(--color-danger)" /></svg> Clínica cirúrgica (busca de emergência)
        </span>
        <span className="flex items-center gap-1">
          <svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="var(--color-warning)" /></svg> Entregador em trânsito (IN_TRANSIT_LIVE)
        </span>
        <span className="flex items-center gap-1">
          <svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="var(--color-surface-card)" stroke="var(--color-brand-navy)" /></svg> Destino do pedido (posição aproximada pela distância)
        </span>
      </div>
    </div>
  );
};

export default DentgoRadarMap;
