export type ServiceConnectionStatus = 'connected' | 'disconnected' | 'not_configured';
export type SystemHealth = 'operational' | 'degraded' | 'down';

export interface ServiceStatus {
  status: ServiceConnectionStatus;
  message?: string;
}

export interface SystemStatus {
  version: string;
  environment: string;
  status: SystemHealth;
  database: ServiceStatus;
  vectorstore: ServiceStatus;
}

export interface DocumentInfo {
  id: string;
  name: string;
  status: 'indexed' | 'processing' | 'error';
  chunks: number;
  indexed_at: string | null;
}
