import * as React from "react";
import { ConsignmentSurgicalBoard } from "@/features/keypartners/ConsignmentSurgicalBoard";
import { DentgoExpressCockpit } from "@/features/dentgo/DentgoExpressCockpit";
import { LandingPageBuilder } from "@/features/campaigns/LandingPageBuilder";
import { SupersetEmbeddedDashboard } from "@/features/bi/SupersetEmbeddedDashboard";
import { DicomStl3DViewer } from "@/features/imaging/DicomStl3DViewer";
import { RbacHierarchyTree } from "@/features/rbac/RbacHierarchyTree";
import { CredentialsVaultPage } from "@/features/settings/CredentialsVaultPage";
import { LiveKitDealRoomModal } from "@/features/communications/LiveKitDealRoomModal";
import { IcpScoringDashboard } from "@/features/scoring/IcpScoringDashboard";
import { ContactsCrmWorkspace } from "@/features/contacts/ContactsCrmWorkspace";
import { ContractsDocumensoWorkspace } from "@/features/contracts/ContractsDocumensoWorkspace";
import { SupportAnvisaWorkspace } from "@/features/support/SupportAnvisaWorkspace";
import { CalcomReactivationWorkspace } from "@/features/scheduling/CalcomReactivationWorkspace";
import { IntelligenceSuiteWorkspace } from "@/features/intelligence/IntelligenceSuiteWorkspace";

import { OmnichannelWorkspace } from "@/features/inbox/OmnichannelWorkspace";
import { ExecutiveCockpitView } from "@/features/dashboard/ExecutiveCockpitView";
import { DealsWorkspace } from "@/features/deals/DealsWorkspace";
import { MarketIntelRadarWorkspace } from "@/features/market_intel/MarketIntelRadarWorkspace";

export type AppRoute =
  | "dashboard"
  | "deals"
  | "contacts"
  | "omnichannel"
  | "keypartners"
  | "dentgo"
  | "video_sos"
  | "contracts"
  | "intelligence"
  | "market_intel"
  | "analytics"
  | "scheduling"
  | "rbac"
  | "support"
  | "settings"
  | "scoring"
  | "marketing"
  | "imaging";

export interface RouteConfig {
  id: AppRoute;
  title: string;
  suite: "crm" | "surgical" | "logistics" | "omnichannel" | "bi" | "governance";
  component: React.ComponentType<any>;
}

export interface RouterProps {
  currentRoute: string;
  onNavigate?: (route: any) => void;
}

export const AppRouter: React.FC<RouterProps> = ({ currentRoute, onNavigate }) => {
  switch (currentRoute) {
    case "deals":
      return <DealsWorkspace onNavigate={onNavigate} />;
    case "contacts":
      return <ContactsCrmWorkspace />;
    case "keypartners":
      return <ConsignmentSurgicalBoard />;
    case "dentgo":
      return <DentgoExpressCockpit />;
    case "omnichannel":
      return <OmnichannelWorkspace onOpenSosVideo={() => onNavigate && onNavigate("video_sos")} />;
    case "dashboard":
      return (
        <ExecutiveCockpitView
          onNavigate={(route) => onNavigate && onNavigate(route)}
        />
      );
    case "analytics":
      return (
        <SupersetEmbeddedDashboard
          mode="bi_studio"
          title="Estúdio BI Superset RLS & Agente Analítico Text-to-SQL"
          onNavigate={(route) => onNavigate && onNavigate(route)}
        />
      );
    case "video_sos":
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <LiveKitDealRoomModal
            inline
            dealTitle="Suporte Emergencial SOS Mesa Cirúrgica"
            contactName="Cirurgião em Campo Operatório"
          />
        </div>
      );
    case "imaging":
      return <DicomStl3DViewer />;
    case "contracts":
      return <ContractsDocumensoWorkspace />;
    case "intelligence":
      return <IntelligenceSuiteWorkspace />;
    case "market_intel":
      return <MarketIntelRadarWorkspace />;
    case "scheduling":
      return <CalcomReactivationWorkspace />;
    case "support":
      return <SupportAnvisaWorkspace />;
    case "scoring":
      return <IcpScoringDashboard />;
    case "marketing":
    case "campaigns":
      return <LandingPageBuilder />;
    case "rbac":
      return <RbacHierarchyTree />;
    case "settings":
      return <CredentialsVaultPage />;
    default:
      return <DealsWorkspace onNavigate={onNavigate} />;
  }
};

export default AppRouter;
