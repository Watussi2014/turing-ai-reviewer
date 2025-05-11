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
    fetch('turing-ai-reviewer-production.up.railway.app:8080/api/analyze', {
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
    fetch('turing-ai-reviewer-production.up.railway.app:8080/api/chat', {
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
    <div className="min-h-screen bg-[#0f0f11] text-white font-sans">
      {!isAnalyzed ? (
        // PRE-ANALYSIS LAYOUT
        <div className="max-w-4xl mx-auto px-6 py-24">
          <h1 className="text-4xl font-bold mb-8 text-white">GitHub Repository URL</h1>
          <div className="bg-[#1a1b1e] p-6 rounded-xl border border-[#2b2c2f] shadow-md">
            <Label htmlFor="repoUrl" className="block text-gray-300 mb-2">GitHub Repository URL</Label>
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                id="repoUrl"
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="bg-[#121316] border border-[#2c2d30] text-white placeholder:text-gray-500 flex-grow"
                disabled={isAnalyzing}
              />
              <Button 
                onClick={handleAnalyzeRepo} 
                disabled={isAnalyzing || !repoUrl}
                className="bg-[#7c3aed] hover:bg-[#6d28d9] transition-all text-white"
              >
                {isAnalyzing ? (
                  <><Loader2 size={16} className="mr-2 animate-spin" /> Analyzing</>
                ) : (
                  <>Analyze</>
                )}
              </Button>
            </div>
  
            {isAnalyzing && (
              <div className="mt-6">
                <div className="w-full h-2 bg-[#2a2a2d] rounded-full overflow-hidden">
                  <div className="h-full w-full animate-pulse bg-gradient-to-r from-purple-500 via-indigo-500 to-purple-500" />
                </div>
                <p className="text-sm text-gray-400 mt-2">Processing repository data...</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        // POST-ANALYSIS CHAT UI
        <div className="w-full px-4 sm:px-8 py-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6 px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="Logo" className="w-8 h-8" />
              <h2 className="text-2xl font-semibold text-white">Chat with AI about this repository</h2>
            </div>
            <Button
              onClick={() => window.location.href = '/'}
              variant="outline"
              className="border border-[#2c2d30] text-gray-300 hover:bg-[#2a2a2e]"
            >
              Back
            </Button>
          </div>
  
          {/* Fullscreen Chat Card */}
          <div className="bg-[#1a1b1e] rounded-xl border border-[#2c2d30] shadow-md px-6 py-8 min-h-[calc(100vh-140px)] flex flex-col justify-between">
            <div className="overflow-y-auto space-y-4 mb-4 max-h-[70vh] pr-2">
              {messages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}
                >
                  <div 
                    className={`inline-block max-w-3xl whitespace-pre-wrap px-4 py-3 rounded-lg text-sm ${
                      msg.sender === 'user' 
                        ? 'bg-[#7c3aed] text-white' 
                        : 'bg-[#2c2d30] text-gray-200'
                    }`}
                  >
                    <MarkdownMessage content={msg.text} />
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="text-sm text-gray-400">AI is typing...</div>
              )}
            </div>
  
            {/* Chat input */}
            <div className="pt-4 border-t border-[#2c2d30]">
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask me about the repository..."
                  className="bg-[#121316] border border-[#2c2d30] text-white placeholder:text-gray-500 flex-grow"
                  disabled={isTyping}
                />
                <Button 
                  onClick={handleSendMessage} 
                  disabled={!inputMessage.trim() || isTyping}
                  className="bg-[#7c3aed] hover:bg-[#6d28d9]"
                >
                  {isTyping ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
      <Toaster />
    </div>
  );
  
}  
export default AiReviewPage;