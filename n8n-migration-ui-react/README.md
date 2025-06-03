# n8n Migration Tool - Modern UI

This project is a modern React 18 frontend for the n8n Migration Tool, built with Vite, TypeScript, Tailwind CSS, and shadcn/ui.

## Project Overview

The goal is to replace the existing plain HTML checklist with a feature-rich, accessible, and responsive user interface. This UI will communicate with the existing backend REST endpoints for importing n8n workflows and credentials.

### Key Features (Planned)

*   Polished, accessible (WCAG 2.2 AA), and responsive design.
*   Workflow and credential management.
*   Drag-and-drop file uploads.
*   Search and filtering capabilities.
*   Bulk actions (e.g., import selected).
*   Light/Dark theme toggling.
*   Client-side validation of JSON files.
*   Progress indicators and toast notifications.

### Tech Stack

*   **Framework**: React 18
*   **Build Tool**: Vite
*   **Language**: TypeScript (strict mode)
*   **Styling**: Tailwind CSS v3 (with Typography plugin)
*   **UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
*   **State Management**: Zustand
*   **Forms & Validation**: React Hook Form + Zod (planned)
*   **Animations**: Framer Motion (planned)
*   **Icons**: Lucide React (used by shadcn/ui)
*   **Testing**: Vitest + React Testing Library (planned)
*   **Linting/Formatting**: ESLint (Airbnb config) + Prettier
*   **Git Hooks**: Husky (planned)

## Prerequisites

*   Node.js (v18.x or v20.x recommended)
*   npm (v9.x or v10.x recommended) or yarn

## Getting Started

1.  **Clone the repository (if applicable) or ensure you are in the project directory.**

2.  **Install dependencies:**
    ```bash
    npm install
    # or
    # yarn install
    ```

3.  **Initialize shadcn/ui (if not already done or if you need to reconfigure):**
    Follow the CLI prompts. Choose your preferred base color, CSS variables, etc.
    ```bash
    npx shadcn-ui@latest init
    ```

4.  **Add shadcn/ui components (examples):**
    You'll need to add the components used in the project if they are not already present or if you're setting up fresh.
    ```bash
    npx shadcn-ui@latest add button card checkbox dropdown-menu input label scroll-area select tabs toast dialog tooltip
    ```
    (Add other components as needed based on the UI requirements.)

5.  **Run the development server:**
    ```bash
    npm run dev
    # or
    # yarn dev
    ```
    The application should now be running on `http://localhost:3000` (or the port specified in `vite.config.ts`).

## Available Scripts

*   `npm run dev`: Starts the development server.
*   `npm run build`: Builds the application for production.
*   `npm run lint`: Lints the codebase using ESLint.
*   `npm run preview`: Serves the production build locally for preview.
*   `npm run test`: Runs tests using Vitest (once configured).

## Project Structure

```
n8n-migration-ui-react/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images, fonts, etc.
│   ├── components/
│   │   ├── ui/             # shadcn/ui components (generated)
│   │   ├── ThemeProvider.tsx # Theme context
│   │   └── ThemeToggle.tsx   # Theme switch button
│   │   └── WorkflowList.tsx  # Workflow import component
│   │   └── ...             # Other custom components
│   ├── config/             # App configuration (e.g., API endpoints)
│   ├── hooks/              # Custom React hooks
│   ├── lib/
│   │   └── utils.ts        # Utility functions (e.g., cn for Tailwind)
│   ├── services/           # API service calls
│   ├── stores/             # Global state (e.g., Zustand stores)
│   ├── styles/
│   │   └── global.css      # Tailwind base styles, custom global CSS (if any)
│   ├── types/              # TypeScript type definitions
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # React entry point
│   └── vite-env.d.ts       # Vite environment types
├── .eslintrc.cjs
├── .gitignore
├── .prettierrc.json
├── index.html              # Main HTML entry
├── Makefile                # Convenience make commands
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## Contributing

(Details on how to contribute, coding standards, branch strategy, etc. - To be defined)

## License

(Specify project license - To be defined)
