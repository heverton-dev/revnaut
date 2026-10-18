import * as React from "react";
import { ConsignmentSurgicalBoard } from "@/features/keypartners/ConsignmentSurgicalBoard";
import { DentgoExpressCockpit } from "@/features/dentgo/DentgoExpressCockpit";
import { LandingPageBuilder } from "@/features/campaigns/LandingPageBuilder";
import { OmnichannelContextSidebar } from "@/features/inbox/OmnichannelContextSidebar";
import { SupersetEmbeddedDashboard } from "@/features/bi/SupersetEmbeddedDashboard";
import { DicomStl3DViewer } from "@/features/imaging/DicomStl3DViewer";
import { RbacHierarchyTree } from "@/features/rbac/RbacHierarchyTree";
import { CredentialsVaultPage } from "@/features/settings/CredentialsVaultPage";
import { GranolaCopilotCard } from "@/features/deals/components/GranolaCopilotCard";
import { CroVerifiedInput } from "@/features/contacts/components/CroVerifiedInput";
import { LiveKitDealRoomModal } from "@/features/communications/LiveKitDealRoomModal";
import { IcpScoringDashboard } from "@/features/scoring/IcpScoringDashboard";
import { R2DirectUploader } from "@/components/shared/R2DirectUploader";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";

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
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Base de Cirurgiões-Dentistas & Compliance CRO/CFO</CardTitle>
              <CardDescription>
                Validação determinística em tempo real junto ao Conselho Regional de Odontologia e score preditivo ICP.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CroVerifiedInput required />
            </CardContent>
          </Card>
          <IcpScoringDashboard />
        </div>
      );
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
    case "analytics":
    case "dashboard":
      return <SupersetEmbeddedDashboard userId="usr-director-br" dashboardId="dash-revops-executivo-01" />;
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
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Contratos Digitais Documenso & Custódia R2</CardTitle>
              <CardDescription>
                Assinatura eletrônica com manifesto criptográfico SHA-256 e arquivamento direto no Cloudflare R2.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <R2DirectUploader module="contracts" accept=".pdf" />
            </CardContent>
          </Card>
        </div>
      );
    case "intelligence":
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <GranolaCopilotCard dealId="d-101" />
        </div>
      );
    case "scheduling":
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <SupersetEmbeddedDashboard
            userId="usr-director-br"
            dashboardId="dash-calcom-reativacao-01"
            dashboardType="clinic_chair"
            title="Motor Cal.com • Reativação Preventiva de Pacientes (6/12/18m)"
          />
        </div>
      );
    case "support":
      return (
        <div className="space-y-6 max-w-5xl mx-auto">
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Tecnovigilância ANVISA, RMA & Laudos Tomográficos</CardTitle>
              <CardDescription>
                Abertura de garantia de osseointegração com anexação de evidências radiográficas e bloqueio preventivo de lote.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <R2DirectUploader module="dicom" accept=".dcm,.stl,.ply,.pdf,.jpg,.png" />
            </CardContent>
          </Card>
        </div>
      );
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
