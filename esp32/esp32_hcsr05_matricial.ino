#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "TU_WIFI_SSID";
const char* password = "TU_WIFI_PASSWORD";
const char* apiUrl = "http://TU_IP_API:5000/api";

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int LED_PINS[] = {23, 19, 4};
const int BTN_PINS[] = {15, 2, 13};

const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[ROWS] = {32, 33, 25, 26};
byte colPins[COLS] = {27, 14, 12, 13};

bool ledStates[] = {false, false, false};
bool lastBtnStates[] = {false, false, false};
unsigned long lastSensorRead = 0;
unsigned long lastApiUpdate = 0;
const unsigned long SENSOR_INTERVAL = 2000;
const unsigned long API_INTERVAL = 3000;

int menuState = 0;
int subMenuState = 0;
String currentUser = "";

void setup() {
  Serial.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  for (int i = 0; i < 3; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    pinMode(BTN_PINS[i], INPUT);
    digitalWrite(LED_PINS[i], LOW);
  }

  for (int i = 0; i < ROWS; i++) {
    pinMode(rowPins[i], OUTPUT);
    digitalWrite(rowPins[i], HIGH);
  }
  for (int i = 0; i < COLS; i++) {
    pinMode(colPins[i], INPUT_PULLUP);
  }

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Sistema HC-SR05");
  lcd.setCursor(0, 1);
  lcd.print("Iniciando...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Conectado");
  delay(2000);

  mostrarMenuPrincipal();
}

void loop() {
  unsigned long currentMillis = millis();

  leerPulsadores();

  char key = leerTecladoMatricial();
  if (key) {
    procesarTecla(key);
  }

  if (currentMillis - lastSensorRead >= SENSOR_INTERVAL) {
    lastSensorRead = currentMillis;
    float distancia = leerDistancia();
    enviarSensorAPI(distancia);
  }

  if (currentMillis - lastApiUpdate >= API_INTERVAL) {
    lastApiUpdate = currentMillis;
    verificarLogin();
  }
}

float leerDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distancia = duration * 0.034 / 2;

  if (distancia > 400 || distancia == 0) {
    distancia = 400;
  }

  return distancia;
}

void leerPulsadores() {
  for (int i = 0; i < 3; i++) {
    bool currentState = digitalRead(BTN_PINS[i]);

    if (currentState == HIGH && lastBtnStates[i] == LOW) {
      ledStates[i] = !ledStates[i];
      digitalWrite(LED_PINS[i], ledStates[i] ? HIGH : LOW);

      actualizarLedAPI(i + 1, ledStates[i]);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("LED ");
      lcd.print(i + 1);
      lcd.print(ledStates[i] ? " ON" : " OFF");
      delay(1000);

      if (menuState == 0) {
        mostrarMenuPrincipal();
      } else {
        mostrarSubMenu();
      }
    }

    lastBtnStates[i] = currentState;
  }
}

char leerTecladoMatricial() {
  for (int row = 0; row < ROWS; row++) {
    digitalWrite(rowPins[row], LOW);

    for (int col = 0; col < COLS; col++) {
      if (digitalRead(colPins[col]) == LOW) {
        delay(50);
        if (digitalRead(colPins[col]) == LOW) {
          digitalWrite(rowPins[row], HIGH);
          while (digitalRead(colPins[col]) == LOW);
          return keys[row][col];
        }
      }
    }

    digitalWrite(rowPins[row], HIGH);
  }

  return 0;
}

void procesarTecla(char key) {
  if (menuState == 0) {
    if (key == '1') {
      menuState = 1;
      subMenuState = 0;
      mostrarSubMenu();
    } else if (key == '2') {
      menuState = 2;
      subMenuState = 0;
      mostrarSubMenu();
    } else if (key == '3') {
      mostrarEstadisticasBD();
    } else if (key == '*') {
      mostrarMenuPrincipal();
    }
  } else if (menuState == 1) {
    if (key == '1') {
      controlarDispositivo(0, true);
    } else if (key == '2') {
      controlarDispositivo(0, false);
    } else if (key == '3') {
      mostrarEstadoDispositivo(0);
    } else if (key == '*') {
      menuState = 0;
      mostrarMenuPrincipal();
    }
  } else if (menuState == 2) {
    if (key == '1') {
      controlarDispositivo(1, true);
    } else if (key == '2') {
      controlarDispositivo(1, false);
    } else if (key == '3') {
      mostrarEstadoDispositivo(1);
    } else if (key == '*') {
      menuState = 0;
      mostrarMenuPrincipal();
    }
  }
}

