// API Configuration
// In development: uses Vite proxy (/api)
// In production: uses the VITE_API_URL environment variable

export const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export function getApiUrl(path: string): string {
  // If we have a full API URL (production), use it
  if (API_BASE_URL) {
    return `${API_BASE_URL}${path}`;
  }
  // Otherwise, use relative path (development with Vite proxy)
  return path;
}

