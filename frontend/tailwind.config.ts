import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1A0A2E",
          mid: "#2D1654",
        },
        secondary: "#C084FC",
        accent: "#E879F9",
        gold: "#D4AF37",
        "text-dark": "#1A1A2E",
        "text-mid": "#4A4A6A",
        "text-muted": "#8A8AA8",
        "bg-light": "#F8F5FF",
        "bg-dark": "#0F0720",
        border: "#E8E0F0",
        hs: {
          low: "#EF4444",
          mid: "#F59E0B",
          good: "#10B981",
          excellent: "#6366F1",
        },
      },
      fontFamily: {
        display: ["var(--font-cormorant)", "Georgia", "serif"],
        sans: ["var(--font-jakarta)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "10px",
      },
    },
  },
  plugins: [],
};

export default config;
