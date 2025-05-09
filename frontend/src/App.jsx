
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import Navigation from "@/components/Navigation";
import ProjectForm from "@/components/ProjectForm";
import ProjectUpload from "@/components/ProjectUpload";

const App = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gradient-to-b from-background to-secondary/20">
        <Navigation />
        
        <main className="flex-grow container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<ProjectForm />} />
            <Route path="/upload" element={<ProjectUpload />} />
          </Routes>
        </main>
        
        <Toaster />
      </div>
    </Router>
  );
};

export default App;
