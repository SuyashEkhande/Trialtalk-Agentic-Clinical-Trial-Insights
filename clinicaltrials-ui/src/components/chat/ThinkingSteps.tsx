"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { ThinkingStep } from "@/lib/api";
import { Brain, Search, Database, MessageSquare, Terminal, Eye, Info } from "lucide-react";

interface ThinkingStepsProps {
  steps: ThinkingStep[];
}

function cleanLog(details: any): string {
  if (typeof details !== "string") {
    try {
      return JSON.stringify(details, null, 2);
    } catch {
      return String(details);
    }
  }

  // Check if it's a JSON string
  try {
    const parsed = JSON.parse(details);

    // If it's a structured log from LangGraph/LangChain
    if (parsed.type === "tool_start" && parsed.data) {
      const toolName = parsed.data.tool;
      const input = parsed.data.input;
      return `Tool Call: ${toolName}\nInput: ${typeof input === "object" ? JSON.stringify(input, null, 2) : input}`;
    }

    if (parsed.type === "tool_end" && parsed.data) {
      const toolName = parsed.data.tool;
      const output = parsed.data.output;
      return `Tool Result: ${toolName}\nOutput: ${typeof output === "object" ? JSON.stringify(output, null, 2) : output}`;
    }

    // Generic formatting for any other JSON
    return JSON.stringify(parsed, null, 2);
  } catch {
    // Not JSON, return as is
    return details;
  }
}

export function ThinkingSteps({ steps }: ThinkingStepsProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="mt-4 space-y-2 max-w-full overflow-hidden">
      <div className="flex items-center gap-2 text-sm font-semibold text-primary/80 mb-2">
        <div className="p-1 rounded bg-primary/10">
          <Brain className="w-3.5 h-3.5" />
        </div>
        <span>Agent Reasoning</span>
        <Badge variant="secondary" className="ml-auto text-[10px] h-5 px-2 bg-primary/5 text-primary-foreground/70 border-primary/10">
          {steps.length} {steps.length === 1 ? 'Step' : 'Steps'}
        </Badge>
      </div>
      <Accordion type="single" collapsible className="w-full space-y-1">
        {steps.map((step, index) => {
          let action = step.action || "Processing";
          const details = step.details || step.thought || JSON.stringify(step);

          let Icon = Info;
          if (action.toLowerCase().includes("search")) Icon = Search;
          if (action.toLowerCase().includes("database") || action.toLowerCase().includes("sql")) Icon = Database;
          if (action.toLowerCase().includes("final") || action.toLowerCase().includes("answer")) Icon = MessageSquare;
          if (action.toLowerCase().includes("tool") || action.toLowerCase().includes("process")) Icon = Terminal;
          if (action.toLowerCase().includes("observation") || action.toLowerCase().includes("view")) Icon = Eye;

          // Try to make action more readable
          if (typeof details === 'string' && details.includes('"tool":')) {
            try {
              const p = JSON.parse(details);
              if (p.data?.tool) {
                action = `Calling ${p.data.tool}`;
                if (p.type === 'tool_end') action = `Result from ${p.data.tool}`;
              }
            } catch { }
          }

          return (
            <AccordionItem key={index} value={`step-${index}`} className="border rounded-lg bg-muted/20 px-3 border-muted/30">
              <AccordionTrigger className="hover:no-underline py-2.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-all group">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded flex items-center justify-center bg-background border shadow-sm group-hover:bg-primary/5 transition-colors">
                    <Icon className="w-3 h-3 text-primary/70" />
                  </div>
                  <span className="truncate max-w-[200px] sm:max-w-[400px]">Step {index + 1}: {action}</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="pt-0 pb-3">
                <div className="pl-7 pr-2">
                  <div className="bg-background/80 rounded-md border p-2.5 text-[11px] font-mono text-muted-foreground overflow-x-auto whitespace-pre-wrap leading-relaxed shadow-sm">
                    {cleanLog(details)}
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
    </div>
  );
}
