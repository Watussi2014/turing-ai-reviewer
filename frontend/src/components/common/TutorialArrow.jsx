import React from 'react';
import { motion } from 'framer-motion';

const TutorialArrow = ({ direction = 'right', text, className = '' }) => {
  // Set up the arrow direction styling and animation
  const arrowDirection = {
    right: 'rotate-0',
    left: 'rotate-180',
    up: '-rotate-90',
    down: 'rotate-90'
  };

  // Configure initial and animation properties based on direction
  const getInitialProps = () => {
    switch(direction) {
      case 'left': return { opacity: 0, x: 20 };
      case 'right': return { opacity: 0, x: -20 };
      case 'up': return { opacity: 0, y: 20 };
      case 'down': return { opacity: 0, y: -20 };
      default: return { opacity: 0, x: -20 };
    }
  };

  // Configure animation direction
  const getAnimationProps = () => {
    const baseProps = { opacity: 1, x: 0, y: 0 };
    
    switch(direction) {
      case 'left':
      case 'right':
        return { ...baseProps, x: [0, direction === 'left' ? -5 : 5, 0] };
      case 'up':
      case 'down':
        return { ...baseProps, y: [0, direction === 'up' ? -5 : 5, 0] };
      default:
        return { ...baseProps, x: [0, 5, 0] };
    }
  };

  return (
    <motion.div 
    className={`absolute flex items-center ${direction === 'up' ? 'flex-row-reverse' : 'flex-row'} ${className}`}
      initial={getInitialProps()}
      animate={getAnimationProps()}
      transition={{ 
        opacity: { duration: 0.5 },
        x: { repeat: Infinity, duration: 1.5, ease: "easeInOut" },
        y: { repeat: Infinity, duration: 1.5, ease: "easeInOut" }
      }}
    >
      <div className="bg-[#198E86] text-black px-3 py-1 rounded-md text-sm font-medium shadow-lg">
        {text}
      </div>
      <svg 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className={`w-8 h-8 text-[#198E86] ${arrowDirection[direction]}`}
      >
        <path d="M5 12H19M19 12L12 5M19 12L12 19" 
          stroke="currentColor" 
          strokeWidth="3" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    </motion.div>
  );
};

export default TutorialArrow;