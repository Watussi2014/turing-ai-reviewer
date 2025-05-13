
    import React from 'react';
    import { MessageSquare } from 'lucide-react';
    import { motion } from 'framer-motion';

    const FloatingActionButton = () => (
      <motion.button
        whileHover={{ scale: 1.1, rotate: 15 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-8 right-8 bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 rounded-full shadow-xl z-50"
      >
        <MessageSquare size={28} />
      </motion.button>
    );

    export default FloatingActionButton;
  