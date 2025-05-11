
    import React from 'react';
    import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
    import { Toaster } from '@/components/ui/toaster';
    import Sidebar from '@/components/layout/Sidebar';
    import MainContent from '@/components/layout/MainContent';
    import AiReviewPage from '@/pages/AiReviewPage';
    import FloatingActionButton from '@/components/common/FloatingActionButton';

    function App() {
      return (
        <Router>
          <div className="flex min-h-screen bg-slate-900">
            <Routes>
              <Route path="/" element={
                <>
                  <Sidebar />
                  <div className="flex-1 flex flex-col">
                    <MainContent />
                  </div>
                  <FloatingActionButton />
                </>
              } />
              <Route path="/review" element={<AiReviewPage />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      );
    }

    export default App;
  