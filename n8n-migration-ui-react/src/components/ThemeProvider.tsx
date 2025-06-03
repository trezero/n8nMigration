import React, { useEffect } from 'react';
import { useThemeStore, type Theme } from '@/stores/themeStore';

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  // storageKey is implicitly handled by Zustand's persist middleware name
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = "system",
}) => {
  // Zustand's persist middleware handles loading the theme from localStorage.
  // We initialize it in the store itself.
  const theme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);

  useEffect(() => {
    // If the store somehow didn't initialize from localStorage or has no value,
    // set it to defaultTheme. This is a fallback.
    if (!theme) {
      setTheme(defaultTheme);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultTheme, setTheme]); // Removed 'theme' from deps to avoid loop on init

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");

    let effectiveTheme = theme;
    if (theme === "system") {
      const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      effectiveTheme = systemPrefersDark ? "dark" : "light";
    }

    root.classList.add(effectiveTheme);
  }, [theme]);

  return <>{children}</>;
};
