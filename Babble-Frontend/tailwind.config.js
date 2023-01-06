module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        primary: '#28774F',
        dark: '#0D5932',
        light: '#28774F',
        lighter: '#cdface',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
