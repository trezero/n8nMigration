module.exports = {
  root: true,
  env: { browser: true, es2020: true, node: true /* 'vitest-globals/env': true */ }, // Consider vitest-globals if using Vitest ESLint plugin
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'airbnb',
    'airbnb-typescript',
    'plugin:prettier/recommended', // Must be last to override other formatting rules
  ],
  ignorePatterns: [
    'dist',
    '.eslintrc.cjs',
    'vite.config.ts',
    'vitest.config.ts', // If you create this
    'tailwind.config.js',
    'postcss.config.js',
    'node_modules/',
    'coverage/',
    '*.yaml',
    '*.yml',
    'Makefile',
    'Dockerfile',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  plugins: ['react-refresh', '@typescript-eslint', 'prettier', 'jsx-a11y', /* 'vitest' */ ], // Consider vitest ESLint plugin
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'prettier/prettier': [
      'error',
      {
        // Prettier options can be defined here or in .prettierrc.json
        // semi: true, (example, ensure it matches .prettierrc.json)
      }
    ],
    'react/react-in-jsx-scope': 'off',
    'react/jsx-props-no-spreading': 'off',
    'react/require-default-props': 'off',
    'import/prefer-default-export': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
    'jsx-a11y/label-has-associated-control': [
        'warn', // Changed to warn as it can be noisy, but good to keep an eye on
        {
          assert: 'either',
        },
    ],
    'import/extensions': [
      'error',
      'ignorePackages',
      {
        js: 'never',
        jsx: 'never',
        ts: 'never',
        tsx: 'never',
      },
    ],
    'react/function-component-definition': [
      2,
      { 
        namedComponents: "arrow-function",
        unnamedComponents: "arrow-function",
      }
    ]
  },
  settings: {
    'import/resolver': {
      typescript: {
        project: './tsconfig.json',
      },
    },
  },
};
