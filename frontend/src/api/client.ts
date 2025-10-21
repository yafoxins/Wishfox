import axios, { AxiosInstance } from "axios";

const apiBase = import.meta.env.VITE_API_BASE ?? "/api";

export const createApiClient = (csrfToken?: string): AxiosInstance => {
  const instance = axios.create({
    baseURL: apiBase,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  });

  instance.interceptors.request.use((config) => {
    // Remove JSON content-type for FormData so browser sets multipart boundary
    const isFormData = typeof FormData !== "undefined" && config.data instanceof FormData;
    if (isFormData) {
      if (config.headers) {
        delete (config.headers as Record<string, unknown>)["Content-Type"];
      }
    }
    if (csrfToken && config.method && config.method.toUpperCase() !== "GET") {
      config.headers = {
        ...config.headers,
        "X-CSRF-Token": csrfToken,
      };
    }
    return config;
  });

  return instance;
};
