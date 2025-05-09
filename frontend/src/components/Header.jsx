
import React from "react";
import { motion } from "framer-motion";
import { FileCode } from "lucide-react";

const Header = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="py-6 mb-8"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center">
          <motion.div
            whileHover={{ rotate: 10, scale: 1.1 }}
            transition={{ type: "spring", stiffness: 300 }}
            className="mr-3 text-primary"
          >
            <FileCode size={36} />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
              Python File Uploader
            </h1>
            <p className="text-muted-foreground">
              Upload files to process with your Python application
            </p>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
