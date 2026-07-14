# honeypot_simulator.py

import socket
import time
import random
from concurrent.futures import ThreadPoolExecutor
import argparse
import logging

# Setup logging
logging.basicConfig(
    filename='attack_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HoneypotSimulator:
    def __init__(self, target_ip="127.0.0.1", intensity="medium"):
        self.target_ip = target_ip
        self.intensity = intensity

        self.target_ports = [21, 22, 23, 25, 80, 443, 3306, 5432]

        self.intensity_settings = {
            "low": {"max_threads": 2, "delay_range": (1, 3)},
            "medium": {"max_threads": 5, "delay_range": (0.5, 1.5)},
            "high": {"max_threads": 10, "delay_range": (0.1, 0.5)}
        }

        self.attack_counter = {}
        self.blocked_ips = set()
        self.BLOCK_THRESHOLD = 10

    def log_attack(self, attack_type, port, details=""):
        msg = f"[{attack_type}] Attack on port {port}. Details: {details}"
        logging.info(msg)
        print(msg)

        if self.target_ip not in self.attack_counter:
            self.attack_counter[self.target_ip] = 0

        self.attack_counter[self.target_ip] += 1

        if self.attack_counter[self.target_ip] >= self.BLOCK_THRESHOLD:
            if self.target_ip not in self.blocked_ips:
                self.blocked_ips.add(self.target_ip)
                block_msg = f"[BLOCKED] IP {self.target_ip} blocked after excessive activity."
                logging.warning(block_msg)
                print(block_msg)

    def is_blocked(self):
        return self.target_ip in self.blocked_ips

    def simulate_port_scan(self):
        if self.is_blocked():
            return
        print(f"\n[*] Starting PORT SCAN on {self.target_ip}")
        for port in self.target_ports:
            self.log_attack("PORT_SCAN", port, "Scanning port")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    sock.connect((self.target_ip, port))
            except:
                pass
            time.sleep(0.1)

    def simulate_brute_force(self, port):
        if self.is_blocked():
            return
        print(f"\n[*] Starting R2L brute force on port {port}")
        users = ["admin", "root"]
        pwds = ["123456", "password", "toor"]
        for u in users:
            for p in pwds:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(2)
                        sock.connect((self.target_ip, port))
                        creds = f"{u}:{p}"
                        sock.send(creds.encode())
                        self.log_attack("R2L_ATTACK", port, f"Attempted {creds}")
                        time.sleep(0.2)
                except:
                    pass

    def simulate_url_scan(self):
        if self.is_blocked():
            return
        print(f"\n[*] Simulating URL Scan on port 80")
        urls = ["/admin", "/phpmyadmin", "/wp-login.php", "/login", "/.env"]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((self.target_ip, 80))
                for path in urls:
                    req = f"GET {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n\r\n"
                    sock.send(req.encode())
                    self.log_attack("URL_SCAN", 80, f"Scanned {path}")
                    time.sleep(0.2)
        except:
            pass

    def simulate_ddos_attack(self):
        if self.is_blocked():
            return
        print(f"\n[*] Simulating DDoS on port 80")
        try:
            for _ in range(50):  # simulate burst
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.2)
                    sock.connect((self.target_ip, 80))
                    sock.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
                    self.log_attack("DDOS", 80, "Rapid request flood")
        except:
            pass

    def simulate_malware_probe(self):
        if self.is_blocked():
            return
        print(f"\n[*] Simulating Malware Probe on port 21")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.target_ip, 21))
                sock.send(b"USER anonymous\r\n")
                sock.recv(1024)
                sock.send(b"STOR evil.exe\r\n")
                self.log_attack("MALWARE_PROBE", 21, "Attempted to upload malware")
        except:
            pass

    def run_continuous_simulation(self, duration=300):
        print(f"\n[*] Running simulation for {duration} seconds at intensity '{self.intensity}'")
        end_time = time.time() + duration
        max_threads = self.intensity_settings[self.intensity]["max_threads"]
        delay_range = self.intensity_settings[self.intensity]["delay_range"]

        attack_pool = [
            ("PORT_SCAN", lambda: self.simulate_port_scan()),
            ("R2L", lambda: self.simulate_brute_force(22)),
            ("URL_SCAN", lambda: self.simulate_url_scan()),
            ("DDOS", lambda: self.simulate_ddos_attack()),
            ("MALWARE_PROBE", lambda: self.simulate_malware_probe())
        ]

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            while time.time() < end_time:
                if self.is_blocked():
                    print(f"[!] IP {self.target_ip} blocked. Stopping simulation.")
                    break
                _, attack_func = random.choice(attack_pool)
                executor.submit(attack_func)
                time.sleep(random.uniform(*delay_range))

def main():
    parser = argparse.ArgumentParser(description="Honeypot Attack Simulator")
    parser.add_argument("--target", default="127.0.0.1", help="Target IP address")
    parser.add_argument("--intensity", choices=["low", "medium", "high"], default="medium", help="Intensity")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    args = parser.parse_args()

    simulator = HoneypotSimulator(args.target, args.intensity)
    try:
        simulator.run_continuous_simulation(args.duration)
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    finally:
        print("[*] Simulation complete.")

if __name__ == "__main__":
    main()
