import { Component, input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-loading-spinner',
  imports: [MatProgressSpinnerModule],
  template: `
    <div class="spinner-wrapper" [class.spinner-wrapper--overlay]="overlay()">
      <mat-spinner [diameter]="diameter()" />
      @if (message()) {
        <p class="spinner-message">{{ message() }}</p>
      }
    </div>
  `,
  styles: [
    `
      .spinner-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        padding: 24px;
      }
      .spinner-wrapper--overlay {
        position: fixed;
        inset: 0;
        background: rgba(255, 255, 255, 0.85);
        z-index: 999;
        justify-content: center;
      }
      .spinner-message {
        font-size: 0.9rem;
        color: #78909c;
        margin: 0;
      }
    `,
  ],
})
export class LoadingSpinnerComponent {
  readonly diameter = input<number>(40);
  readonly message = input<string>('');
  readonly overlay = input<boolean>(false);
}
