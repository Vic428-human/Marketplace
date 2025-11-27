import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { ngrok } from "vite-plugin-ngrok";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [["babel-plugin-react-compiler"]],
      },
    }),
  ],
  server: {
    allowedHosts: ["risky-unutterably-gia.ngrok-free.dev"],
  },
});
