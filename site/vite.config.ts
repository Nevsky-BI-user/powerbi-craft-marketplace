import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base = імʼя репозиторію: сайт живе на nevsky-bi-user.github.io/powerbi-craft-marketplace/
export default defineConfig({
  plugins: [react()],
  base: "/powerbi-craft-marketplace/",
});
