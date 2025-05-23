import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        globals: true, // <-- enables global expect, test, describe, etc.
        environment: 'jsdom', // <-- simulates the DOM for React components
        setupFiles: './vitest.setup.js',
        testTimeout: 10000,
    },
});
