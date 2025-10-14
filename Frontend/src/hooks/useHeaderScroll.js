import { useEffect } from 'react';

/**
 * Custom hook to handle header background opacity on scroll
 * Eliminates duplicate scroll handling code across pages
 */
export function useHeaderScroll() {
  useEffect(() => {
    const handleScroll = () => {
      const header = document.querySelector('header');
      if (header) {
        const currentScrollY = window.scrollY;
        if (currentScrollY > 100) {
          header.style.background = 'rgba(15, 23, 42, 0.95)';
        } else {
          header.style.background = 'rgba(15, 23, 42, 0.8)';
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
}
