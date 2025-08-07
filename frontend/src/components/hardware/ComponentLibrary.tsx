import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Cpu, Zap, Radio, Gauge, Lightbulb, Speaker } from "lucide-react";

interface Component {
  id: string;
  name: string;
  category: string;
  type?: string;
  icon: React.ReactNode;
  description: string;
  pins?: number;
}

const hardwareComponents: Component[] = [
  // Microcontrollers
  { id: "arduino-uno", name: "Arduino Uno", category: "microcontroller", icon: <Cpu className="w-4 h-4" />, description: "ATmega328P microcontroller board", pins: 14, type: "arduino-uno" },
  
  // Sensors
  { id: "dht22", name: "DHT22", category: "sensor", icon: <Gauge className="w-4 h-4" />, description: "Temperature & humidity sensor", pins: 3, type: "dht22" },
  { id: "potentiometer", name: "Potentiometer", category: "sensor", icon: <Gauge className="w-4 h-4" />, description: "Variable resistor", pins: 3, type: "potentiometer" },
  
  // Output Components
  { id: "led", name: "LED", category: "output", icon: <Lightbulb className="w-4 h-4" />, description: "Light emitting diode", pins: 2, type: "led" },
  { id: "buzzer", name: "Buzzer", category: "output", icon: <Speaker className="w-4 h-4" />, description: "Piezo buzzer", pins: 2, type: "buzzer" },
  { id: "servo", name: "Servo Motor", category: "output", icon: <Zap className="w-4 h-4" />, description: "180° servo motor", pins: 3, type: "servo" },
  
  // Input Components
  { id: "pushbutton", name: "Push Button", category: "input", icon: <Radio className="w-4 h-4" />, description: "Momentary push button", pins: 2, type: "pushbutton" },
  
  // Passive Components
  { id: "resistor", name: "Resistor", category: "passive", icon: <Zap className="w-4 h-4" />, description: "Fixed resistor", pins: 2, type: "resistor" },
  { id: "breadboard", name: "Breadboard", category: "passive", icon: <Cpu className="w-4 h-4" />, description: "Solderless breadboard", pins: 0, type: "breadboard" },
  
  // Displays
  { id: "lcd1602", name: "LCD 16x2", category: "display", icon: <Cpu className="w-4 h-4" />, description: "16x2 character LCD", pins: 16, type: "lcd1602" },
];

const categories = [
  { id: "all", name: "All", color: "bg-muted" },
  { id: "microcontroller", name: "Microcontrollers", color: "bg-primary" },
  { id: "sensor", name: "Sensors", color: "bg-accent" },
  { id: "output", name: "Output", color: "bg-secondary" },
  { id: "input", name: "Input", color: "bg-accent" },
  { id: "passive", name: "Passive", color: "bg-muted" },
  { id: "display", name: "Displays", color: "bg-primary" },
];

export const ComponentLibrary = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const filteredComponents = hardwareComponents.filter(component => {
    const matchesSearch = component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         component.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || component.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleDragStart = (e: React.DragEvent, component: Component) => {
    e.dataTransfer.setData("application/json", JSON.stringify(component));
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">
        <h3 className="font-semibold">Component Library</h3>
      </div>
      
      <div className="flex-1 flex flex-col p-4 gap-4 min-h-0">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Badge
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "outline"}
              className="cursor-pointer text-xs px-2 py-1"
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </Badge>
          ))}
        </div>

        {/* Components List */}
        <ScrollArea className="flex-1">
          <div className="space-y-2">
            {filteredComponents.map((component) => (
              <div
                key={component.id}
                className="component-item"
                draggable
                onDragStart={(e) => handleDragStart(e, component)}
              >
                <div className="flex items-start gap-3">
                  <div className="text-primary mt-1">
                    {component.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm truncate">{component.name}</h4>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {component.description}
                    </p>
                    {component.pins && (
                      <Badge variant="outline" className="mt-2 text-xs">
                        {component.pins} pins
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};