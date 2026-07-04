import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let userMessage = 'Ha ocurrido un error inesperado.';

      if (error.status === 0) {
        userMessage =
          'No se puede conectar con el servidor. Verifique que el backend esté en ejecución.';
      } else if (error.status === 404) {
        userMessage = error.error?.detail ?? 'Recurso no encontrado.';
      } else if (error.status === 501) {
        userMessage =
          error.error?.detail?.message ?? 'Esta función aún no está disponible.';
      } else if (error.status >= 500) {
        userMessage = 'Error del servidor. Por favor intente nuevamente.';
      }

      return throwError(() => ({ ...error, userMessage }));
    }),
  );
};
