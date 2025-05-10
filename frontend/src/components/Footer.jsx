
import React from "react";
import { motion } from "framer-motion";
import { Heart } from "lucide-react";

const Footer = () => {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="py-6 mt-12 border-t"
    >
      <div className="container mx-auto px-4">
        <div className="flex flex-col items-center justify-center">
          <p className="text-sm text-muted-foreground flex items-center">
            Made with{" "}
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, repeatDelay: 1.5, duration: 0.5 }}
              className="inline-block mx-1 text-red-500"
            >
              <Heart size={14} fill="currentColor" />
            </motion.span>{" "}
            for your Python projects
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            &copy; {new Date().getFullYear()} File Upload Service
          </p>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
