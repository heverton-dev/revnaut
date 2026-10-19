import * as React from "react";
import qrcode from "qrcode-generator";

export interface QrCodeSvgProps {
  value: string;
  size?: number;
  className?: string;
}

/** QR Code real (Reed-Solomon) renderizado como SVG vetorial nítido, usando apenas tokens. */
export function QrCodeSvg({ value, size = 160, className }: QrCodeSvgProps) {
  const path = React.useMemo(() => {
    const qr = qrcode(0, "M");
    qr.addData(value || " ");
    qr.make();
    const n = qr.getModuleCount();
    let d = "";
    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        if (qr.isDark(r, c)) d += `M${c + 2},${r + 2}h1v1h-1z`;
      }
    }
    return { d, n };
  }, [value]);

  const dim = path.n + 4;
  return (
    <svg
      role="img"
      aria-label={`QR Code para ${value}`}
      viewBox={`0 0 ${dim} ${dim}`}
      width={size}
      height={size}
      shapeRendering="crispEdges"
      className={className}
    >
      <rect width={dim} height={dim} fill="var(--color-surface-card)" />
      <path d={path.d} fill="var(--color-text-main)" />
    </svg>
  );
}

export default QrCodeSvg;
