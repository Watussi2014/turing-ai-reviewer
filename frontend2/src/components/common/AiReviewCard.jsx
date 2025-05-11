
    import React from 'react';
    import { Link } from 'react-router-dom';
    import { BrainCircuit } from 'lucide-react';
    import { Button } from '@/components/ui/button';
    import { motion } from 'framer-motion';

    const AiReviewCard = () => (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700"
      >
        <div className="flex items-center mb-4">
          <motion.div
            initial={{ rotate: -15 }}
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 0.8, repeat: Infinity, repeatType: "mirror" }}
            className="mr-3"
          >
            <BrainCircuit size={28} className="text-indigo-400" />
          </motion.div>
          <h2 className="text-2xl font-semibold text-white">AI-Powered Review</h2>
        </div>
        <p className="text-gray-400 mb-6">
          Get instant feedback on your project. Our AI will analyze your work and provide valuable insights.
        </p>
        <div className="space-y-3 sm:space-y-0 sm:flex sm:space-x-3">
          <Link to="/review" className="w-full sm:w-auto">
            <Button size="lg" className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold shadow-lg transform hover:scale-105 transition-transform">
              Start AI Review
            </Button>
          </Link>
          <Button variant="outline" size="lg" className="w-full sm:w-auto border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors">
            Peer Review
          </Button>
          <Button variant="outline" size="lg" className="w-full sm:w-auto border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors">
            STL Review
          </Button>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          Pass a total of 2 reviews, with at least 1 led by an STL.
        </p>
      </motion.div>
    );

    export default AiReviewCard;
  