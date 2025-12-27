"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { TrialAgentAPI, QueryResponse, ThinkingStep } from "@/lib/api";
import { Send, User, Bot, Loader2, Plus, Trash2, Brain, Sparkles, Search, Database, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
  thinkingSteps?: ThinkingStep[];
  id: string;
}

function LoadingProgress() {
  const [step, setStep] = useState(0);
  const steps = [
    "Authenticating with Clinical Intelligence Gateway...",
    "Connecting to Clinical Trials MCP...",
    "Analyzing search parameters and medical entities...",
    "Querying ClinicalTrials.gov V2 repository...",
    "Synthesizing research findings and eligibility data..."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="flex items-center gap-3 text-xs text-muted-foreground">
      <span className="flex gap-1.5">
        <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
      </span>
      <span className="font-medium animate-in fade-in slide-in-from-left-1 duration-500 key={step}">
        {steps[step]}
      </span>
    </div>
  );
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Generate a random session ID on mount
    setSessionId(Math.random().toString(36).substring(7));
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTo({
          top: scrollContainer.scrollHeight,
          behavior: "smooth",
        });
      }
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await TrialAgentAPI.query({
        query: input,
        session_id: sessionId,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        thinkingSteps: response.thinking_steps,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error query:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please check if the backend is running.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(Math.random().toString(36).substring(7));
  };

  const clearSession = async () => {
    if (sessionId) {
      try {
        await TrialAgentAPI.deleteSession(sessionId);
        handleNewChat();
      } catch (error) {
        console.error("Error clearing session:", error);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background text-foreground max-w-5xl mx-auto border-x shadow-2xl overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b bg-background/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
              <Bot className="text-primary-foreground w-6 h-6" />
            </div>
            <div className="absolute -top-1 -right-1">
              <Sparkles className="w-3 h-3 text-primary animate-pulse" />
            </div>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">TrialTalk Agent</h1>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold flex items-center gap-1">
                Clinical Trial Intelligence <Badge variant="secondary" className="px-1 py-0 h-4 text-[8px] bg-primary/10 text-primary">v1.2</Badge>
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleNewChat} className="text-muted-foreground hover:text-primary transition-colors">
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
          <Button variant="ghost" size="sm" onClick={clearSession} className="text-muted-foreground hover:text-destructive transition-colors">
            <Trash2 className="w-4 h-4 mr-2" />
            Clear
          </Button>
        </div>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1 min-h-0 px-4 sm:px-6 py-8" ref={scrollRef}>
        <div className="space-y-8 max-w-3xl mx-auto pb-4">
          {messages.length === 0 && (
            <div className="h-[60vh] flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-20 h-20 rounded-3xl bg-primary/5 flex items-center justify-center mb-4 border border-primary/10">
                <Brain className="w-10 h-10 text-primary/40" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">How can I assist with your Research?</h2>
              <div className="max-w-md space-y-4">
                <p className="text-muted-foreground text-sm">
                  Ask about eligibility, trial locations, specific medical conditions, or drug research insights.
                </p>
                <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-primary/5 border border-primary/10 text-[11px] text-primary/80">
                  <Database className="w-3.5 h-3.5" />
                  <span>This AI agent connects with ClinicalTrials.gov official data source and provides answers based on that.</span>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full max-w-md">
                {[
                  { label: "Trials for Lung Cancer", icon: Search },
                  { label: "Phase 3 trials in NY", icon: Database },
                  { label: "Eligibility for IDH1 inhibitors", icon: Sparkles },
                  { label: "Recent Alzheimer's breakthroughs", icon: Brain }
                ].map((q) => (
                  <Button
                    key={q.label}
                    variant="outline"
                    size="sm"
                    className="h-auto py-3 px-4 text-xs font-medium justify-start hover:bg-primary/5 hover:border-primary/20 transition-all border-muted/60 overflow-hidden"
                    onClick={() => setInput(q.label)}
                  >
                    <q.icon className="w-3.5 h-3.5 mr-2.5 flex-shrink-0 text-primary/60" />
                    <span className="truncate">{q.label}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-3 duration-500`}>
              <div className={`flex gap-4 max-w-[90%] sm:max-w-[85%] ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <Avatar className={`border shadow-sm h-9 w-9 mt-1 ${m.role === "user" ? "border-primary/20" : "border-muted"}`}>
                  <AvatarFallback className={`text-[10px] font-bold ${m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                    {m.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </AvatarFallback>
                </Avatar>
                <div className={`space-y-3 min-w-0 flex-1 ${m.role === "user" ? "text-right" : "text-left"}`}>
                  <div className={`inline-block p-4 rounded-2xl shadow-sm text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-full ${m.role === "user"
                    ? "bg-primary text-primary-foreground rounded-tr-none font-medium ml-auto shadow-primary/10"
                    : "bg-card border rounded-tl-none border-muted/60"
                    }`}>
                    {m.role === 'assistant' ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                          ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2" {...props} />,
                          ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2" {...props} />,
                          li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                          h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-1" {...props} />,
                          code: ({ node, className, children, ...props }: any) => {
                            const match = /language-(\w+)/.exec(className || "");
                            return !match ? (
                              <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                                {children}
                              </code>
                            ) : (
                              <pre className="overflow-x-auto bg-muted/50 p-3 rounded-lg my-2 font-mono text-xs">
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              </pre>
                            );
                          }
                        }}
                      >
                        {m.content}
                      </ReactMarkdown>
                    ) : (
                      m.content
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start animate-in fade-in duration-300">
              <div className="flex gap-4 max-w-[80%]">
                <Avatar className="border shadow-sm h-9 w-9 h-9 w-9 border-muted">
                  <AvatarFallback className="bg-muted text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </AvatarFallback>
                </Avatar>
                <div className="p-4 bg-muted/20 border rounded-2xl rounded-tl-none border-dashed border-primary/20">
                  <LoadingProgress />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <footer className="p-6 border-t bg-background/80 backdrop-blur-md">
        <div className="max-w-3xl mx-auto relative group">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Search for conditions, trials, or eligibility criteria..."
            className="pr-14 py-7 rounded-2xl bg-muted/20 border-border focus-visible:ring-primary/30 focus-visible:border-primary/50 transition-all shadow-sm placeholder:text-muted-foreground/60"
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl h-11 w-11 shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </Button>
        </div>
        <p className="mt-4 text-[11px] text-center text-muted-foreground/80 flex items-center justify-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-primary/60" />
          <span>Always consult medical professionals.</span>
          <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
          <span>Built with <span className="text-red-500/80 mx-0.5">❤️</span> by <a href="https://www.linkedin.com/in/suyashekhande/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium decoration-primary/30 underline-offset-4">Suyash Ekhande</a></span>
        </p>
      </footer>
    </div>
  );
}
