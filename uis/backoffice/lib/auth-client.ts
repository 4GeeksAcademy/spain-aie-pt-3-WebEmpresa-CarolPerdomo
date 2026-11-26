"use client";

export const TOKEN_KEY = "nexova_access_token";

export function getAuthToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveAuthToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const token = getAuthToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(input, { ...init, headers, cache: "no-store" });
  if (response.status === 401) {
    clearAuthToken();
    window.dispatchEvent(new Event("nexova:unauthorized"));
  }
  return response;
}
