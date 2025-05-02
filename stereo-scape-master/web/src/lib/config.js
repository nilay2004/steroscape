export const BACKEND_ = import.meta.env.VITE_PUBLIC_BACKEND_URL || 'http://localhost:5000';
export const MAX_RETRY_ATTEMPTS = 3;
export const RETRY_DELAY = 2000; // 2 seconds
export const REQUEST_TIMEOUT = 15000; // 15 seconds
export const DEBUG_MODE = true; // Enable debug logging 