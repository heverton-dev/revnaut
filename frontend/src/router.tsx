import * as React from "react";
import { ConsignmentSurgicalBoard } from "@/features/keypartners/ConsignmentSurgicalBoard";
import { DentgoExpressCockpit } from "@/features/dentgo/DentgoExpressCockpit";
import { LandingPageBuilder } from "@/features/campaigns/LandingPageBuilder";
import { OmnichannelContextSidebar } from "@/features/inbox/OmnichannelContextSidebar";
import { SupersetEmbeddedDashboard } from "@/features/bi/SupersetEmbeddedDashboard";
import { DicomStl3DViewer } from "@/features/imaging/DicomStl3DViewer";
import { RbacHierarchyTree } from "@/features/rbac/RbacHierarchyTree";

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
    case "keypartners":
      return <ConsignmentSurgicalBoard />;
    case "dentgo":
      return <DentgoExpressCockpit />;
    case "omnichannel":
      return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          <div className="lg:col-span-2">
            <OmnichannelContextSidebar contactId="cnt-01" currentDealId="deal-01" />
          </div>
          <div>
            <DicomStl3DViewer studyId="study-demo-01" />
          </div>
        </div>
      );
    case "analytics":
    case "dashboard":
      return <SupersetEmbeddedDashboard dashboardId="dash-revops-executivo-01" />;
    case "video_sos":
    case "imaging":
      return <DicomStl3DViewer studyId="study-demo-01" />;
    case "marketing":
    case "campaigns":
      return <LandingPageBuilder campaignId="camp-allon4-sp" />;
    case "rbac":
      return <RbacHierarchyTree accountId="0f14ffff" />;
    default:
      return <>{defaultComponent}</>;
  }
};

export default AppRouter;
