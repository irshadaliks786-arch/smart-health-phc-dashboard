import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  // GitHub Pages ke liye
  base: "/smart-health-phc-dashboard/",

  server: {
    host: "0.0.0.0",
    port: 5173,
  },
});
