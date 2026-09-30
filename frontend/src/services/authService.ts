import api from "./api";
import type { AuthUser, TokenResponse } from "../types/auth";

export async function register(email: string, password: string): Promise<AuthUser> {
  const { data } = await api.post<AuthUser>("/auth/register", { email, password, role: "patient" });
  return data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return data;
}

export async function me(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>("/auth/me");
  return data;
}

export function logout(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isLoggedIn(): boolean {
  return Boolean(localStorage.getItem("access_token"));
}

export function extractErrorMessage(err: unknown): string {
  const anyErr = err as { response?: { data?: { error?: { message?: string } } } };
  return anyErr?.response?.data?.error?.message ?? "Something went wrong. Please try again.";
}
