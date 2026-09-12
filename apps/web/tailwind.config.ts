import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--bg)",
        ink: "var(--fg)",
        muted: "var(--muted)",
        line: "var(--border)",
        accent: "var(--accent)",
        danger: "var(--danger)",
      },
      maxWidth: {
        prose: "78ch",
      },
    },
  },
  plugins: [],
};

export default config;
