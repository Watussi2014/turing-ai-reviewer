import React, { useState } from 'react';
import Header from '@/components/layout/Header';
import AiReviewCard from '@/components/common/AiReviewCard';
import { Button } from '@/components/ui/button';

const MainContent = () => {
  const [showInput, setShowInput] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');

  const handleRepoClick = () => {
    setShowInput(prev => !prev);
  };

  const handleInputChange = (e) => {
    setRepoUrl(e.target.value);
  };

  const saveToLocalStorage = () => {
    localStorage.setItem('repoUrl', repoUrl);
  };

  return (
    <main className="flex-1 p-8 overflow-y-auto">
      <Header />
      <div className="mt-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Sprint: Statistical Inference</p>
            <h1 className="text-3xl font-bold text-white mt-1">Project - Analyzing A/B Tests</h1>
          </div>
          <div className="flex flex-col items-end">
            <Button 
              variant="outline" 
              className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
              onClick={handleRepoClick}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-github mr-2" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
              </svg>
              Repository
            </Button>

            {showInput && (
              <div className="mt-2 flex gap-2">
                <input 
                  type="text"
                  value={repoUrl}
                  onChange={handleInputChange}
                  placeholder="Enter GitHub repo URL"
                  className="px-2 py-1 rounded bg-gray-800 text-white border border-gray-600"
                />
                <Button onClick={saveToLocalStorage} className="bg-green-600 hover:bg-green-700">
                  Save
                </Button>
              </div>
            )}
          </div>
        </div>

        <div className="mt-10">
          <AiReviewCard />
        </div>

        <div className="mt-12 text-gray-300">
            <p className="mb-4">Congratulations on getting to the end of Sprint 2! You have almost completed a Sprint on a rather nuanced topic - statistical inference. You now know how to estimate population parameters from samples, how to express uncertainty using confidence intervals and how to test hypotheses. Now it is time to apply these skills on some real-world datasets.</p>
            <h3 className="text-lg font-semibold text-white mb-2">Objectives</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-400">
              <li>Practice analyzing experiments.</li>
              <li>Practice working with statistical Python packages.</li>
              <li>Practice formulating and testing hypotheses.</li>
              <li>Practice interpreting p-values and confidence intervals.</li>
            </ul>
          </div>
      </div>
    </main>
  );
};

export default MainContent;
