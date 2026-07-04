import { Component, input, computed } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { CoverageAnalysisResponse } from '../../core/models/coverage-analysis.model';

@Component({
  selector: 'app-coverage-result',
  imports: [MatCardModule, MatExpansionModule, MatDividerModule, MatChipsModule],
  templateUrl: './coverage-result.component.html',
  styleUrl: './coverage-result.component.scss',
})
export class CoverageResultComponent {
  readonly result = input.required<CoverageAnalysisResponse>();

  readonly resultLabel = computed(() => {
    switch (this.result().coverage_result) {
      case 'cubierto':
        return 'Cubierto';
      case 'no_cubierto':
        return 'No Cubierto';
      case 'cubierto_con_condiciones':
        return 'Cubierto con condiciones';
      default:
        return 'Pendiente';
    }
  });
}
