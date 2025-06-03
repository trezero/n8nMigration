import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = "light" | "dark" | "system";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set: (partial: Partial<ThemeState> | ((state: ThemeState) => Partial<ThemeState>)) => void) => ({
      theme: "system" as Theme, // Initialize with 'system' as default
      setTheme: (theme: Theme) => set({ theme }),
    }),
    {
      name: 'n8n-migration-ui-theme', // localStorage key
    }
  )
);
