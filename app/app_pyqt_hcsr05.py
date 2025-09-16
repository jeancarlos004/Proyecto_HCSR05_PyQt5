# app_pyqt_hcsr05.py
# Aplicación PyQt5 para control de LEDs, pulsadores y lectura de sensor HC-SR05 con ESP32
# Se conecta a MySQL (XAMPP) y guarda usuarios, lecturas y eventos

# --- IMPORTANTE ---
# Ajustar SERIAL_PORT y DB_CONFIG antes de correr el sistema
import sys
import serial
import json
import threading
import bcrypt
import mysql.connector
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
                             QLineEdit, QMessageBox, QGridLayout, QMainWindow, QHBoxLayout,
                             QFrame, QTextBrowser, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, QTime

# ---------------- CONFIG ----------------
SERIAL_PORT = "COM3"  # Cambia según tu puerto real
BAUD_RATE = 9600

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # pon tu pass si tienes
    "database": "proyecto_hcsr05"
}

# ---------------- DB FUNCTIONS ----------------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------- LOGIN WINDOW ----------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema HC-SR05 - Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a11cb, stop:1 #2575fc
                );
            }
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                border: none;
                border-radius: 8px;
                padding: 8px;
                background: #f1f1f1;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a11cb, stop:1 #2575fc
                );
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4752a3;
            }
        """)

        layout = QVBoxLayout(self)

        frame = QFrame()
        inner_layout = QVBoxLayout(frame)

        title = QLabel("🔒 Sistema HC-SR05", objectName="title")
        title.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(title)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Ingresa tu usuario")
        inner_layout.addWidget(self.input_user)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Ingresa tu contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        inner_layout.addWidget(self.input_pass)

        self.button_login = QPushButton("Iniciar Sesión")
        self.button_login.clicked.connect(self.check_login)
        inner_layout.addWidget(self.button_login)

        layout.addWidget(frame, alignment=Qt.AlignCenter)

    def check_login(self):
        username = self.input_user.text()
        password = self.input_pass.text()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username=%s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode("utf-8"), result[0].encode("utf-8")):
            self.accept_login(username)
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")

    def accept_login(self, username):
        self.close()
        self.main_window = MainWindow(username)
        self.main_window.show()

# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Panel Principal - Bienvenido {username}")
        self.setFixedSize(950, 700)
        self.username = username

        # --------- STYLES ----------
        self.setStyleSheet("""
            QWidget {
                background: #0f2027;
                color: #eee;
            }
            QFrame {
                background: #1c1f26;
                border-radius: 12px;
                padding: 12px;
            }
            QLabel {
                font-size: 14px;
                color: #ddd;
            }
            QPushButton {
                background: #3a3f47;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #5c5f66;
            }
            QPushButton:checked {
                background: #4CAF50;
                color: white;
            }
            QTextBrowser {
                background: black;
                color: lime;
                font-family: monospace;
                border-radius: 8px;
                padding: 6px;
            }
        """)

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ----- HEADER -----
        header_layout = QHBoxLayout()
        header = QLabel(f"📊 Panel de Control - Usuario: {username}")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header_layout.addWidget(header)

        self.btn_logout = QPushButton("🚪 Cerrar sesión")
        self.btn_logout.setStyleSheet("background: #8e2de2; padding: 8px; font-weight: bold;")
        self.btn_logout.clicked.connect(self.logout)
        header_layout.addWidget(self.btn_logout, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)

        # ----- GRID -----
        grid = QGridLayout()

        # SENSOR
        sensor_box = QFrame()
        s_layout = QVBoxLayout(sensor_box)
        s_title = QLabel("📡 Sensor HC-SR05")
        s_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #bbb;")
        s_layout.addWidget(s_title)
        self.label_sensor = QLabel("0.0 cm")
        self.label_sensor.setStyleSheet("font-size: 28px; font-weight: bold; color: cyan;")
        s_layout.addWidget(self.label_sensor, alignment=Qt.AlignCenter)
        self.label_estado = QLabel("🟢 DETECCIÓN NORMAL")
        s_layout.addWidget(self.label_estado, alignment=Qt.AlignCenter)
        grid.addWidget(sensor_box, 0, 0)

               # LEDs
        led_box = QFrame()
        l_layout = QVBoxLayout(led_box)
        l_title = QLabel("💡 Control de LEDs")
        l_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #bbb;")
        l_layout.addWidget(l_title)

        self.led_buttons = []
        for i, (color_name, color_hex) in enumerate([
            ("Rojo", "#e74c3c"),   # rojo brillante
            ("Verde", "#2ecc71"),  # verde esmeralda
            ("Azul", "#3498db")    # azul claro
        ], start=1):
            btn = QPushButton(f"{color_name} OFF")
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #3a3f47;
                    border-radius: 10px;
                    padding: 8px;
                    font-weight: bold;
                    color: #ccc;
                }}
                QPushButton:checked {{
                    background: {color_hex};
                    color: white;
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.toggle_led(idx))
            self.led_buttons.append(btn)
            l_layout.addWidget(btn)
        grid.addWidget(led_box, 0, 1)


        # Pulsadores
        puls_box = QFrame()
        p_layout = QVBoxLayout(puls_box)
        p_title = QLabel("🔘 Estado de Pulsadores")
        p_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #bbb;")
        p_layout.addWidget(p_title)
        self.puls_labels = []
        for i in range(1, 4):
            lbl = QLabel(f"Pulsador {i}: No Presionado")
            lbl.setStyleSheet("""
                QLabel {
                    background: #2a2d35;
                    border-radius: 8px;
                    padding: 6px;
                    font-weight: bold;
                    color: #ccc;
                }
            """)
            self.puls_labels.append(lbl)
            p_layout.addWidget(lbl)
        grid.addWidget(puls_box, 1, 0)

        # LOG LCD
        log_box = QFrame()
        log_layout = QVBoxLayout(log_box)
        log_title = QLabel("📟 Display LCD")
        log_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #bbb;")
        log_layout.addWidget(log_title)
        self.log_display = QTextBrowser()
        self.log_display.append(">> Sistema iniciado...")
        log_layout.addWidget(self.log_display)
        grid.addWidget(log_box, 1, 1)

        main_layout.addLayout(grid)

        # FOOTER
        self.status = QStatusBar()
        self.status.showMessage("✔ Conectado | Lecturas: 0")
        main_layout.addWidget(self.status)

        # Timer para hora
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Conexión serial en segundo plano
        self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.serial_thread.start()
        except Exception as e:
            QMessageBox.warning(self, "Serial", f"No se pudo abrir puerto serial: {e}")
            self.ser = None

    # ----------- FUNCIONES LEDs ------------
    def toggle_led(self, index):
        state = self.led_buttons[index-1].isChecked()
        self.led_buttons[index-1].setText(f"LED {index} {'ON' if state else 'OFF'}")
        self.save_led_db(index, state)

        if self.ser:
            msg = json.dumps({"led": index, "state": state})
            self.ser.write((msg + "\n").encode())

        self.log_display.append(f">> LED {index} {'encendido' if state else 'apagado'}")

    def save_led_db(self, led_id, state):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE leds SET estado=%s WHERE id=%s", (state, led_id))
        conn.commit()
        conn.close()

    # ----------- LECTURA SERIAL ------------
    def read_serial(self):
        if not self.ser:
            return
        while True:
            try:
                line = self.ser.readline().decode().strip()
                if line:
                    data = json.loads(line)
                    self.process_serial_data(data)
            except Exception:
                continue

    def process_serial_data(self, data):
        if "sensor" in data:
            value = data["sensor"]
            self.label_sensor.setText(f"{value} cm")
            self.save_sensor_db(value)
            self.log_display.append(f">> Distancia medida: {value} cm")

        if "pulsadores" in data:
            states = data["pulsadores"]
            for i, state in enumerate(states):
                self.puls_labels[i].setText(
                    f"Pulsador {i+1}: {'Presionado' if state else 'No Presionado'}"
                )
                self.save_puls_db(i+1, state)

    def save_sensor_db(self, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensores (tipo, valor, fecha) VALUES (%s, %s, %s)",
                       ("HC-SR05", value, datetime.now()))
        conn.commit()
        conn.close()

    def save_puls_db(self, puls_id, state):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pulsadores SET estado=%s WHERE id=%s", (state, puls_id))
        conn.commit()
        conn.close()

    def update_time(self):
        hora = QTime.currentTime().toString("HH:mm:ss")
        self.status.showMessage(f"✔ Conectado | Hora: {hora}")

    def logout(self):
        self.close()
        self.login = LoginWindow()
        self.login.show()

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
