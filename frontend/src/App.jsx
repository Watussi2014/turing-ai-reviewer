
import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import MarkdownMessage from './components/ui/mdMessages';
function App() {
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
    <div className="min-h-screen grid-pattern gradient-bg flex flex-col">
      <header className="container mx-auto py-6">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2"
        >
          <img 
            src="https://storage.googleapis.com/hostinger-horizons-assets-prod/218bdcfb-0707-4c21-9787-5b4c093a43d8/520c1ec8e62253f69c6475c3fd4cc23a.png"
            alt="Turing College Logo"
            className="h-8 w-8"
          />
          <h1 className="text-2xl font-bold">Turing AI Reviewer</h1>
        </motion.div>
      </header>

      <main className="container mx-auto flex-1 flex flex-col gap-6 px-4 pb-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-panel rounded-xl p-6 shadow-lg"
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="repo-url">GitHub Repository URL</Label>
              <div className="flex gap-2">
                <Input
                  id="repo-url"
                  placeholder="https://github.com/username/repository"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  className="flex-1"
                  disabled={isAnalyzing || isAnalyzed}
                />
                <Button 
                  onClick={handleAnalyzeRepo} 
                  disabled={isAnalyzing || isAnalyzed || !repoUrl}
                  className="glow"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing
                    </>
                  ) : isAnalyzed ? (
                    <>
                      <CheckCircle2 className="mr-2 h-4 w-4" />
                      Analyzed
                    </>
                  ) : (
                    "Analyze Repository"
                  )}
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {isAnalyzed && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-panel rounded-xl flex-1 flex flex-col shadow-lg overflow-hidden"
          >
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold">Chat with AI about this repository</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="flex flex-col gap-4">
                {messages.map((message, index) => (
                  <div 
                    key={index} 
                    className={`chat-bubble ${message.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}
                  >
                    <MarkdownMessage content={message.text} />
                  </div>
                ))}
                
                {isTyping && (
                  <div className="chat-bubble bot-bubble">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
            
            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <Input
                  placeholder="Ask about the project..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1"
                />
                <Button onClick={handleSendMessage} className="glow">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </main>

      <footer className="container mx-auto py-4 text-center text-sm text-muted-foreground">
        <p>Turing AI Project Reviewer &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
