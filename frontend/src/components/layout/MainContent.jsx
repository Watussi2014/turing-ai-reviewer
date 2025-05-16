import React, { useState, useEffect } from 'react';
import Header from '@/components/layout/Header';
import AiReviewCard from '@/components/common/AiReviewCard';
import { Button } from '@/components/ui/button';
import Modal from '@/components/ui/Modal';
import AiReviewPage from '@/pages/AiReviewPage';
import TutorialArrow from '@/components/common/TutorialArrow';

const MainContent = () => {
  const [showInput, setShowInput] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showTutorial, setShowTutorial] = useState(true);

  // Check if this is first visit
  useEffect(() => {
    const tutorialShown = localStorage.getItem('tutorialShown');
    if (tutorialShown) {
      setShowTutorial(true);
    }
  }, []);

  // Hide tutorial after some time
  useEffect(() => {
    if (showTutorial) {
      const timer = setTimeout(() => {
        setShowTutorial(true);
        //localStorage.setItem('tutorialShown', 'true');
      }, 60000); // Hide tutorial after 15 seconds

      return () => clearTimeout(timer);
    }
  }, [showTutorial]);

  const handleStartAiReview = () => {
    setIsModalOpen(true);
    if (showTutorial) {
      setShowTutorial(false);
      localStorage.setItem('tutorialShown', 'true');
    }
  };

  const handleRepoClick = () => {
    setShowInput(prev => !prev);
    if (showTutorial) {
      setShowTutorial(false);
      localStorage.setItem('tutorialShown', 'true');
    }
  };

  const handleInputChange = (e) => {
    setRepoUrl(e.target.value);
  };

  const saveToLocalStorage = () => {
    localStorage.setItem('repoUrl', repoUrl);
    setShowInput(false);
    toast({
      title: "Repository URL Saved",
      description: "Your GitHub repository URL has been saved successfully.",
      variant: "default",
    });
  };

  // Function to reset tutorial
  const resetTutorial = () => {
    localStorage.removeItem('tutorialShown');
    setShowTutorial(true);
  };

  return (
    <main className="flex-1 p-8 overflow-y-auto">
      <Header />
      <div className="mt-8">
        <div className="flex items-center justify-between relative">
          <div>
            <p className="text-sm text-gray-400">Sprint: AI Engineering</p>
            <h1 className="text-3xl font-bold text-white mt-1">Project - AI Reviewer</h1>
          </div>
          <div className="flex flex-col items-end relative">
            <Button
              variant="outline"
              className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
              onClick={handleRepoClick}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-github mr-2" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
              </svg>
              Repository
            </Button>

            {/* Repository button tutorial arrow */}
            {showTutorial && (
              <TutorialArrow
                direction="right"
                text="1.Set your GitHub repo URL here"
                className="right-full mr-4"
              />
            )}

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

        <div className="mt-10 relative">
          <AiReviewCard onStartReview={handleStartAiReview} />
          {/* AI Review button tutorial arrow */}
          {(
            <TutorialArrow
              direction="up"
              text="2.Click here to start the AI review"
              className="bottom-5 left-10 mb-4"
            />
          )}

        </div>

        <div className="mt-12 text-gray-400">
          <p className="mb-1">Welcome to our first version of the AI Reviewer. This is a proof of concept of what an automated AI reviewer could look like for Turing College.</p>
          <p className="text-gray-400 mb-2">
            For more informations, you can visit the{' '}
            <a 
              href="https://github.com/Watussi2014/turing-ai-reviewer" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-400 underline">
              GitHub repo</a>{' '}of the project.
          </p>
          <h3 className="text-lg font-semibold text-white mb-2">How it works</h3>
          <ol className="list-decimal list-inside space-y-1 text-gray-400">
            <li>It downloads all of the files from a GitHub repo.</li>
            <li>It automatically extract and find the task description and the requirements.</li>
            <li>It feeds the projects files, task description and requirements with a custom prompt to an LLM.</li>
            <li>It then generates a first review of the project.</li>
            <li>You can chat with the model to get further help.</li>
          </ol>
          <h3 className="text-lg font-semibold text-white mb-2 mt-4">Current issues</h3>
          <ul className="list-disc list-inside space-y-1 text-gray-400">
            <li>Right now the analysis is very slow, it can take 3+ minutes if the repo contains a lot of files. Rewriting some functions to be asynchronous would help with that.</li>
            <li>The LLM hallucinates some requirements. We need to find a good balance between how strict we want the LLM to follow the requirements and the suggestions it makes.</li>
            <li>Only public repos are supported. We can add support for private repos if we get an access token to Turing College github.</li>
          </ul>
        </div>

        {/* Small link to reset tutorial */}
        <div className="mt-6">
          <button
            onClick={resetTutorial}
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
            Show tutorial arrows again
          </button>
        </div>
      </div>

      {isModalOpen && (
        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <AiReviewPage />
        </Modal>
      )}
    </main>
  );
};

export default MainContent;
