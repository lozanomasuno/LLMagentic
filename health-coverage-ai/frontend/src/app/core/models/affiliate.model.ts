export type PlanType = 'Esencial' | 'Clásico' | 'Premium';
export type AffiliateStatus = 'Activo' | 'Suspendido' | 'Retirado';
export type PaymentStatus = 'Al día' | 'En mora';
export type DocumentType = 'CC' | 'CE' | 'TI' | 'PA';

export interface Affiliate {
  id_afiliado: string;
  tipo_documento: DocumentType;
  numero_documento: string;
  primer_nombre: string;
  primer_apellido: string;
  segundo_apellido: string | null;
  sexo: string;
  fecha_nacimiento: string;
  edad: number;
  ciudad: string;
  departamento: string;
  tipo_afiliado: string;
  parentesco: string;
  plan: PlanType;
  fecha_afiliacion: string;
  antiguedad_meses: number;
  estado_afiliacion: AffiliateStatus;
  estado_pagos: PaymentStatus;
  dias_mora: number;
  valor_pendiente_cop: number;
  tiene_autorizacion_previa: boolean;
  servicio_autorizado: string | null;
  numero_autorizacion: string | null;
  fecha_autorizacion: string | null;
  vigencia_autorizacion: string | null;
  preexistencia_declarada: boolean;
  descripcion_preexistencia: string | null;
}
