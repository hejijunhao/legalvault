// src/lib/animations.ts
// Centralized animation presets for Framer Motion
// Usage: <motion.div {...animations.fadeInUp}>

import type { Variants, Transition } from 'framer-motion'

// Standard transitions
export const transitions = {
  fast: { duration: 0.2 } as Transition,
  normal: { duration: 0.3 } as Transition,
  slow: { duration: 0.5 } as Transition,
  spring: { type: 'spring', stiffness: 300, damping: 30 } as Transition,
  smooth: { duration: 0.8, ease: [0.04, 0.62, 0.23, 0.98] } as Transition,
} as const

// Motion presets for spread syntax: <motion.div {...animations.fadeInUp}>
export const animations = {
  // Fade variations
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: transitions.normal,
  },

  fadeInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: transitions.slow,
  },

  fadeInUpSmall: {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 10 },
    transition: transitions.normal,
  },

  fadeInDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: transitions.slow,
  },

  // Slide variations
  slideInRight: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: transitions.normal,
  },

  slideInLeft: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: transitions.normal,
  },

  // Scale variations
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: transitions.fast,
  },

  scaleInBounce: {
    initial: { opacity: 0, scale: 0.5 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.5 },
    transition: transitions.spring,
  },

  // Expand/collapse for height animations
  expand: {
    initial: { height: 0, opacity: 0 },
    animate: { height: 'auto', opacity: 1 },
    exit: { height: 0, opacity: 0 },
    transition: transitions.fast,
  },

  // Combined effects
  popIn: {
    initial: { opacity: 0, y: 20, scale: 0.95 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: 20, scale: 0.95 },
    transition: transitions.normal,
  },
} as const

// Variants for list animations with stagger
export const listVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
}

export const listItemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.slow,
  },
}

// Grid stagger variants
export const gridVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export const gridItemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.slow,
  },
}

// Helper to create staggered animations with custom delay
export function withDelay(animation: typeof animations.fadeInUp, delay: number) {
  return {
    ...animation,
    transition: {
      ...animation.transition,
      delay,
    },
  }
}

// Helper to create index-based stagger delay
export function withStaggerIndex(animation: typeof animations.fadeInUp, index: number, staggerDelay = 0.05) {
  return withDelay(animation, index * staggerDelay)
}
