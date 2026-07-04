import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AffiliateService } from '../../core/services/affiliate.service';
import { Affiliate } from '../../core/models/affiliate.model';
import { AffiliateCardComponent } from '../affiliate-card/affiliate-card.component';
import { CoverageQueryComponent } from '../coverage-query/coverage-query.component';

@Component({
  selector: 'app-affiliate-search',
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    AffiliateCardComponent,
    CoverageQueryComponent,
  ],
  templateUrl: './affiliate-search.component.html',
  styleUrl: './affiliate-search.component.scss',
})
export class AffiliateSearchComponent {
  private readonly affiliateService = inject(AffiliateService);

  readonly documentNumber = signal('');
  readonly isLoading = signal(false);
  readonly affiliate = signal<Affiliate | null>(null);
  readonly errorMessage = signal<string | null>(null);

  search(): void {
    const doc = this.documentNumber().trim();
    if (!doc) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.affiliate.set(null);

    this.affiliateService.findByDocument(doc).subscribe({
      next: (result) => {
        this.affiliate.set(result);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(
          err.userMessage ?? 'Error al buscar el afiliado.',
        );
        this.isLoading.set(false);
      },
    });
  }
}
