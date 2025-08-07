import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Code, FileText, Download, Upload } from "lucide-react";

const codeExamples = {
  arduino: `// Arduino - Blinking LED Example
#define LED_PIN 13

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Arduino LED Blink Started");
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  Serial.println("LED ON");
  delay(1000);
  
  digitalWrite(LED_PIN, LOW);
  Serial.println("LED OFF");
  delay(1000);
}`,
  
  python: `# CircuitPython - Temperature Sensor
import time
import board
import adafruit_dht11

# Initialize DHT11 sensor
dht = adafruit_dht11.DHT11(board.D2)

print("DHT11 Temperature & Humidity Sensor")

while True:
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        
        print(f"Temp: {temperature}°C, Humidity: {humidity}%")
        
    except RuntimeError as e:
        print(f"Reading error: {e.args[0]}")
    
    time.sleep(2)`,
    
  cpp: `// ESP32 - WiFi IoT Sensor
#include <WiFi.h>
#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

const char* ssid = "your_wifi";
const char* password = "your_password";

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("WiFi connected!");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (!isnan(temperature) && !isnan(humidity)) {
    Serial.printf("Temperature: %.1f°C, Humidity: %.1f%%\\n", 
                  temperature, humidity);
  }
  
  delay(2000);
}`
};

export const CodeEditor = () => {
  const [activeTab, setActiveTab] = useState("arduino");
  const [code, setCode] = useState(codeExamples.arduino);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    setCode(codeExamples[value as keyof typeof codeExamples]);
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <Code className="w-4 h-4" />
          Code Editor
        </h3>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Upload className="w-4 h-4 mr-1" />
            Load
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-1" />
            Save
          </Button>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col min-h-0">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="flex-1 flex flex-col">
          <div className="border-b border-border px-4 py-2">
            <TabsList className="grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="arduino" className="text-xs">
                Arduino/C++
              </TabsTrigger>
              <TabsTrigger value="python" className="text-xs">
                Python
              </TabsTrigger>
              <TabsTrigger value="cpp" className="text-xs">
                ESP32/C++
              </TabsTrigger>
            </TabsList>
          </div>
          
          <div className="flex-1 min-h-0">
            <TabsContent value={activeTab} className="h-full mt-0">
              <div className="h-full p-4">
                <ScrollArea className="h-full">
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="code-editor w-full h-full min-h-[300px] p-4 resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                    spellCheck={false}
                  />
                </ScrollArea>
              </div>
            </TabsContent>
          </div>
        </Tabs>
        
        {/* Status Bar */}
        <div className="border-t border-border px-4 py-2 bg-panel-accent">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-4">
              <span>Lines: {code.split('\n').length}</span>
              <span>Characters: {code.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {activeTab === 'arduino' ? 'Arduino IDE' : activeTab === 'python' ? 'CircuitPython' : 'ESP32-IDF'}
              </Badge>
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <span>Ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};