/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // 新增这一行，直接覆盖错误规则
  safelist: [],
  theme: {
    extend: {},
  },
  plugins: [],
  presets:[require('@neo4j-ndl/base').tailwindConfig],
  corePlugins: {
    preflight: false,
  },
  prefix:""
}