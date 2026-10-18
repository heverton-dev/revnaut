import * as React from "react";
import { ConsignmentSurgicalBoard } from "@/features/keypartners/ConsignmentSurgicalBoard";
import { DentgoExpressCockpit } from "@/features/dentgo/DentgoExpressCockpit";
import { LandingPageBuilder } from "@/features/campaigns/LandingPageBuilder";
import { OmnichannelContextSidebar } from "@/features/inbox/OmnichannelContextSidebar";
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
  defaultComponent?: React.ReactNode;
}

export const AppRouter: React.FC<RouterProps> = ({ currentRoute, defaultComponent }) => {
  switch (currentRoute) {
    case "deals":
      return <>{defaultComponent}</>;
    case "contacts":
      return <ContactsCrmWorkspace />;
    case "keypartners":
      return <ConsignmentSurgicalBoard />;
    case "dentgo":
      return <DentgoExpressCockpit />;
    case "omnichannel":
      return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          <div className="lg:col-span-2">
            <OmnichannelContextSidebar contactIdentifier="cnt-01" contactId="cnt-01" currentDealId="deal-01" />
          </div>
          <div>
            <DicomStl3DViewer studyId="study-demo-01" />
          </div>
        </div>
      );
    case "dashboard":
      return (
        <SupersetEmbeddedDashboard
          mode="executive_cockpit"
          title="Cockpit Executivo RevOps & Inteligência de Carteira"
        />
      );
    case "analytics":
      return (
        <SupersetEmbeddedDashboard
          mode="bi_studio"
          title="Estúdio BI Superset RLS & Agente Analítico Text-to-SQL"
        />
      );
    case "video_sos":
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <LiveKitDealRoomModal
            inline
            dealId="sos-mesa-01"
            dealTitle="Suporte Emergencial SOS Mesa Cirúrgica"
            contactName="Cirurgião em Campo Operatório"
          />
        </div>
      );
    case "imaging":
      return <DicomStl3DViewer studyId="study-demo-01" />;
    case "contracts":
      return <ContractsDocumensoWorkspace />;
    case "intelligence":
      return <IntelligenceSuiteWorkspace />;
    case "scheduling":
      return <CalcomReactivationWorkspace />;
    case "support":
      return <SupportAnvisaWorkspace />;
    case "scoring":
      return <IcpScoringDashboard />;
    case "marketing":
    case "campaigns":
      return <LandingPageBuilder campaignId="camp-allon4-sp" />;
    case "rbac":
      return <RbacHierarchyTree accountId="0f14ffff" />;
    case "settings":
      return <CredentialsVaultPage />;
    default:
      return <>{defaultComponent}</>;
  }
};

export default AppRouter;
