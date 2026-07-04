export type CoverageResult =
  | 'cubierto'
  | 'no_cubierto'
  | 'cubierto_con_condiciones';

export interface CoverageAnalysisRequest {
  document_number: string;
  query: string;
}

export interface DocumentSource {
  document: string;
  section: string;
  page: number | null;
  excerpt: string;
  relevance_score: number | null;
}

export interface AgentStep {
  step: string;
  description: string;
  result: string | null;
  duration_ms: number | null;
}

export interface CoverageAnalysisResponse {
  consultation_id: string;
  affiliate_id: string;
  coverage_result: CoverageResult;
  response_text: string;
  sources: DocumentSource[];
  agent_trace: AgentStep[];
  duration_ms: number;
}
