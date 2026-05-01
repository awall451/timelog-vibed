import nodeAdapter from '@sveltejs/adapter-node';
import staticAdapter from '@sveltejs/adapter-static';

const demoMode = process.env.VITE_DEMO_MODE === 'true';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: demoMode
			? staticAdapter({ fallback: 'index.html', strict: false })
			: nodeAdapter(),
		alias: {}
	}
};

export default config;
