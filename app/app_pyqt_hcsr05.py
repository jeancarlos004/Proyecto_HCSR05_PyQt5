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

# ---------------- EVENT LOG ----------------
def save_event(usuario: str, accion: str, detalles: str = None):
    """Guarda un evento de usuario en la tabla 'eventos'.
    Se asume una tabla con columnas: id (AI), usuario VARCHAR, accion VARCHAR,
    detalles TEXT NULL, fecha DATETIME.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO eventos (usuario, accion, detalles, fecha)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario, accion, detalles, datetime.now())
        )
        conn.commit()
    except Exception:
        # Evitar que un fallo de logging detenga la app
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---------------- ORGANISED HISTORY TABLES ----------------
# Nota: crear tablas en MySQL (ver SQL que te proporcioné en el chat):
#   led_hist(id AI, usuario, led_id, estado, fuente, fecha)
#   pulsador_hist(id AI, usuario, pulsador_id, estado, fuente, fecha)

def save_led_hist(usuario: str, led_id: int, estado: bool, fuente: str):
    """Guarda histórico de cambios de LED (fuente: 'UI' o 'HW')."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO led_hist (usuario, led_id, estado, fuente, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario, led_id, bool(estado), fuente, datetime.now())
        )
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def save_pulsador_hist(usuario: str, pulsador_id: int, estado: bool, fuente: str):
    """Guarda histórico de pulsadores (fuente: 'UI' o 'HW')."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO pulsador_hist (usuario, pulsador_id, estado, fuente, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario, pulsador_id, bool(estado), fuente, datetime.now())
        )
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

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
        # Log de evento: inicio de sesión correcto
        try:
            save_event(username, "login", "Inicio de sesión")
        except Exception:
            pass
        self.main_window = MainWindow(username)
        self.main_window.show()

# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Panel Principal - Bienvenido {username}")
        self.setFixedSize(950, 700)
        self.username = username
        # Evita eco serial cuando el estado del LED viene del hardware
        self.suppress_serial_echo = False
        # Contador de lecturas para el footer
        self.readings_count = 0
        # Estados previos de pulsadores recibidos por hardware para registrar cambios
        self._last_puls_hw = [None, None, None]

        # --------- STYLES ----------
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1f005c, stop:0.5 #5b0060, stop:1 #00b4d8);
                color: #eef2f7;
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
            # Deshabilitamos interacción manual: solo pulsadores/hardware pueden cambiar LEDs
            btn.setEnabled(False)
            btn.setToolTip("Controlado por Pulsadores / Hardware")
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
        self.puls_buttons = []
        for i in range(1, 4):
            row = QHBoxLayout()
            pill = QLabel(f"Pulsador {i}")
            pill.setProperty("pill", True)
            state_lbl = QLabel("Libre")
            state_lbl.setProperty("subpill", True)
            state_lbl.setVisible(False)
            sim_btn = QPushButton("Presionar")
            sim_btn.setToolTip("Simular pulsación del pulsador y conmutar LED")
            if i == 1:
                c1, c2 = "#7b5cff", "#e85d9e"   # morado -> rosa
            elif i == 2:
                c1, c2 = "#00c6ff", "#0072ff"   # cian -> azul
            else:
                c1, c2 = "#3ae374", "#0be881"   # verde claro -> verde
            sim_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {c1}, stop:1 {c2});
                    color: white; border: none; border-radius: 14px; padding: 10px 14px;
                    font-weight: 800;
                }}
                /* Qt no soporta 'filter' en stylesheets; evitamos warnings */
                QPushButton:pressed {{ background: #2e2e3e; }}
            """)
            sim_btn.clicked.connect(lambda checked=False, idx=i: self.press_pulsador(idx))
            row.addWidget(pill)
            row.addStretch()
            row.addWidget(sim_btn)
            container = QFrame()
            container.setLayout(row)
            p_layout.addWidget(container)
            self.puls_labels.append(state_lbl)
            self.puls_buttons.append(sim_btn)
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
        # Actualiza texto/estado del botón sin emitir señales extra
        self.update_led_button(index, state)
        # Persiste en BD
        self.save_led_db(index, state)
        # Log de evento de usuario (sólo si proviene de UI)
        if not self.suppress_serial_echo:
            try:
                save_event(self.username, "led_toggle", f"LED {index} -> {'ON' if state else 'OFF'} (UI)")
            except Exception:
                pass
            # Histórico organizado (LED)
            try:
                save_led_hist(self.username, index, state, "UI")
            except Exception:
                pass
        # Solo enviar al hardware si el cambio se originó en la UI (no desde hardware)
        if self.ser and not self.suppress_serial_echo:
            msg = json.dumps({"led": index, "state": state})
            self.ser.write((msg + "\n").encode())
        # Log
        self.log_display.append(f">> LED {index} {'encendido' if state else 'apagado'}")

    def update_led_button(self, index, state):
        """Actualiza el botón del LED indexado (1..3) sin provocar señales de clic."""
        btn = self.led_buttons[index-1]
        was_blocked = btn.blockSignals(True)
        try:
            btn.setChecked(state)
            btn.setText(f"LED {index} {'ON' if state else 'OFF'}")
        finally:
            btn.blockSignals(was_blocked)

    def apply_led_state_from_hw(self, index, state):
        """Aplica estado de LED proveniente del hardware evitando eco serial y bucles."""
        self.suppress_serial_echo = True
        try:
            self.update_led_button(index, state)
            self.save_led_db(index, state)
            self.log_display.append(f">> LED {index} {'encendido' if state else 'apagado'} (hardware)")
            # Registrar evento de hardware
            try:
                save_event(self.username, "led_toggle_hw", f"LED {index} -> {'ON' if state else 'OFF'} (HW)")
            except Exception:
                pass
            # Histórico organizado (LED)
            try:
                save_led_hist(self.username, index, state, "HW")
            except Exception:
                pass
        finally:
            self.suppress_serial_echo = False

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
            # Actualiza contador y última actualización
            self.readings_count += 1
            self.ultima_act.setText(f"Última actualización: {datetime.now().strftime('%I:%M:%S %p').lower()}")
            # Refrescar footer inmediatamente
            self.update_time()
            # Registrar evento HW para lectura de sensor
            try:
                save_event(self.username, "sensor_read", f"HC-SR05={value} cm (HW)")
            except Exception:
                pass
 
        if "pulsadores" in data:
            states = data["pulsadores"]
            for i, state in enumerate(states):
                self.puls_labels[i].setText(
                    f"Pulsador {i+1}: {'Presionado' if state else 'No Presionado'}"
                )
                self.save_puls_db(i+1, state)
                # Registrar evento de HW sólo cuando cambie el estado respecto al previo
                try:
                    if self._last_puls_hw[i] is None or bool(self._last_puls_hw[i]) != bool(state):
                        estado_txt = "Presionado" if state else "No Presionado"
                        save_event(self.username, "pulsador_change_hw", f"Pulsador {i+1}: {estado_txt} (HW)")
                        self._last_puls_hw[i] = bool(state)
                except Exception:
                    pass
                # Histórico organizado (Pulsador)
                try:
                    save_pulsador_hist(self.username, i+1, bool(state), "HW")
                except Exception:
                    pass
 
        # Refleja estados de LEDs enviados por el ESP32
        if "led" in data:
            try:
                idx = int(data["led"])  # 1..3
                st = bool(data.get("state", data.get("on", False)))
                if 1 <= idx <= len(self.led_buttons):
                    self.apply_led_state_from_hw(idx, st)
            except Exception:
                pass
 
        if "leds" in data:
            try:
                leds_states = list(data["leds"])  # [true,false,true]
                for i, st in enumerate(leds_states, start=1):
                    if i <= len(self.led_buttons):
                        self.apply_led_state_from_hw(i, bool(st))
            except Exception:
                pass

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
        # Log de evento: cierre de sesión
        try:
            save_event(self.username, "logout", "Cierre de sesión")
        except Exception:
            pass
        self.close()
        self.login = LoginWindow()
        self.login.show()

    def press_pulsador(self, index):
        """Simula una pulsación: marca 'Presionado' breve, actualiza BD y conmuta el LED correspondiente."""
        # 1) Mostrar 'Presionado' en la UI
        if 1 <= index <= len(self.puls_labels):
            self.puls_labels[index-1].setText("Presionado")
        # 1.1) Log de evento de usuario (acción en UI)
        try:
            save_event(self.username, "pulsador_press", f"Pulsador {index} (UI)")
        except Exception:
            pass
        # 2) Guardar estado de pulsador en BD (presionado)
        try:
            self.save_puls_db(index, True)
        except Exception:
            pass
        # 3) Conmutar el LED correspondiente (mismo índice 1..3)
        if 1 <= index <= len(self.led_buttons):
            new_state = not self.led_buttons[index-1].isChecked()
            # Fijar estado y ejecutar la lógica estándar (BD + Serial + Log)
            self.led_buttons[index-1].setChecked(new_state)
            self.toggle_led(index)
        # 4) Tras un breve tiempo, volver a 'Libre' y guardar en BD (no presionado)
        QTimer.singleShot(250, lambda: self._release_pulsador(index))

    def _release_pulsador(self, index):
        if 1 <= index <= len(self.puls_labels):
            self.puls_labels[index-1].setText("Libre")
        try:
            self.save_puls_db(index, False)
        except Exception:
            pass
        # Log de evento de usuario (liberación)
        try:
            save_event(self.username, "pulsador_release", f"Pulsador {index} (UI)")
        except Exception:
            pass
        # Histórico organizado (Pulsador UI)
        try:
            save_pulsador_hist(self.username, index, False, "UI")
        except Exception:
            pass

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
