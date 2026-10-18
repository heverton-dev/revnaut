/**
 * API Contracts & Data Schemas — Rvops Reverse-Engineered
 * Reconstituído factual a partir de network intercept e bundles da aplicação.
 */

export interface RvopsUser {
  id: string | number;
  email: string;
  first_name: string;
  last_name: string;
  profile_img: string | null;
  phone_number: string;
  timezone: string;
  mfa_enabled: boolean;
  default_mfa_method: 'WHATSAPP' | 'EMAIL' | 'APP';
  is_temp_token?: boolean;
}

export interface RvopsAccount {
  id: string; // Ex: "0f14ffff"
  name: string; // Ex: "Sales Rocket"
  created_at?: string;
  plan_tier?: 'starter' | 'pro' | 'enterprise';
}

export interface UserRole {
  id: number;
  user_id: number;
  object:
    | 'ads'
    | 'asset'
    | 'billing'
    | 'campaign'
    | 'communication-inbox'
    | 'communication-management'
    | 'company'
    | 'config'
    | 'deal'
    | 'email'
    | 'form'
    | 'lead'
    | 'pipeline'
    | 'product'
    | 'report-dashboard'
    | 'task'
    | 'ticket';
  objectCreate: 0 | 1;
  objectRead: 0 | 1;
  objectEdit: 0 | 1;
  objectDelete: 0 | 1;
  mktPublish: 0 | 1;
}

export interface AuthLoginResponse {
  access_token: string;
  refresh_token: string;
  user: RvopsUser;
  roles: UserRole[];
}

export interface Contact {
  id: number | string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company_name?: string;
  tags?: string[];
  owner_id?: number | string;
  owner_name?: string;
  created_at: string;
  updated_at: string;
  score?: number;
  status?: string;
}

export interface ContactListRequest {
  page?: number;
  limit?: number;
  search?: string;
  filters?: {
    owner_id?: string[];
    company_id?: string[];
    tags?: string[];
    created_after?: string;
    created_before?: string;
  };
}

export interface ContactListResponse {
  total: number;
  page: number;
  limit: number;
  data: Contact[];
}

export interface PipelineStage {
  id: number;
  pipeline_id: number;
  name: string;
  order: number;
  color?: string;
  probability?: number;
}

export interface Deal {
  id: number | string;
  title: string;
  value: number;
  stage_id: number;
  pipeline_id: number;
  contact_id?: number | string;
  contact_name?: string;
  company_id?: number | string;
  company_name?: string;
  owner_id: number | string;
  owner_name: string;
  expected_close_date?: string;
  created_at: string;
}

export interface PipelineWithDeals {
  id: number;
  name: string;
  stages: Array<PipelineStage & { deals: Deal[]; total_value: number }>;
}

export interface ChatConversation {
  id: string;
  channel: 'whatsapp' | 'webchat' | 'sms';
  contact_id: string | number;
  contact_name: string;
  last_message: string;
  last_message_at: string;
  unread_count: number;
  status: 'open' | 'pending' | 'resolved';
  assigned_to?: string;
}

export interface Ticket {
  id: number | string;
  subject: string;
  status: 'novo' | 'em_andamento' | 'aguardando_cliente' | 'resolvido';
  priority: 'baixa' | 'media' | 'alta' | 'urgente';
  requester_name: string;
  requester_email: string;
  assigned_agent?: string;
  created_at: string;
  sla_due_at?: string;
}

export interface Task {
  id: number | string;
  title: string;
  due_date: string;
  completed: boolean;
  type: 'ligacao' | 'email' | 'reuniao' | 'whatsapp' | 'tarefa';
  associated_deal_id?: number | string;
  associated_contact_name?: string;
  owner_id: number | string;
}

export interface AccountUsageLimit {
  object: string; // 'contacts' | 'users' | 'storage'
  current_used: number;
  max_limit: number;
  percentage: number;
}

// ==========================================
// Contratos Canônicos — Revnaut Dental Ops
// ==========================================

export type DataScopeEnum = 'self' | 'team' | 'subtree' | 'business_unit' | 'tenant_global';

export interface UserContext {
  user_id: string;
  account_id: string;
  role_id: string;
  team_id?: string | null;
  business_unit_id?: string | null;
  data_scope: DataScopeEnum;
  permissions: string[];
  is_superadmin: boolean;
}

export interface DentalContact extends Contact {
  cro: string;
  cro_uf: string;
  specialty: string;
  work_model: string;
  monthly_implants_volume: string;
  customer_type: 'Cirurgião' | 'Professor/KOL' | 'Aluno Especialização' | 'Clínica/DSO';
  city?: string;
  state?: string;
}

export interface ConsignmentBoxItem {
  id: string;
  sku: string;
  description: string;
  batch_number: string;
  expiry_date: string;
  quantity: number;
  unit_price: number;
}

export interface ConsignmentBox {
  id: string;
  account_id: string;
  contact_id: number | string;
  clinic_name: string;
  cro: string;
  box_status: 'em_campo' | 'em_cirurgia' | 'fechamento_pendente' | 'faturada_totvs';
  total_items: number;
  total_value: number;
  items: ConsignmentBoxItem[];
  created_at: string;
  updated_at: string;
}

