import { useEffect } from 'react';

/**
 * Custom hook to handle scroll-triggered animations
 * Uses Intersection Observer for performance
 */
export function useScrollAnimations() {
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animationPlayState = 'running';
        }
      });
    }, observerOptions);

    setTimeout(() => {
      document.querySelectorAll('.animate-on-scroll').forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
      });
    }, 100);

    return () => observer.disconnect();
  }, []);
}
