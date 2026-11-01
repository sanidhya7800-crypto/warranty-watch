export interface WarrantyStatus {
  status: 'Active' | 'Expiring Soon' | 'Expired' | 'Unknown';
  days_to_expiry: number | null;
  coverage_end: string | null;
  coverage_basis: 'warranty' | 'extended' | 'none' | null;
  amc_status: 'Active' | 'Expiring Soon' | 'Expired' | null;
  amc_days_to_expiry: number | null;
  amc_expiry: string | null;
}

export interface Product {
  id: number;
  name: string;
  category: string;
  manufacturer: string;
  model_number: string;
  serial_number?: string | null;
  purchase_date: string;
  purchase_price?: number | null;
  warranty_duration_months?: number | null;
  warranty_expiry_date?: string | null;
  extended_warranty_expiry?: string | null;
  amc_expiry_date?: string | null;
  invoice_filename?: string | null;
  has_invoice: boolean;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  warranty: WarrantyStatus;
}

export interface ServiceRequest {
  id: number;
  product_id: number;
  manufacturer: string;
  issue_description: string;
  complaint_number?: string | null;
  service_portal_url?: string | null;
  request_date: string;
  status: 'Draft' | 'Submitted' | 'Pending' | 'Technician Assigned' | 'In Progress' | 'Resolved' | 'Rejected' | 'Unknown' | string;
  last_checked?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecallAlert {
  id: number;
  title: string;
  manufacturer: string;
  affected_model?: string | null;
  description?: string | null;
  source_url?: string | null;
  date_detected?: string | null;
  severity: 'Low' | 'Medium' | 'High' | 'Critical' | string;
  related_product_ids: number[];
  created_at: string;
}

export interface NotificationItem {
  id: number;
  type: string;
  message: string;
  product_id?: number | null;
  severity: 'info' | 'warning' | 'critical';
  is_read: boolean;
  created_at: string;
}

export interface TinyFishActivity {
  id: number;
  capability: 'search' | 'fetch' | 'agent' | 'browser' | 'monitor' | string;
  status: 'running' | 'completed' | 'failed' | 'demo' | string;
  mode: 'live' | 'demo';
  task_description?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  result_summary?: string | null;
  source_url?: string | null;
  error?: string | null;
  detail?: any;
  created_at: string;
}

export interface MonitorItem {
  id: number;
  tinyfish_monitor_id?: string | null;
  name: string;
  monitor_type: 'search' | 'fetch';
  target: string;
  schedule_cron: string;
  status: string;
  purpose?: string | null;
  product_id?: number | null;
  last_run_at?: string | null;
  last_change_summary?: string | null;
  last_error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardMetrics {
  total_products: number;
  active_warranties: number;
  expiring_warranties: number;
  expired_warranties: number;
  open_service_requests: number;
  alert_count: number;
  upcoming_expiries: Product[];
  recent_activity: TinyFishActivity[];
  warranty_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
}

export interface KeyStatus {
  key_present: boolean;
  key_length?: number;
  mode: 'live' | 'demo';
}

export interface TinyFishHealth {
  key_present: boolean;
  key_length?: number;
  mode: 'live' | 'demo';
  api_reachable: boolean | null;
  api_error?: string | null;
  error_category?: string | null;
  capabilities: Record<string, string>;
  note?: string;
}