export interface TotvsOrderItem {
  item_code: string; // SC6 B1_COD
  quantity: number;  // SC6 C6_QTD
  unit_price: number; // SC6 C6_PRCVEN
  total_value: number; // SC6 C6_VALOR
}

export interface TotvsOrderPayload {
  order_id: string;
  deal_id?: string;
  account_id: string;
  customer_code: string; // SA1 A1_COD
  customer_branch: string; // SA1 A1_LOJA
  customer_tax_id: string; // SA1 A1_CGC (CPF ou CNPJ)
  cro?: string;
  cro_uf?: string;
  total_amount: number;
  items: TotvsOrderItem[];
  payment_condition: string;
  sales_channel: string;
  idempotency_key: string;
}

export interface HierarchyPreset {
  name: 'fabrica_enxuta' | 'nacional_expansao' | 'multidivisao_produtos' | 'multinacional_enterprise';
  title: string;
  description: string;
  business_units_count: number;
  teams_count: number;
  roles_count: number;
}

export type RelationshipTypeEnum = 'operates_at' | 'partner_cadcam' | 'teaches_at' | 'kol_speaker';

export interface ContactInstitution {
  id: string;
  account_id: string;
  contact_id: number;
  institution_id: string;
  relationship_type: RelationshipTypeEnum;
  role_title?: string;
  is_kol: boolean;
  notes?: string;
  created_at: string;
  institution_name?: string;
  institution_type?: string;
  contact_name?: string;
  contact_cro?: string;
}

export interface ClinicalGraphNode {
  id: string;
  label: string;
  node_type: 'surgeon' | 'clinic' | 'cadcam_lab' | 'university' | 'radiology';
  metadata?: Record<string, any>;
}

export interface ClinicalGraphEdge {
  source: string;
  target: string;
  relationship: string;
  is_kol: boolean;
  label: string;
}

export interface ClinicalGraphResponse {
  nodes: ClinicalGraphNode[];
  edges: ClinicalGraphEdge[];
  total_nodes: number;
  total_edges: number;
  kol_speakers_count: number;
}

export interface ChurnRiskItem {
  contact_id: number;
  name: string;
  cro?: string;
  clinic_name?: string;
  uf?: string;
  tier: string;
  monthly_implant_volume: number;
  avg_reorder_interval_days: number;
  days_since_last_order: number;
  days_overdue: number;
  last_order_date?: string;
  churn_risk_score: number;
  churn_risk_level: 'baixo' | 'medio' | 'alto' | 'critico';
  recommended_action: string;
}

export interface ChurnRiskSummary {
  total_monitored: number;
  critical_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

export interface ChurnRiskResponse {
  summary: ChurnRiskSummary;
  radar: ChurnRiskItem[];
}

// =============================================================================
// FASE 8: ERP Fiscal Hub, Orthanc DICOM 3D & Webhooks Outbound (TICKETS 38-40)
// =============================================================================

export interface ErpFiscalInvoice {
  id: string;
  account_id: string;
  erp_type: 'totvs_protheus' | 'sap_b1' | 'sankhya';
  flow_type: 'REMITTANCE_5917' | 'RETURN_1918' | 'SALE_5113';
  reference_id?: string;
  cfop: string;
  nfe_number: string;
  nfe_series: string;
  nfe_access_key: string;
  recipient_cnpj_cpf: string;
  recipient_name: string;
  total_invoice_value: number;
  xml_r2_key: string;
  danfe_pdf_r2_key: string;
  xml_url?: string;
  danfe_pdf_url?: string;
  status: string;
  sefaz_protocol?: string;
  windmill_job_id?: string;
  created_at?: string;
}

export interface ImagingStudy {
  id: string;
  account_id: string;
  patient_name?: string | null;
  patient_anonymized_id: string;
  deal_id?: string | null;
  ticket_id?: string | null;
  study_type: 'DICOM_CBCT' | 'INTRAORAL_STL' | 'INTRAORAL_PLY' | 'GUIDED_SURGERY_PLAN';
  orthanc_study_id?: string | null;
  r2_storage_key: string;
  file_name: string;
  file_size_bytes: number;
  slice_count: number;
  jaw_type: 'MAXILA' | 'MANDIBULA' | 'AMBAS' | 'PERIAPICAL';
  bone_density_estimate: string;
  implant_site?: string | null;
  is_anonymized: boolean;
  created_at?: string;
}

export interface ImagingStudyViewerSession {
  study_id: string;
  viewer_token: string;
  viewer_stream_url: string;
  r2_public_url: string;
  study_type: string;
  patient_anonymized_id: string;
  jaw_type: string;
  bone_density_estimate: string;
  implant_site?: string | null;
  slice_count: number;
  recommended_implant_diameter_mm: number;
  recommended_implant_length_mm: number;
  bone_thickness_mm: number;
  expires_in_seconds: number;
}

export interface WebhookSubscription {
  id: string;
  account_id: string;
  name: string;
  target_url: string;
  subscribed_events: string[];
  signing_secret: string;
  is_active: boolean;
  consecutive_failures: number;
  circuit_breaker_tripped: boolean;
  created_at?: string;
}

export interface WebhookDeliveryLog {
  id: string;
  subscription_id: string;
  account_id: string;
  event_name: string;
  target_url: string;
  signature_header: string;
  status_code?: number;
  response_body?: string;
  latency_ms: number;
  attempt: number;
  success: boolean;
  created_at?: string;
}



