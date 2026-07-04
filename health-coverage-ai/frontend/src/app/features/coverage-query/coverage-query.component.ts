import { Component, input, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Affiliate } from '../../core/models/affiliate.model';
import {
  CoverageAnalysisRequest,
  CoverageAnalysisResponse,
} from '../../core/models/coverage-analysis.model';
import { CoverageAnalysisService } from '../../core/services/coverage-analysis.service';
import { CoverageResultComponent } from '../coverage-result/coverage-result.component';

@Component({
  selector: 'app-coverage-query',
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    CoverageResultComponent,
  ],
  templateUrl: './coverage-query.component.html',
  styleUrl: './coverage-query.component.scss',
})
export class CoverageQueryComponent {
  private readonly coverageService = inject(CoverageAnalysisService);

  readonly affiliate = input.required<Affiliate>();
  readonly queryText = signal('');
  readonly isAnalyzing = signal(false);
  readonly result = signal<CoverageAnalysisResponse | null>(null);
  readonly errorMessage = signal<string | null>(null);

  submit(): void {
    const query = this.queryText().trim();
    if (!query || query.length < 10) return;

    const request: CoverageAnalysisRequest = {
      document_number: this.affiliate().numero_documento,
      query,
    };

    this.isAnalyzing.set(true);
    this.result.set(null);
    this.errorMessage.set(null);

    this.coverageService.analyze(request).subscribe({
      next: (response) => {
        this.result.set(response);
        this.isAnalyzing.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.userMessage ?? 'Error al procesar la consulta.');
        this.isAnalyzing.set(false);
      },
    });
  }
}
