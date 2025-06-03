import React from 'react';

import { ThemeToggle } from '@/components/ThemeToggle';
import { WorkflowList } from '@/components/WorkflowList';
import { Button } from '@/components/ui/button'; // Placeholder

const App: React.FC = () => {
  return (
      <div className="min-h-screen bg-background text-foreground">
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 max-w-screen-2xl items-center">
            <div className="mr-4 hidden md:flex">
              <a href="/" className="mr-6 flex items-center space-x-2">
                {/* <Icons.logo className="h-6 w-6" /> */}
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className="h-6 w-6">
                  <rect width="256" height="256" fill="none"></rect>
                  <line x1="208" y1="128" x2="128" y2="208" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></line>
                  <line x1="192" y1="40" x2="40" y2="192" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></line>
                </svg>
                <span className="hidden font-bold sm:inline-block">
                  n8n Migration UI
                </span>
              </a>
              <nav className="flex items-center gap-6 text-sm">
                {/* Add nav links here if needed */}
              </nav>
            </div>
            <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
              <nav className="flex items-center">
                <ThemeToggle />
              </nav>
            </div>
          </div>
        </header>
        
        <main className="container mx-auto max-w-5xl p-4 md:p-8">
          <h1 className="text-3xl font-bold mb-6">Welcome to the n8n Migration Tool</h1>
          <p className="mb-4">Upload your n8n workflow and credential JSON files to begin the migration process.</p>
          
          <WorkflowList />

          <div className="mt-8 p-6 border rounded-lg shadow-sm bg-card">
            <h2 className="text-xl font-semibold mb-3">Credential Importer (Coming Soon)</h2>
            <p className="text-muted-foreground mb-4">Drag and drop your credential files here or click to browse.</p>
            <Button variant="secondary">Browse Files (Placeholder)</Button>
          </div>

        </main>

        <footer className="py-6 md:px-8 md:py-0 border-t">
          <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
            <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
              Built by Your Name/Team. The source code is available on <a href="#" target="_blank" rel="noreferrer" className="font-medium underline underline-offset-4">GitHub</a>.
            </p>
          </div>
        </footer>
      </div>
  );
};

export default App;
