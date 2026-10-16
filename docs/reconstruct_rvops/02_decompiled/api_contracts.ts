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
