import { Component, input, computed } from '@angular/core';
import { DatePipe, CurrencyPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { Affiliate } from '../../core/models/affiliate.model';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-affiliate-card',
  imports: [MatCardModule, MatDividerModule, DatePipe, CurrencyPipe, StatusBadgeComponent],
  templateUrl: './affiliate-card.component.html',
  styleUrl: './affiliate-card.component.scss',
})
export class AffiliateCardComponent {
  readonly affiliate = input.required<Affiliate>();

  readonly nombreCompleto = computed(() => {
    const a = this.affiliate();
    const parts = [a.primer_nombre, a.primer_apellido];
    if (a.segundo_apellido) parts.push(a.segundo_apellido);
    return parts.join(' ');
  });

  readonly planClass = computed(() =>
    'plan-' + this.affiliate().plan.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''),
  );
}
