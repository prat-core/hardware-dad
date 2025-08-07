import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Terminal, Trash2, Download, Settings } from "lucide-react";

interface SerialMonitorProps {
  logs: string[];
}

export const SerialMonitor = ({ logs }: SerialMonitorProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }) + '.' + now.getMilliseconds().toString().padStart(3, '0');
  };

  const getLogType = (log: string) => {
    if (log.toLowerCase().includes('error')) return 'error';
    if (log.toLowerCase().includes('warning')) return 'warning';
    if (log.toLowerCase().includes('agent:')) return 'agent';
    return 'info';
  };

  const getLogColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-destructive';
      case 'warning': return 'text-yellow-500';
      case 'agent': return 'text-secondary';
      default: return 'text-foreground';
    }
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4" />
          <h3 className="font-semibold">Serial Monitor</h3>
          <Badge variant="outline" className="text-xs">
            9600 baud
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <ScrollArea className="h-full">
          <div className="console-output">
            {logs.length === 0 ? (
              <div className="text-muted-foreground text-center py-8">
                <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Serial monitor ready</p>
                <p className="text-xs">Waiting for output...</p>
              </div>
            ) : (
              logs.map((log, index) => {
                const logType = getLogType(log);
                const logColor = getLogColor(logType);
                
                return (
                  <div key={index} className="flex gap-2 py-1 hover:bg-muted/20">
                    <span className="text-muted-foreground text-xs shrink-0 w-16">
                      {formatTimestamp()}
                    </span>
                    <span className={`text-xs ${logColor} flex-1`}>
                      {logType === 'agent' && (
                        <span className="bg-secondary/20 text-secondary px-1 rounded text-xs mr-2">
                          AI
                        </span>
                      )}
                      {log}
                    </span>
                  </div>
                );
              })
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </div>
      
      {/* Status Bar */}
      <div className="border-t border-border px-4 py-2 bg-panel-accent">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{logs.length} message{logs.length !== 1 ? 's' : ''}</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent rounded-full"></div>
            <span>Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
};