import React, { useState, useRef, useEffect } from 'react';
// Remove the Link import since it's causing issues
import { BrainCircuit, ChevronRight, Send, Loader2, AlertCircle, CheckCircle2, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Toaster } from '@/components/ui/toaster';
import { useToast } from '@/components/ui/use-toast';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { motion } from 'framer-motion';
import MarkdownMessage from '@/components/ui/mdMessages';

const AiReviewPage = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnalyzed, setIsAnalyzed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const validateGithubUrl = (url) => {
    const githubRegex = /^https:\/\/github\.com\/[^\/]+\/[^\/]+\/?$/;
    return githubRegex.test(url);
  };

  const handleAnalyzeRepo = () => {
    if (!validateGithubUrl(repoUrl)) {
      toast({
        title: "Invalid GitHub URL",
        description: "Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)",
        variant: "destructive",
      });
      return;
    }
  
    setIsAnalyzing(true);
    
    // Call backend API to analyze the repository
    fetch('http://localhost:3000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repoUrl }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setIsAnalyzing(false);
        setIsAnalyzed(true);
        
        // Add welcome message from the bot
        setMessages([
          {
            sender: 'bot',
            text: data.response
          }
        ]);
        
        toast({
          title: "Repository Analyzed",
          description: "The project has been successfully analyzed. You can now ask questions about it.",
          variant: "default",
        });
      })
      .catch(error => {
        setIsAnalyzing(false);
        toast({
          title: "Analysis Failed",
          description: error.message || "Failed to analyze the repository. Please try again.",
          variant: "destructive",
        });
      });
  };
  
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: inputMessage }]);
    const userQuestion = inputMessage;
    setInputMessage('');
    
    // Simulate bot typing
    setIsTyping(true);
    
    // Call backend API to get a response
    fetch('http://localhost:3000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        repoUrl,
        message: userQuestion
      }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setIsTyping(false);
        setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
      })
      .catch(error => {
        setIsTyping(false);
        setMessages(prev => [...prev, { 
          sender: 'bot', 
          text: "Sorry, I encountered an error while processing your question. Please try again." 
        }]);
        
        toast({
          title: "Error",
          description: error.message || "Failed to get a response. Please try again.",
          variant: "destructive",
        });
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col text-white">
      {/* Initial Input Section - Shown only before analysis is complete */}
      {!isAnalyzed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full flex flex-col items-center justify-center h-screen -mt-16"
        >
          <div className="text-center mb-8">
            <BrainCircuit size={64} className="mx-auto mb-6 text-indigo-400" />
            <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400">
              GitHub Repo Analyzer
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Enter a GitHub repository URL to analyze its code and ask questions about it
            </p>
          </div>

          <div className="bg-slate-800 p-8 rounded-xl shadow-xl border border-slate-700 w-full max-w-3xl mx-auto">
            <Label htmlFor="repoUrl" className="text-md text-gray-300 mb-3 block">GitHub Repository URL</Label>
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                id="repoUrl"
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="bg-slate-900 border-slate-700 text-white placeholder:text-gray-500 flex-grow text-lg py-6"
                disabled={isAnalyzing}
              />
              <Button 
                onClick={handleAnalyzeRepo} 
                disabled={isAnalyzing || !repoUrl}
                className="bg-indigo-600 hover:bg-indigo-700 sm:w-auto w-full text-lg py-6 px-8"
              >
                {isAnalyzing ? (
                  <><Loader2 size={20} className="mr-2 animate-spin" /> Analyzing</>
                ) : (
                  <><Github size={20} className="mr-2" /> Analyze</>
                )}
              </Button>
            </div>

            {isAnalyzing && (
              <div className="mt-8 space-y-3">
                <motion.div
                  className="w-full h-3 bg-slate-700 rounded-full overflow-hidden"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-indigo-500"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 5, ease: "linear", repeat: Infinity }}
                  />
                </motion.div>
                <p className="text-sm text-gray-400 text-center">Processing repository data...</p>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Chat Interface - Expanded to full width after analysis */}
      {isAnalyzed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="bg-slate-800 rounded-xl shadow-2xl border border-slate-700 flex flex-col w-full max-w-6xl mx-auto p-1"
          style={{ height: 'calc(100vh - 40px)' }}
        >
        {/* Chat Messages Area */}
        <div className="flex-1 p-5 overflow-y-auto">
          {messages.length === 0 && !isAnalyzed && (
            <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
              <BrainCircuit size={40} className="mb-4 text-slate-700" />
              <h3 className="text-lg font-medium text-slate-500">Repository Analysis</h3>
              <p className="text-sm mt-1 max-w-md text-slate-600">
                Enter a GitHub repository URL and click "Analyze" to start exploring the codebase
              </p>
            </div>
          )}
          
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`mb-4 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-3/4 rounded-lg p-3 ${
                  msg.sender === 'user' 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-slate-700 text-gray-100'
                }`}
              >
                <MarkdownMessage content={msg.text} />
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-700 text-white rounded-lg p-3">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-75"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Chat Input Area - Only shown after analysis */}
        {isAnalyzed && (
          <div className="p-4 border-t border-slate-700">
            <div className="flex gap-2">
              <Input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me about the repository..."
                className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                disabled={isTyping}
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={!inputMessage.trim() || isTyping}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {isTyping ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Back button only shown when analysis is complete */}
        {isAnalyzed && (
          <div className="p-4 border-t border-slate-700">
            <Button 
              onClick={() => window.location.href = '/'} 
              variant="outline" 
              className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            >
              <ChevronRight size={16} className="mr-2 rotate-180" /> Back to Dashboard
            </Button>
          </div>
        )}
              </motion.div>
      )}
      <Toaster />
    </div>
  );
};

export default AiReviewPage;