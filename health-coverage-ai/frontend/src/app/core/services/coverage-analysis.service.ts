import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  CoverageAnalysisRequest,
  CoverageAnalysisResponse,
} from '../models/coverage-analysis.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class CoverageAnalysisService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/coverage-analysis`;
  private readonly suggestionsUrl = `${environment.apiUrl}/suggestions`;

  analyze(request: CoverageAnalysisRequest): Observable<CoverageAnalysisResponse> {
    return this.http.post<CoverageAnalysisResponse>(this.baseUrl, request);
  }

  getSuggestions(query: string): Observable<string[]> {
    return this.http.get<string[]>(this.suggestionsUrl, {
      params: { q: query },
    });
  }
}
