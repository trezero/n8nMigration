# Makefile for n8n Migration UI React project

.PHONY: help install dev build preview lint clean clean-modules test

# Default command: Show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install project dependencies (npm install)"
	@echo "  dev             Start the development server (npm run dev)"
	@echo "  build           Build the project for production (npm run build)"
	@echo "  preview         Preview the production build locally (npm run preview)"
	@echo "  lint            Lint the codebase (npm run lint)"
	@echo "  lint-fix        Attempt to automatically fix lint issues (npm run lint -- --fix)"
	@echo "  format          Format code with Prettier (npm run format)"
	@echo "  test            Run tests (npm run test)"
	@echo "  test-watch      Run tests in watch mode (npm run test -- --watch)"
	@echo "  shadcn-init     Initialize shadcn/ui (npx shadcn-ui@latest init)"
	@echo "  shadcn-add      Add a shadcn/ui component (e.g., make shadcn-add c=button)"
	@echo "  clean           Remove the build directory (dist/)"
	@echo "  clean-modules   Remove node_modules/ directory"
	@echo "  clean-all       Remove build directory and node_modules/"

# Variables
NPM = npm
NPX = npx

# Project commands
install:
	@echo "Installing dependencies..."
	$(NPM) install

dev:
	@echo "Starting development server..."
	$(NPM) run dev

build:
	@echo "Building for production..."
	$(NPM) run build

preview:
	@echo "Previewing production build..."
	$(NPM) run preview

lint:
	@echo "Linting codebase..."
	$(NPM) run lint

lint-fix:
	@echo "Attempting to fix lint issues..."
	$(NPM) run lint -- --fix

format:
	@echo "Formatting code with Prettier..."
	$(NPM) run format

test:
	@echo "Running tests..."
	$(NPM) run test

test-watch:
	@echo "Running tests in watch mode..."
	$(NPM) run test -- --watch

# shadcn/ui commands
shadcn-init:
	@echo "Initializing shadcn/ui..."
	$(NPX) shadcn-ui@latest init

shadcn-add:
	@echo "Adding shadcn/ui component: $(c)..."
	@$(NPX) shadcn-ui@latest add $(c)

# Cleaning commands
clean:
	@echo "Cleaning build directory (dist/)..."
	rm -rf dist

clean-modules:
	@echo "Cleaning node_modules/ directory..."
	rm -rf node_modules

clean-all: clean clean-modules
	@echo "Project cleaned."
