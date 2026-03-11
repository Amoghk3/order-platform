// ── Auth ────────────────────────────────────────────────
export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ── RBAC ────────────────────────────────────────────────
export interface Role {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Permission {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

// ── User ────────────────────────────────────────────────
export interface User {
  id: number;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

// ── Order ───────────────────────────────────────────────
export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_amount: string; // Decimal comes as string from JSON
  created_at: string;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
}

// ── JWT payload (decoded client-side) ───────────────────
export interface JwtPayload {
  sub: string;
  role: string;
  exp: number;
}