void mostrarMenuPrincipal() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("1.LED 2.Sensor");
  lcd.setCursor(0, 1);
  lcd.print("3.Est.BD *Menu");
}

void mostrarSubMenu() {
  lcd.clear();
  lcd.setCursor(0, 0);

  if (menuState == 1) {
    lcd.print("1.ON 2.OFF");
    lcd.setCursor(0, 1);
    lcd.print("3.Estado *Volver");
  } else if (menuState == 2) {
    lcd.print("1.ON 2.OFF");
    lcd.setCursor(0, 1);
    lcd.print("3.Estado *Volver");
  }
}

void controlarDispositivo(int deviceIndex, bool estado) {
  if (deviceIndex < 3) {
    ledStates[deviceIndex] = estado;
    digitalWrite(LED_PINS[deviceIndex], estado ? HIGH : LOW);
    actualizarLedAPI(deviceIndex + 1, estado);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("LED ");
    lcd.print(deviceIndex + 1);
    lcd.print(estado ? " ON" : " OFF");

    if (ledStates[deviceIndex] == estado) {
      lcd.setCursor(0, 1);
      lcd.print("Ya esta ");
      lcd.print(estado ? "ON" : "OFF");
    }

    delay(2000);
    mostrarSubMenu();
  }
}

void mostrarEstadoDispositivo(int deviceIndex) {
  lcd.clear();
  lcd.setCursor(0, 0);

  if (deviceIndex < 3) {
    lcd.print("LED ");
    lcd.print(deviceIndex + 1);
    lcd.print(": ");
    lcd.print(ledStates[deviceIndex] ? "ON" : "OFF");
  }

  delay(2000);
  mostrarSubMenu();
}

void mostrarEstadisticasBD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Consultando BD");
  lcd.setCursor(0, 1);
  lcd.print("Espere...");

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(apiUrl) + "/led_hist?limit=5";
    http.begin(url);

    int httpCode = http.GET();

    if (httpCode == 200) {
      String payload = http.getString();
      DynamicJsonDocument doc(2048);
      deserializeJson(doc, payload);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Ultimos 5:");

      int count = 0;
      for (JsonObject item : doc.as<JsonArray>()) {
        if (count >= 5) break;

        lcd.setCursor(0, 1);
        lcd.print("LED");
        lcd.print(item["led_id"].as<int>());
        lcd.print(" ");
        lcd.print(item["estado"].as<bool>() ? "ON" : "OFF");
        lcd.print(" ");
        lcd.print(item["fuente"].as<String>());

        delay(2000);
        count++;
      }
    } else {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Error BD");
    }

    http.end();
  }

  delay(2000);
  menuState = 0;
  mostrarMenuPrincipal();
}

void enviarSensorAPI(float distancia) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(apiUrl) + "/sensores";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(256);
    doc["tipo"] = "HC-SR05";
    doc["valor"] = distancia;

    String jsonString;
    serializeJson(doc, jsonString);

    int httpCode = http.POST(jsonString);
    http.end();
  }
}

void actualizarLedAPI(int ledId, bool estado) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(apiUrl) + "/leds/" + String(ledId);
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(256);
    doc["estado"] = estado;
    doc["usuario"] = currentUser.isEmpty() ? "ESP32" : currentUser;
    doc["fuente"] = "HW";

    String jsonString;
    serializeJson(doc, jsonString);

    int httpCode = http.PUT(jsonString);
    http.end();
  }
}

void verificarLogin() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(apiUrl) + "/eventos?limit=1";
    http.begin(url);

    int httpCode = http.GET();

    if (httpCode == 200) {
      String payload = http.getString();
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, payload);

      if (doc.size() > 0) {
        JsonObject evento = doc[0];
        String accion = evento["accion"].as<String>();

        if (accion == "login") {
          String usuario = evento["usuario"].as<String>();

          if (usuario != currentUser) {
            currentUser = usuario;

            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Login:");
            lcd.setCursor(0, 1);
            lcd.print(usuario);

            delay(3000);
            mostrarMenuPrincipal();
          }
        }
      }
    }

    http.end();
  }
}
