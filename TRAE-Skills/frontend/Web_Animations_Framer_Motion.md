# Skill: Advanced Web Animations with Framer Motion

## Purpose
To create smooth, production-ready animations and transitions in React applications using Framer Motion.

## When to Use
- When building modern, polished UIs with animations
- For page transitions and navigation animations
- When implementing interactive micro-interactions
- For scroll-triggered animations
- When creating engaging onboarding experiences

## Procedure

### 1. Basic Animations
Simple animations with Framer Motion.

```jsx
import { motion } from 'framer-motion';

function BasicAnimation() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      Hello, World!
    </motion.div>
  );
}

function HoverAnimation() {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      className="px-4 py-2 bg-blue-500 text-white rounded"
    >
      Click Me
    </motion.button>
  );
}
```

### 2. Variants for Complex Animations
Define reusable animation variants.

```jsx
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 }
  }
};

function StaggeredList() {
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item, index) => (
        <motion.li key={index} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### 3. Page Transitions
Animate transitions between pages.

```jsx
import { AnimatePresence, motion } from 'framer-motion';
import { useLocation, Routes, Route } from 'react-router-dom';

const pageVariants = {
  initial: { opacity: 0, x: '-100vw' },
  in: { opacity: 1, x: 0 },
  out: { opacity: 0, x: '100vw' }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.5
};

function App() {
  const location = useLocation();
  
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route 
          path="/" 
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="in"
              exit="out"
              transition={pageTransition}
            >
              <HomePage />
            </motion.div>
          } 
        />
        <Route 
          path="/about" 
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="in"
              exit="out"
              transition={pageTransition}
            >
              <AboutPage />
            </motion.div>
          } 
        />
      </Routes>
    </AnimatePresence>
  );
}
```

### 4. Scroll-Triggered Animations
Animate elements as they scroll into view.

```jsx
import { motion, useScroll, useTransform } from 'framer-motion';

function ParallaxSection() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  
  return (
    <motion.div
      style={{ y, opacity }}
      className="h-screen flex items-center justify-center bg-gradient-to-b from-blue-500 to-purple-600"
    >
      <h1 className="text-6xl text-white">Scroll Down</h1>
    </motion.div>
  );
}

function ScrollReveal({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.div>
  );
}
```

### 5. Gestures and Drag
Implement drag-and-drop interactions.

```jsx
import { motion } from 'framer-motion';

function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
      dragElastic={0.1}
      whileDrag={{ scale: 1.1, rotate: 5 }}
      className="w-64 h-64 bg-white rounded-xl shadow-2xl flex items-center justify-center"
    >
      Drag Me!
    </motion.div>
  );
}
```

## Best Practices
- **Performance**: Use `will-change` for expensive animations
- **Reduced Motion**: Respect user's reduced motion preferences with `useReducedMotion`
- **Variants**: Use variants for reusable animations
- **AnimatePresence**: Always use AnimatePresence for exit animations
- **Spring Physics**: Prefer spring animations for natural feel
- **Test on Mobile**: Ensure animations work well on mobile devices
- **Don't Overdo It**: Use animations purposefully, not just for decoration
