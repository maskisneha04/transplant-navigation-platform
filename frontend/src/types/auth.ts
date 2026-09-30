export type UserRole = "patient" | "coordinator" | "hospital_admin" | "system_admin";

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiErrorBody {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}
