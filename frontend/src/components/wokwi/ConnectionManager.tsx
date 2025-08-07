import { useState, useCallback } from 'react';
import { ConnectionWire } from './ConnectionWire';

export interface Connection {
  id: string;
  fromComponent: string;
  toComponent: string;
  fromPin: string;
  toPin: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  color: string;
}

interface ConnectionManagerProps {
  connections: Connection[];
  onConnectionCreate?: (connection: Omit<Connection, 'id'>) => void;
  onConnectionDelete?: (connectionId: string) => void;
}

export const ConnectionManager = ({
  connections,
  onConnectionCreate,
  onConnectionDelete,
}: ConnectionManagerProps) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [pendingConnection, setPendingConnection] = useState<{
    fromComponent: string;
    fromPin: string;
    fromX: number;
    fromY: number;
  } | null>(null);

  const startConnection = useCallback((
    component: string, 
    pin: string, 
    x: number, 
    y: number
  ) => {
    setPendingConnection({
      fromComponent: component,
      fromPin: pin,
      fromX: x,
      fromY: y,
    });
    setIsConnecting(true);
  }, []);

  const completeConnection = useCallback((
    toComponent: string,
    toPin: string,
    toX: number,
    toY: number
  ) => {
    if (pendingConnection && onConnectionCreate) {
      const wireColors = ['#22d3ee', '#ef4444', '#22c55e', '#f59e0b', '#a855f7', '#ec4899'];
      const color = wireColors[connections.length % wireColors.length];
      
      onConnectionCreate({
        fromComponent: pendingConnection.fromComponent,
        toComponent,
        fromPin: pendingConnection.fromPin,
        toPin,
        fromX: pendingConnection.fromX,
        fromY: pendingConnection.fromY,
        toX,
        toY,
        color,
      });
    }
    
    setPendingConnection(null);
    setIsConnecting(false);
  }, [pendingConnection, connections.length, onConnectionCreate]);

  const cancelConnection = useCallback(() => {
    setPendingConnection(null);
    setIsConnecting(false);
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Render all established connections */}
      {connections.map((connection) => (
        <ConnectionWire
          key={connection.id}
          id={connection.id}
          startX={connection.fromX}
          startY={connection.fromY}
          endX={connection.toX}
          endY={connection.toY}
          color={connection.color}
          fromComponent={connection.fromComponent}
          toComponent={connection.toComponent}
          fromPin={connection.fromPin}
          toPin={connection.toPin}
        />
      ))}
      
      {/* Connection UI State */}
      {isConnecting && (
        <div className="absolute top-4 left-4 bg-primary text-primary-foreground px-3 py-2 rounded-lg shadow-lg z-50 pointer-events-auto">
          <p className="text-sm font-medium">
            Connecting from {pendingConnection?.fromComponent}:{pendingConnection?.fromPin}
          </p>
          <p className="text-xs opacity-80">Click on a pin to complete connection</p>
          <button
            onClick={cancelConnection}
            className="mt-2 text-xs underline hover:no-underline"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};

