import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Affiliate } from '../models/affiliate.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AffiliateService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/affiliates`;

  findByDocument(documentNumber: string): Observable<Affiliate> {
    return this.http.get<Affiliate>(`${this.baseUrl}/${documentNumber}`);
  }
}
