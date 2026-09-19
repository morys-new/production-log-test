/**
 * TYPES ONLY. No runtime code.
 * Metro (Expo) and Next.js erase `import type` — this file is never bundled.
 *
 * All consumers must use:  import type { ... } from '../../shared/types'
 */

export interface HealthResponse {
  status: string;
  db_version: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
