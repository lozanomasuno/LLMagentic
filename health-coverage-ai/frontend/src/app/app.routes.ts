import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/affiliate-search/affiliate-search.component').then(
        (m) => m.AffiliateSearchComponent,
      ),
  },
  { path: '**', redirectTo: '' },
];
