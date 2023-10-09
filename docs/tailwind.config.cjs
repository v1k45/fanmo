const starlightPlugin = require('@astrojs/starlight-tailwind');
const colors = require('tailwindcss/colors');
const defaultTheme = require("tailwindcss/defaultTheme");

const brandColors = {
	primary: {
	  DEFAULT: '#6B68F9',
	  100: '#E1E1FE',
	  200: '#C4C3FE',
	  300: '#A6A4FD',
	  400: '#908DFB',
	  500: '#6B68F9',
	  600: '#4E4CD6',
	  700: '#3634B3',
	  800: '#222190',
	  900: '#151377'
	},
	success: {
	  DEFAULT: '#9DCE0A',
	  50: colors.lime['50'],
	  100: '#F5FCCC',
	  200: '#E9FA9A',
	  300: '#D5F067',
	  400: '#BDE140',
	  500: '#9DCE0A',
	  600: '#82B107',
	  700: '#699405',
	  800: '#517703',
	  900: '#406201'
	},
	info: {
	  DEFAULT: '#028DFF',
	  50: colors.blue['50'],
	  100: '#CCF3FF',
	  200: '#99E1FF',
	  300: '#67CBFF',
	  400: '#41B3FF',
	  500: '#028DFF',
	  600: '#016DDB',
	  700: '#0151B7',
	  800: '#003993',
	  900: '#00287A'
	},
	warning: {
	  DEFAULT: '#FFBB00',
	  50: colors.yellow['50'],
	  100: '#FFF7CC',
	  200: '#FFEC99',
	  300: '#FFDE66',
	  400: '#FFD13F',
	  500: '#FFBB00',
	  600: '#DB9A00',
	  700: '#B77C00',
	  800: '#936000',
	  900: '#7A4C00'
	},
	error: {
	  DEFAULT: '#FF5647',
	  50: colors.rose['50'],
	  100: '#FFE9DA',
	  200: '#FFCDB5',
	  300: '#FFAB90',
	  400: '#FF8B75',
	  500: '#FF5647',
	  600: '#DB3333',
	  700: '#B7232F',
	  800: '#93162B',
	  900: '#7A0D28'
	},
	gray: {
	  DEFAULT: '#B0B2C1',
	  50: '#F9F9FA',
	  100: '#EDEDF1',
	  200: '#E0E0E6',
	  300: '#D1D2DB',
	  400: '#C2C3CF',
	  500: '#B0B2C1',
	  600: '#9D9FAD',
	  700: '#878895',
	  800: '#6A6C75',
	  900: '#3E3F45',
	  darkest: '#1D1D20'
	}
};

/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				accent: brandColors.primary,
			},
			fontFamily: {
				sans: ['"Work Sans"', ...defaultTheme.fontFamily.sans],
			}
		},
	},
	plugins: [starlightPlugin()],
}
