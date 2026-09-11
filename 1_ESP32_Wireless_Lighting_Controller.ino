#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "home";
const char* password = "1234567890";

WebServer server(80);

const int LED_PIN = 13;
bool lampu = false;

void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kontrol Lampu ESP32</title>
  <style>
    body {
      font-family: Arial;
      text-align: center;
      margin-top: 60px;
    }

    h1 {
      font-size: 30px;
    }

    .status {
      font-size: 22px;
      margin: 20px;
    }

    button {
      padding: 15px 35px;
      margin: 10px;
      font-size: 20px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
    }

    .on {
      background: #22c55e;
      color: white;
    }

    .off {
      background: #ef4444;
      color: white;
    }
  </style>
</head>

<body>

<h1>Kontrol Lampu ESP32</h1>

<div class="status">
  Status: <b>%STATUS%</b>
</div>

<a href="/on">
  <button class="on">NYALAKAN</button>
</a>

<a href="/off">
  <button class="off">MATIKAN</button>
</a>

</body>
</html>
)rawliteral";

  html.replace("%STATUS%", lampu ? "ON" : "OFF");

  server.send(200, "text/html", html);
}

void handleOn() {
  lampu = true;
  digitalWrite(LED_PIN, HIGH);
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleOff() {
  lampu = false;
  digitalWrite(LED_PIN, LOW);
  server.sendHeader("Location", "/");
  server.send(303);
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  WiFi.begin(ssid, password);

  Serial.print("Menghubungkan ke WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi terhubung!");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/on", handleOn);
  server.on("/off", handleOff);

  server.begin();

  Serial.println("Web server aktif!");
}

void loop() {
  server.handleClient();
}