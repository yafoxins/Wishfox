import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    define: {
      __APP_VERSION__: JSON.stringify(env.npm_package_version ?? "0.0.0"),
      __BOT_NAME__: JSON.stringify(env.TELEGRAM_BOT_NAME ?? env.VITE_BOT_NAME ?? ""),
    },
    server: {
      port: 5173,
      host: "0.0.0.0",
      proxy: {
        "/api": {
          target: env.BACKEND_URL ?? "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "dist",
    },
  };
});
