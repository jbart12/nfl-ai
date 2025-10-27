import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",
        secondary: "#059669",
        accent: "#DC2626",
        confidence: {
          high: "#10B981",
          medium: "#F59E0B",
          low: "#EF4444",
        },
        over: "#10B981",
        under: "#DC2626",
      },
    },
  },
  plugins: [],
}
export default config
