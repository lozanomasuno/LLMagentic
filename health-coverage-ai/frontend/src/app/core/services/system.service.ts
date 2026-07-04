import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SystemStatus, DocumentInfo } from '../models/system.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SystemService {
  private readonly http = inject(HttpClient);

  getSystemStatus(): Observable<SystemStatus> {
    return this.http.get<SystemStatus>(`${environment.apiUrl}/system`);
  }

  getDocuments(): Observable<DocumentInfo[]> {
    return this.http.get<DocumentInfo[]>(`${environment.apiUrl}/documents`);
  }
}
