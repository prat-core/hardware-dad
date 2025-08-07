import { useEffect, useRef } from 'react';

interface WokwiComponentProps {
  type: string;
  id: string;
  x: number;
  y: number;
  rotation?: number;
  props?: Record<string, any>;
  onPinChange?: (pin: string, value: any) => void;
}

export const WokwiWrapper = ({ 
  type, 
  id, 
  x, 
  y, 
  rotation = 0, 
  props = {},
  onPinChange 
}: WokwiComponentProps) => {
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Import wokwi-elements when component mounts
    import('@wokwi/elements').catch(() => {
      console.warn('Wokwi elements not available, using fallback');
    });
  }, []);

  useEffect(() => {
    if (!elementRef.current) return;

    // Set up pin change listeners if needed
    const element = elementRef.current;
    
    const handlePinChange = (event: CustomEvent) => {
      if (onPinChange) {
        onPinChange(event.detail.pin, event.detail.value);
      }
    };

    element.addEventListener('pinchange', handlePinChange as EventListener);
    
    return () => {
      element.removeEventListener('pinchange', handlePinChange as EventListener);
    };
  }, [onPinChange]);

  const componentStyle = {
    position: 'absolute' as const,
    left: `${x}px`,
    top: `${y}px`,
    transform: `rotate(${rotation}deg)`,
    transformOrigin: 'center',
    width: '80px',
    height: '60px',
  };

  // Create the wokwi component element directly
  useEffect(() => {
    if (!elementRef.current) return;

    const container = elementRef.current;
    container.innerHTML = '';

    // Create the wokwi element
    const wokwiElement = document.createElement(`wokwi-${type}`);
    wokwiElement.id = id;
    
    // Set any additional props
    Object.entries(props).forEach(([key, value]) => {
      wokwiElement.setAttribute(key, String(value));
    });

    container.appendChild(wokwiElement);
  }, [type, id, props]);

  return (
    <div
      ref={elementRef}
      style={componentStyle}
      className="wokwi-component-wrapper"
    />
  );
};