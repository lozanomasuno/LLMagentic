import { Component, input, computed } from '@angular/core';
import { NgClass } from '@angular/common';
import { AffiliateStatus, PaymentStatus } from '../../../core/models/affiliate.model';

type BadgeType = 'affiliation' | 'payment';
type BadgeStatus = AffiliateStatus | PaymentStatus;

@Component({
  selector: 'app-status-badge',
  imports: [NgClass],
  template: `
    <span class="badge" [ngClass]="badgeClass()">{{ status() }}</span>
  `,
  styles: [
    `
      .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }
      .badge--activo     { background: #e8f5e9; color: #2e7d32; }
      .badge--suspendido { background: #fff3e0; color: #e65100; }
      .badge--retirado   { background: #fce4ec; color: #ad1457; }
      .badge--al-dia     { background: #e8f5e9; color: #2e7d32; }
      .badge--en-mora    { background: #ffebee; color: #c62828; }
    `,
  ],
})
export class StatusBadgeComponent {
  readonly status = input.required<BadgeStatus>();
  readonly type = input.required<BadgeType>();

  readonly badgeClass = computed(() => {
    const key = this.status()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
    return `badge--${key}`;
  });
}
