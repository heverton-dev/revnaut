// -*- coding: utf-8 -*-
/**
 * ExecutiveCockpitView.tsx
 * Wrapper do Cockpit Executivo (rota `dashboard`) que orquestra o modo
 * `executive_cockpit` de SupersetEmbeddedDashboard e injeta a navegação
 * de estágio do funil para o workspace de Deals (TICKET-DASH-06).
 */

import React from "react";
import {
  SupersetEmbeddedDashboard,
  type SupersetEmbeddedProps,
} from "@/features/bi/SupersetEmbeddedDashboard";

export interface ExecutiveCockpitViewProps {
  title?: string;
  onNavigate?: (route: string, opts?: { stage?: string }) => void;
  userId?: string;
  accountId?: string;
}

const resolveStageHash = (stage?: string): string => {
  if (!stage) return "#!/deals";
  return `#!/deals?stage=${encodeURIComponent(stage)}`;
};

export const ExecutiveCockpitView: React.FC<ExecutiveCockpitViewProps> = ({
  title = "Cockpit Executivo RevOps & Inteligência de Carteira",
  onNavigate,
  userId,
  accountId,
}) => {
  const handleNavigate = React.useCallback(
    (route: string, opts?: { stage?: string }) => {
      if (onNavigate) {
        onNavigate(route, opts);
        return;
      }
      if (route === "deals") {
        window.location.hash = resolveStageHash(opts?.stage);
      } else {
        window.location.hash = `#!/${route}`;
      }
    },
    [onNavigate]
  );

  const props: SupersetEmbeddedProps = {
    mode: "executive_cockpit",
    title,
    onNavigate: handleNavigate,
    userId,
    accountId,
  };

  return <SupersetEmbeddedDashboard {...props} />;
};

export default ExecutiveCockpitView;
