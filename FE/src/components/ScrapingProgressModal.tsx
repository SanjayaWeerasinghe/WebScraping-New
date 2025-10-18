import { useState, useEffect, useRef } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle2, XCircle, Loader2, Terminal } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ScrapingProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ProgressMessage {
  step: string;
  message: string;
  status: 'info' | 'success' | 'error' | 'progress';
  timestamp: Date;
}

interface StepInfo {
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

const PIPELINE_STEPS: StepInfo[] = [
  { name: 'Step 1: Web Scraping', description: 'Collecting product data from competitor websites', status: 'pending' },
  { name: 'Step 2: Price Cleaning', description: 'Normalizing and validating price information', status: 'pending' },
  { name: 'Step 3: Color Extraction', description: 'Analyzing and categorizing product colors', status: 'pending' },
  { name: 'Step 4: Database Import', description: 'Saving processed data to database', status: 'pending' },
];

export const ScrapingProgressModal = ({ isOpen, onClose }: ScrapingProgressModalProps) => {
  const [messages, setMessages] = useState<ProgressMessage[]>([]);
  const [steps, setSteps] = useState<StepInfo[]>(PIPELINE_STEPS);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [hasError, setHasError] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Start scraping when modal opens
  useEffect(() => {
    if (isOpen && !isRunning && !isComplete) {
      startScraping();
    }
  }, [isOpen]);

  // Cleanup EventSource on unmount or when modal closes
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  const updateStepStatus = (message: string) => {
    // Check if message indicates a step starting
    if (message.includes('▶ STARTING:')) {
      const stepMatch = message.match(/Step (\d+):/);
      if (stepMatch) {
        const stepIndex = parseInt(stepMatch[1]) - 1;
        setSteps(prev => prev.map((step, idx) => ({
          ...step,
          status: idx === stepIndex ? 'running' : step.status
        })));
      }
    }
    // Check if message indicates a step completed
    else if (message.includes('✓ COMPLETED:')) {
      const stepMatch = message.match(/Step (\d+):/);
      if (stepMatch) {
        const stepIndex = parseInt(stepMatch[1]) - 1;
        setSteps(prev => prev.map((step, idx) => ({
          ...step,
          status: idx === stepIndex ? 'completed' : step.status
        })));
      }
    }
    // Check if message indicates a step failed
    else if (message.includes('✗ FAILED:')) {
      const stepMatch = message.match(/Step (\d+):/);
      if (stepMatch) {
        const stepIndex = parseInt(stepMatch[1]) - 1;
        setSteps(prev => prev.map((step, idx) => ({
          ...step,
          status: idx === stepIndex ? 'failed' : step.status
        })));
      }
    }
  };

  const startScraping = async () => {
    setMessages([]);
    setSteps(PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' })));
    setIsRunning(true);
    setIsComplete(false);
    setHasError(false);

    try {
      // Use fetch to make POST request
      const response = await fetch(`${API_BASE_URL}/api/run-scraping`, {
        method: 'POST',
        headers: {
          'Accept': 'text/event-stream',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              const newMessage: ProgressMessage = {
                step: data.step,
                message: data.message,
                status: data.status,
                timestamp: new Date(),
              };

              setMessages(prev => [...prev, newMessage]);
              updateStepStatus(data.message);

              if (data.step === 'complete') {
                setIsComplete(true);
                setIsRunning(false);
              } else if (data.step === 'error') {
                setHasError(true);
                setIsRunning(false);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error starting scraping:', error);
      setMessages(prev => [...prev, {
        step: 'error',
        message: `Failed to start scraping: ${error instanceof Error ? error.message : 'Unknown error'}`,
        status: 'error',
        timestamp: new Date(),
      }]);
      setHasError(true);
      setIsRunning(false);
    }
  };

  const handleClose = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    onClose();
    // Reset state after a short delay to allow for smooth closing animation
    setTimeout(() => {
      setMessages([]);
      setSteps(PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' })));
      setIsRunning(false);
      setIsComplete(false);
      setHasError(false);
    }, 300);
  };

  const getStatusIcon = () => {
    if (hasError) {
      return <XCircle className="h-6 w-6 text-destructive" />;
    }
    if (isComplete) {
      return <CheckCircle2 className="h-6 w-6 text-green-500" />;
    }
    if (isRunning) {
      return <Loader2 className="h-6 w-6 text-primary animate-spin" />;
    }
    return <Terminal className="h-6 w-6 text-muted-foreground" />;
  };

  const getStatusText = () => {
    if (hasError) return "Scraping Failed";
    if (isComplete) return "Scraping Complete!";
    if (isRunning) return "Scraping in Progress...";
    return "Ready to Scrape";
  };

  const getStepIcon = (status: StepInfo['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-primary animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-destructive" />;
      case 'pending':
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-muted" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {getStatusIcon()}
            {getStatusText()}
          </DialogTitle>
          <DialogDescription>
            {isRunning && "Please wait while we scrape and process the data. This may take several minutes."}
            {isComplete && "All data has been successfully scraped and saved to the database."}
            {hasError && "An error occurred during the scraping process. Please check the logs below."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Step Progress Indicators */}
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="space-y-3">
              {steps.map((step, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {getStepIcon(step.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className={`text-sm font-medium ${
                        step.status === 'running' ? 'text-primary' :
                        step.status === 'completed' ? 'text-green-600' :
                        step.status === 'failed' ? 'text-destructive' :
                        'text-muted-foreground'
                      }`}>
                        {step.name}
                      </h4>
                      {step.status === 'running' && (
                        <span className="text-xs text-primary font-medium">In Progress...</span>
                      )}
                      {step.status === 'completed' && (
                        <span className="text-xs text-green-600 font-medium">Completed</span>
                      )}
                      {step.status === 'failed' && (
                        <span className="text-xs text-destructive font-medium">Failed</span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Progress Log */}
          <div className="border rounded-lg bg-slate-950 text-slate-50 p-4">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-800">
              <Terminal className="h-4 w-4" />
              <span className="text-sm font-medium">Console Output</span>
            </div>
            <ScrollArea className="h-[400px]" ref={scrollRef}>
              <div className="space-y-1 font-mono text-xs">
                {messages.length === 0 && (
                  <div className="text-slate-400">Waiting for output...</div>
                )}
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`py-1 ${
                      msg.status === 'error' ? 'text-red-400' :
                      msg.status === 'success' ? 'text-green-400' :
                      'text-slate-300'
                    }`}
                  >
                    <span className="text-slate-500">
                      [{msg.timestamp.toLocaleTimeString()}]
                    </span>{' '}
                    {msg.message}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-2">
            {!isRunning && (
              <Button onClick={handleClose} variant="outline">
                Close
              </Button>
            )}
            {isRunning && (
              <Button disabled variant="secondary">
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
