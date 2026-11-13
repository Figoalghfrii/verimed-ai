import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#F4F7FB",
        brand: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          500: "#3B82F6",
          600: "#1D7DFA",
          700: "#1565D8",
          800: "#1E40AF",
          900: "#1E3A8A",
        },
      },
      boxShadow: {
        bento: "0 10px 35px -10px rgba(15, 23, 42, 0.06)",
        glass: "0 14px 36px -12px rgba(29, 125, 250, 0.14)",
        pill: "0 4px 20px -2px rgba(15, 23, 42, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
