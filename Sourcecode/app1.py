import streamlit as st
import socket
import time
import random
import logging
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
import threading
import streamlit as st
import sqlite3  # Import SQLite module
import os
import base64
import subprocess

# Function to convert a file to base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Function to set the background of the Streamlit app
def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-position: center;
        background-size: cover;
        font-family: "Times New Roman", serif;
    }}
    h1, h2, h3, p {{
        font-family: "Times New Roman", serif;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)


# Set the background image for the app
set_background('Background/1.png')
# Logging
logging.basicConfig(filename='attack_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Email config
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'smartidsalerts@gmail.com')

def send_alert_email(subject, body):
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        logging.warning('Email credentials are not configured. Skipping alert email.')
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    except Exception as e:
        logging.error(f"Email send failed: {e}")

class HoneypotSimulator:
    def __init__(self, target_ip="127.0.0.1", intensity="medium"):
        self.target_ip = target_ip
        self.intensity = intensity
        self.target_ports = [21, 22, 23, 25, 80, 443]
        self.intensity_settings = {
            "low": {"max_threads": 2, "delay_range": (1, 3)},
            "medium": {"max_threads": 5, "delay_range": (0.5, 1.5)},
            "high": {"max_threads": 10, "delay_range": (0.1, 0.5)}
        }
        self.attack_counter = {}
        self.blocked_ips = set()
        self.BLOCK_THRESHOLD = 10

    def log_attack(self, attack_type, port, details=""):
        msg = f"[{attack_type}] Attack on port {port}. {details}"
        logging.info(msg)
        if self.target_ip not in self.attack_counter:
            self.attack_counter[self.target_ip] = 0
        self.attack_counter[self.target_ip] += 1
        if self.attack_counter[self.target_ip] >= self.BLOCK_THRESHOLD:
            if self.target_ip not in self.blocked_ips:
                self.blocked_ips.add(self.target_ip)
                send_alert_email("Honeypot Alert", f"BLOCKED IP {self.target_ip} after excessive activity.")

    def is_blocked(self):
        return self.target_ip in self.blocked_ips

    def simulate_port_scan(self):
        for port in self.target_ports:
            self.log_attack("PORT_SCAN", port, "Scan attempt")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    sock.connect((self.target_ip, port))
            except:
                pass
            time.sleep(0.1)

    def simulate_brute_force(self):
        for user in ["admin", "root"]:
            for pwd in ["123456", "password"]:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        sock.connect((self.target_ip, 22))
                        sock.send(f"{user}:{pwd}".encode())
                        self.log_attack("R2L_ATTACK", 22, f"Trying {user}:{pwd}")
                except:
                    pass

    def simulate_url_scan(self):
        for path in ["/admin", "/phpmyadmin"]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    sock.connect((self.target_ip, 80))
                    sock.send(f"GET {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n\r\n".encode())
                    self.log_attack("URL_SCAN", 80, f"Path: {path}")
            except:
                pass

    def simulate_ddos_attack(self):
        for _ in range(20):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.2)
                    sock.connect((self.target_ip, 80))
                    sock.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
                    self.log_attack("DDOS", 80, "Burst request")
            except:
                pass

    def run_simulation(self, duration):
        end_time = time.time() + duration
        attacks = [
            self.simulate_port_scan,
            self.simulate_brute_force,
            self.simulate_url_scan,
            self.simulate_ddos_attack
        ]
        with ThreadPoolExecutor(max_workers=self.intensity_settings[self.intensity]["max_threads"]) as executor:
            while time.time() < end_time:
                if self.is_blocked():
                    break
                executor.submit(random.choice(attacks))
                time.sleep(random.uniform(*self.intensity_settings[self.intensity]["delay_range"]))

# Streamlit UI
st.title("AI Powered Honeypots for Advance Threat Detection and Analysis")
target = st.text_input("Target IP", "127.0.0.1")
intensity = st.selectbox("Attack Intensity", ["low", "medium", "high"])
duration = st.slider("Duration (seconds)", 10, 300, 60)

if st.button("Start Attack Simulation"):
    st.success("Simulation started. Check logs for attack info.")
    sim = HoneypotSimulator(target, intensity)
    threading.Thread(target=sim.run_simulation, args=(duration,), daemon=True).start()
