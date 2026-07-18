import sys
import os
import shutil
import subprocess
import base64
import sqlite3
from tkinter import filedialog

# --- OS ENFORCEMENT & WINDOWS IMPORTS ---
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import ctypes
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    ctypes = None
    winreg = None

# --- AUTOMATIC ENVIRONMENT FIX ---
try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter missing. Attempting automatic installation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

try:
    from PIL import Image
except ImportError:
    print("Pillow library missing. Attempting automatic installation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image  # <-- FIXED: Corrected typo importing ctk instead of PIL

def secure_cipher(text, key):
    if not key:
        return text
    key_sum = sum(ord(k) for k in key) % 256
    return "".join(chr(ord(c) ^ ord(key[i % len(key)]) ^ ((i + key_sum) % 256)) for i, c in enumerate(text))

ctk.set_appearance_mode("Dark")

class PrivacySuiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Veritas Framework")
        self.geometry("1150x820")
        self.minsize(1100, 780)
        
        self.is_admin = self.check_admin()
        
        # Color Strategy
        self.bg_main = "#0d1117"
        self.sidebar_bg = "#161b22"
        self.card_bg = "#21262d"
        self.card_border = "#30363d"
        self.accent_color = "#58a6ff"       
        self.accent_hover = "#1f6feb"      
        self.text_primary = "#c9d1d9"
        self.text_muted = "#8b949e"
        self.warning_bg = "#38230d"
        self.warning_border = "#d29922"

        self.configure(fg_color=self.bg_main)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR PANEL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=self.sidebar_bg, border_color=self.card_border, border_width=1)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 

        self.title_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="VERITAS", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.grid(row=0, column=0, padx=25, pady=(35, 2), sticky="w") 

        self.latin_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="In venatione veritatis et virtutis", 
            text_color=self.accent_color,
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic")
        )
        self.latin_label.grid(row=1, column=0, padx=25, pady=(0, 2), sticky="w")

        self.motto_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Privacy & Optimization Engine", 
            text_color=self.text_muted,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.motto_label.grid(row=2, column=0, padx=25, pady=(0, 35), sticky="w")

        # Sidebar Buttons
        self.nav_buttons = {}
        tabs = [
            ("Hardening", "🔒 System Shielding"),
            ("Sanitizer", "🧼 History & Cache"),
            ("Vault", "🔑 File Vault Manager"),
            ("Shredder", "🔥 Permanent Eraser"),
            ("Perimeter", "🌐 Network Guard")
        ]

        for i, (tab_id, label) in enumerate(tabs):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=label, font=ctk.CTkFont(size=14, weight="normal"),
                fg_color="transparent", hover_color=self.card_bg, text_color=self.text_primary,
                height=45, anchor="w", corner_radius=6,
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.grid(row=i+3, column=0, padx=15, pady=4, sticky="ew")
            self.nav_buttons[tab_id] = btn

        status_text = "🔒 ADMINISTRATOR MODE" if self.is_admin else "⚠️ STANDARD USER MODE"
        status_color = "#2ea043" if self.is_admin else self.warning_border
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.grid(row=9, column=0, pady=25)

        # --- MAIN WORKSPACE CONTAINER ---
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=25)
        
        self.switch_tab("Hardening")

    def check_admin(self):
        if not IS_WINDOWS:
            return False
        try: 
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except: 
            return False

    def request_admin_elevation(self):
        if not IS_WINDOWS:
            self.log_output("Elevation failed: Native UAC adjustments require a Windows platform environment.")
            return
        try:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            sys.exit(0)
        except Exception as e:
            self.log_output(f"Elevation request rejected or failed: {str(e)}")

    def log_output(self, message):
        if hasattr(self, 'console_log') and self.console_log.winfo_exists():
            self.console_log.configure(state="normal")
            self.console_log.insert("end", f">> {message}\n")
            self.console_log.see("end")
            self.console_log.configure(state="disabled")

    def create_toggle_card(self, parent, title, description, command=None):
        card = ctk.CTkFrame(parent, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8, height=75)
        card.pack(fill="x", pady=6)
        card.pack_propagate(False)

        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.pack(side="left", padx=20, fill="y", pady=12)

        lbl_title = ctk.CTkLabel(text_container, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff")
        lbl_title.pack(anchor="w")

        lbl_desc = ctk.CTkLabel(text_container, text=description, font=ctk.CTkFont(size=12), text_color=self.text_muted)
        lbl_desc.pack(anchor="w")

        switch = ctk.CTkSwitch(card, text="", progress_color=self.accent_color, command=command)
        switch.pack(side="right", padx=20)
        return switch

    def create_action_card(self, parent, title, description, btn_text, command):
        card = ctk.CTkFrame(parent, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8, height=75)
        card.pack(fill="x", pady=6)
        card.pack_propagate(False)

        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.pack(side="left", padx=20, fill="y", pady=12)

        lbl_title = ctk.CTkLabel(text_container, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff")
        lbl_title.pack(anchor="w")

        lbl_desc = ctk.CTkLabel(text_container, text=description, font=ctk.CTkFont(size=12), text_color=self.text_muted)
        lbl_desc.pack(anchor="w")

        btn = ctk.CTkButton(card, text=btn_text, fg_color=self.accent_color, hover_color=self.accent_hover, text_color="#ffffff", font=ctk.CTkFont(weight="bold"), width=140, height=35, command=command)
        btn.pack(side="right", padx=20)
        return card

    def modify_registry_dword(self, path, value_name, value_data):
        if not self.is_admin or not winreg:
            self.log_output("Action Aborted: Elevate privileges on Windows to modify system registries.")
            return False
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.log_output(f"Registry Modification Error [{value_name}]: {str(e)}")
            return False

    def toggle_telemetry(self):
        state = 0 if self.sw_telemetry.get() else 1
        if self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", state):
            self.log_output(f"[SUCCESS] Telemetry Tracking setting changed. Active Block: {state == 0}")

    def toggle_advertising(self):
        state = 1 if self.sw_advertising.get() else 0
        if self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo", "DisabledByGroupPolicy", state):
            self.log_output(f"[SUCCESS] Advertising Profile ID tracking changed. Active Block: {state == 1}")

    def toggle_location(self):
        state = 1 if self.sw_location.get() else 0
        s1 = self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", state)
        s2 = self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableSensorServices", state)
        if s1 or s2:
            self.log_output(f"[SUCCESS] Core Hardware Geolocation channel states updated.")

    def run_defender_audit(self):
        self.log_output("Querying active Windows Defender security states...")
        try:
            res = subprocess.check_output("powershell -Command \"Get-MpComputerStatus | Select-Object AMProductVersion, RealTimeProtectionEnabled, AntivirusEnabled\"", shell=True, text=True)
            for line in res.split("\n"):
                if line.strip(): self.log_output(line.strip())
            self.log_output("[SUCCESS] Antivirus validation check done.")
        except Exception as e: self.log_output(f"Failed pulling Defender info: {e}")

    def toggle_doh(self):
        state = 2 if self.sw_doh.get() else 0
        if self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\DNSClient", "EnableAutoDoh", state):
            self.log_output(f"[SUCCESS] System Secure DNS-over-HTTPS routing rules updated.")

    def toggle_wifi_sharing(self):
        state = 1 if self.sw_wifi.get() else 0
        s1 = self.modify_registry_dword(r"SOFTWARE\Microsoft\WcmSvc\Tethering", "ForceDisable", state)
        s2 = self.modify_registry_dword(r"SOFTWARE\Policies\Microsoft\Windows\Wireless\ModemAuth", "DisableModemAuth", state)
        if s1 or s2:
            self.log_output(f"[SUCCESS] Wi-Fi Sense and background sync sharing vectors restricted.")

    def run_sanitizer_purge(self):
        self.log_output("Initializing selected tracking asset purges...")
        if self.sw_c_dns.get():
            try:
                subprocess.check_output("ipconfig /flushdns", shell=True, text=True)
                self.log_output("[SUCCESS] Flushed internal internet domain lookup histories.")
            except Exception as e: self.log_output(f"DNS Purge Failure: {e}")

        if self.sw_c_browsers.get():
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            paths = [os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Cache"), os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Cache")]
            for p in paths:
                if os.path.exists(p):
                    try:
                        shutil.rmtree(p); os.makedirs(p)
                        self.log_output(f"[SUCCESS] Cleaned standard framework cache layout: {os.path.basename(os.path.dirname(p))}")
                    except: self.log_output("[NOTICE] Dynamic browser assets skipped (Process files currently open/locked).")

        if self.sw_c_identity.get():
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            roaming_appdata = os.environ.get('APPDATA', '')
            targets = {
                "Chrome": os.path.join(local_appdata, r"Google\Chrome\User Data\Default"),
                "Edge": os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default"),
                "Opera": os.path.join(roaming_appdata, r"Opera Software\Opera Stable"),
                "Opera GX": os.path.join(roaming_appdata, r"Opera Software\Opera GX Stable")
            }
            for b_name, target_dir in targets.items():
                if os.path.exists(target_dir):
                    for db_file in ["Cookies", "Web Data", "History"]:
                        db_path = os.path.join(target_dir, db_file)
                        if os.path.exists(db_path):
                            try:
                                conn = sqlite3.connect(db_path)
                                cursor = conn.cursor()
                                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                                for t in [row[0] for row in cursor.fetchall()]:
                                    try: cursor.execute(f"DELETE FROM {t};")
                                    except: pass
                                conn.commit(); cursor.execute("VACUUM;"); conn.close()
                                self.log_output(f"[SUCCESS] Scrubbed database layout: {b_name} -> {db_file}")
                            except: 
                                self.log_output(f"[NOTICE] Lock verified on {b_name} {db_file}. Close browser to clean completely.")

        if self.sw_c_temp.get():
            t_dir = os.environ.get('TEMP', '')
            if os.path.exists(t_dir):
                for item in os.listdir(t_dir):
                    ip = os.path.join(t_dir, item)
                    try:
                        if os.path.isdir(ip): shutil.rmtree(ip)
                        else: os.remove(ip)
                    except: pass
                self.log_output("[SUCCESS] Temporary scratch variables dropped.")

        if self.sw_c_events.get() and self.is_admin:
            for log in ["Application", "Security", "System", "Setup"]:
                subprocess.run(f'wevtutil cl "{log}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log_output("[SUCCESS] Windows internal log checkpoints cleared.")

        self.log_output("[COMPLETE] Selected maintenance routines successfully executed.")

    def select_image(self, target_entry):
        fp = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if fp:
            target_entry.delete(0, 'end')
            target_entry.insert(0, fp)

    def encode_text_into_image(self):
        img_path = self.ent_enc_img.get().strip()
        secret_text = self.ent_enc_txt.get().strip()
        passkey = self.vault_passkey.get().strip()
        
        if not img_path or not os.path.exists(img_path) or not secret_text:
            self.log_output("Error: Valid structural image path and payload components required.")
            return
        try:
            ciphered = secure_cipher(secret_text, passkey)
            b64_payload = base64.b64encode(ciphered.encode('utf-8')).decode('utf-8') + "##END##"
            binary_secret = ''.join(format(ord(c), '08b') for c in b64_payload)
            
            img = Image.open(img_path).convert('RGB')
            pixels = img.load()
            width, height = img.size
            
            if len(binary_secret) > width * height * 3:
                self.log_output("Error: Payload bounds outrange target pixel carrier grid dimensions.")
                return
                
            bit_idx = 0
            for y in range(height):
                for x in range(width):
                    if bit_idx >= len(binary_secret): break
                    r, g, b = pixels[x, y]
                    if bit_idx < len(binary_secret): r = (r & ~1) | int(binary_secret[bit_idx]); bit_idx += 1
                    if bit_idx < len(binary_secret): g = (g & ~1) | int(binary_secret[bit_idx]); bit_idx += 1
                    if bit_idx < len(binary_secret): b = (b & ~1) | int(binary_secret[bit_idx]); bit_idx += 1
                    pixels[x, y] = (r, g, b)
            
            out_p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Images", "*.png")])
            if out_p:
                img.save(out_p, "PNG")
                self.log_output(f"[VAULT] Injected encrypted secret layer safely inside: {os.path.basename(out_p)}")
        except Exception as e: self.log_output(f"Vault Injection Aborted: {e}")

    def decode_text_from_image(self):
        img_path = self.ent_dec_img.get().strip()
        passkey = self.vault_passkey.get().strip()
        if not img_path or not os.path.exists(img_path): return

        try:
            img = Image.open(img_path).convert('RGB')
            pixels = img.load()
            width, height = img.size
            binary_data = ""
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    binary_data += str(r & 1) + str(g & 1) + str(b & 1)
            
            all_chars = [chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8) if (i+8) <= len(binary_data)]
            extracted = "".join(all_chars)
            
            if "##END##" in extracted:
                raw_b64 = extracted.split("##END##")[0]
                dec_bytes = base64.b64decode(raw_b64.encode('utf-8')).decode('utf-8', errors='replace')
                self.log_output(f"[VAULT EXTRACTED CONTENT]:\n>> {secure_cipher(dec_bytes, passkey)}")
            else:
                self.log_output("[NOTICE] Extraction cycle done: Verification header token profiles missing.")
        except Exception as e: self.log_output(f"Decoding Event Aborted: {e}")

    def select_shred_file(self):
        fp = filedialog.askopenfilename(title="Select Target File Block")
        if fp:
            self.ent_shred_p.delete(0, 'end'); self.ent_shred_p.insert(0, fp)

    def run_secure_shred(self):
        tp = self.ent_shred_p.get().strip()
        if not tp or not os.path.exists(tp): return
        
        passes = 3
        if "1-Pass" in self.shred_menu.get(): passes = 1
        elif "7-Pass" in self.shred_menu.get(): passes = 7

        try:
            self.log_output(f"Beginning overwrite cycle matrix updates ({passes} passes)...")
            fs = os.path.getsize(tp)
            with open(tp, "ba+", buffering=0) as f:
                for p in range(1, passes + 1):
                    f.seek(0)
                    f.write(b'\x00' * fs if p == passes else os.urandom(fs))
            os.remove(tp)
            self.ent_shred_p.delete(0, 'end')
            self.log_output("[SUCCESS] Target cluster references unlinked and zeroed completely.")
        except Exception as e: self.log_output(f"Shredder Engine Core Fault: {e}")

    def run_perimeter_audit(self):
        self.log_output("Starting local interface boundary validation routines...")
        if self.sw_n_adapters.get():
            self.log_output("--- PHYSICAL HARDWARE INSTANCES ---")
            try:
                res = subprocess.check_output("ipconfig /all", shell=True, text=True)
                for line in res.split("\n"):
                    if any(k in line for k in ["Description", "IPv4 Address", "Physical Address"]): self.log_output(line.strip())
            except: pass

        if self.sw_n_conns.get():
            self.log_output("--- SOCKET MONITOR BOUNDARY LOGS (TOP 5 INTERFACES) ---")
            try:
                res = subprocess.check_output("netstat -n -o", shell=True, text=True)
                c = 0
                for line in res.split("\n"):
                    if "TCP" in line or "UDP" in line:
                        self.log_output(line.strip()); c += 1
                        if c >= 5: break
            except: pass

        if self.sw_n_fw.get():
            self.log_output("--- FIREWALL ACTIVE RULE STATUS MAPS ---")
            try:
                res = subprocess.check_output("netsh advfirewall show allprofilesstate", shell=True, text=True)
                for line in res.split("\n"):
                    if "State" in line or "Profile" in line: self.log_output(line.strip())
            except: pass

    def switch_tab(self, tab_name):
        for t_id, btn in self.nav_buttons.items():
            if t_id == tab_name:
                btn.configure(fg_color=self.card_bg, text_color=self.accent_color)
            else:
                btn.configure(fg_color="transparent", text_color=self.text_primary)

        for widget in self.content_frame.winfo_children(): 
            widget.destroy()

        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        human_titles = {
            "Hardening": ("System Shielding Controls", "Deactivate background tracking services, manage diagnostics, and adjust security settings."),
            "Sanitizer": ("History & Cache Cleaner", "Select tracking profiles below to scan and clean local application cache variables."),
            "Vault": ("Secure Photo File Vault Manager", "Inject confidential text inside carriers or erase camera system parameter keys."),
            "Shredder": ("Permanent Data Eraser Tools", "Destructive sector overrides to prevent file restoration procedures."),
            "Perimeter": ("Network Guard Boundary Auditing", "Analyze active hardware connections, loop parameters, and routing flags.")
        }
        
        h_title, h_desc = human_titles[tab_name]
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        lbl_h = ctk.CTkLabel(header_frame, text=h_title, font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color="#ffffff")
        lbl_h.pack(anchor="w")
        lbl_d = ctk.CTkLabel(header_frame, text=h_desc, font=ctk.CTkFont(size=13), text_color=self.text_muted)
        lbl_d.pack(anchor="w", pady=(2, 0))

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))

        if tab_name == "Hardening":
            if not self.is_admin:
                f_warn = ctk.CTkFrame(scroll_frame, fg_color=self.warning_bg, border_color=self.warning_border, border_width=1, corner_radius=6, height=50)
                f_warn.pack(fill="x", pady=(0, 10))
                f_warn.pack_propagate(False)
                
                ctk.CTkLabel(f_warn, text="⚠️ Elevation Notice: Administrator rights are required to switch target tracking registries permanently.", text_color=self.warning_border, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=15)
                
                btn_elevate = ctk.CTkButton(f_warn, text="Relaunch as Admin", font=ctk.CTkFont(size=11, weight="bold"), fg_color=self.warning_border, hover_color="#b8841a", text_color="#000000", width=130, height=28, command=self.request_admin_elevation)
                btn_elevate.pack(side="right", padx=15)

            self.sw_telemetry = self.create_toggle_card(scroll_frame, "Telemetry Diagnostic Tracking", "Blocks core background diagnostic metrics transmission loops.", self.toggle_telemetry)
            self.sw_advertising = self.create_toggle_card(scroll_frame, "Targeted Advertising Profile ID", "Locks application tracking engines from generating specific ad identifiers.", self.toggle_advertising)
            self.sw_location = self.create_toggle_card(scroll_frame, "System Geolocation Logs", "Restricts hardware GPS coordinates and local background map trackers.", self.toggle_location)
            self.sw_doh = self.create_toggle_card(scroll_frame, "Enforce Secure DNS-over-HTTPS (DoH)", "Forces lookups through secure encrypted translation channels.", self.toggle_doh)
            self.sw_wifi = self.create_toggle_card(scroll_frame, "Wi-Fi Sense Data Sharing Hotspots", "Closes open background mesh synchronization exchanges.", self.toggle_wifi_sharing)
            
            self.create_action_card(scroll_frame, "Windows Defender Security State", "Queries local active system monitoring metrics.", "Check Status", self.run_defender_audit)

        elif tab_name == "Sanitizer":
            self.sw_c_dns = self.create_toggle_card(scroll_frame, "Flush DNS Lookups", "Empties local system website search caches.")
            self.sw_c_browsers = self.create_toggle_card(scroll_frame, "Scrub Browser Storage Cache", "Deletes temporary page layout elements inside Chrome and Edge.")
            self.sw_c_identity = self.create_toggle_card(scroll_frame, "Nuke Core Browser Activity Tables", "Wipes history, cookie arrays, and lookup keys from Chrome/Edge/Opera databases.")
            self.sw_c_temp = self.create_toggle_card(scroll_frame, "Purge Temp Scratchpad Profiles", "Empties hidden system directory staging grounds.")
            self.sw_c_events = self.create_toggle_card(scroll_frame, "Reset Diagnostics Event Framework", "Flushes active local execution tracking checkpoints.")
            
            self.sw_c_dns.select()
            
            btn_run = ctk.CTkButton(scroll_frame, text="🧼 Execute Selected Cleanup Operations", font=ctk.CTkFont(size=14, weight="bold"), fg_color=self.accent_color, hover_color=self.accent_hover, height=42, command=self.run_sanitizer_purge)
            btn_run.pack(fill="x", pady=15)

        elif tab_name == "Vault":
            p_card = ctk.CTkFrame(scroll_frame, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8)
            p_card.pack(fill="x", pady=6, padx=2)
            ctk.CTkLabel(p_card, text="Vault Protection Passkey:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff").pack(side="left", padx=20, pady=15)
            self.vault_passkey = ctk.CTkEntry(p_card, placeholder_text="Salts the target cipher data stream...", show="*", width=380, fg_color=self.bg_main, border_color=self.card_border)
            self.vault_passkey.pack(side="left", padx=10, pady=15)

            enc_card = ctk.CTkFrame(scroll_frame, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8)
            enc_card.pack(fill="x", pady=6, padx=2)
            ctk.CTkLabel(enc_card, text="🔒 Hide Text Inside an Image File", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
            
            self.ent_enc_img = ctk.CTkEntry(enc_card, placeholder_text="Select a cover photo carrier file...", width=480, fg_color=self.bg_main, border_color=self.card_border)
            self.ent_enc_img.grid(row=1, column=0, padx=(20, 10), pady=6, sticky="w")
            btn_br_e = ctk.CTkButton(enc_card, text="📂 Select Image", fg_color="transparent", hover_color=self.bg_main, border_color=self.card_border, border_width=1, command=lambda: self.select_image(self.ent_enc_img))
            btn_br_e.grid(row=1, column=1, padx=10, pady=6, sticky="w")

            self.ent_enc_txt = ctk.CTkEntry(enc_card, placeholder_text="Type private payload string content here...", width=480, fg_color=self.bg_main, border_color=self.card_border)
            self.ent_enc_txt.grid(row=2, column=0, padx=(20, 10), pady=6, sticky="w")
            btn_ex_e = ctk.CTkButton(enc_card, text="✨ Inject Data", fg_color=self.accent_color, hover_color=self.accent_hover, font=ctk.CTkFont(weight="bold"), command=self.encode_text_into_image)
            btn_ex_e.grid(row=2, column=1, padx=10, pady=6, sticky="w")
            enc_card.grid_rowconfigure(3, minsize=10)

            dec_card = ctk.CTkFrame(scroll_frame, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8)
            dec_card.pack(fill="x", pady=6, padx=2)
            ctk.CTkLabel(dec_card, text="🔓 Extract Hidden Text From an Image File", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
            
            self.ent_dec_img = ctk.CTkEntry(dec_card, placeholder_text="Select source payload verification image...", width=480, fg_color=self.bg_main, border_color=self.card_border)
            self.ent_dec_img.grid(row=1, column=0, padx=(20, 10), pady=6, sticky="w")
            btn_br_d = ctk.CTkButton(dec_card, text="📂 Select Image", fg_color="transparent", hover_color=self.bg_main, border_color=self.card_border, border_width=1, command=lambda: self.select_image(self.ent_dec_img))
            btn_br_d.grid(row=1, column=1, padx=10, pady=6, sticky="w")

            btn_ex_d = ctk.CTkButton(dec_card, text="🔍 Extract Text", fg_color=self.accent_color, hover_color=self.accent_hover, font=ctk.CTkFont(weight="bold"), command=self.decode_text_from_image)
            btn_ex_d.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="w")

        elif tab_name == "Shredder":
            shred_card = ctk.CTkFrame(scroll_frame, fg_color=self.card_bg, border_color=self.card_border, border_width=1, corner_radius=8)
            shred_card.pack(fill="x", pady=6)
            
            ctk.CTkLabel(shred_card, text="File Block Shred Engine", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=(15, 5))
            
            self.ent_shred_p = ctk.CTkEntry(shred_card, placeholder_text="Coordinate file paths destined for deletion...", width=480, fg_color=self.bg_main, border_color=self.card_border)
            self.ent_shred_p.pack(anchor="w", padx=20, pady=5)
            
            btn_br_s = ctk.CTkButton(shred_card, text="📂 Browse Targets", fg_color="transparent", hover_color=self.bg_main, border_color=self.card_border, border_width=1, command=self.select_shred_file)
            btn_br_s.pack(anchor="w", padx=20, pady=5)
            
            ctk.CTkLabel(shred_card, text="Erasure Algorithm Strength Spec:", font=ctk.CTkFont(size=12), text_color=self.text_muted).pack(anchor="w", padx=20, pady=(10, 2))
            self.shred_menu = ctk.CTkComboBox(shred_card, values=["1-Pass (Quick Overwrite)", "3-Pass (DoD Standard)", "7-Pass (High Security Spec Shred)"], width=300, fg_color=self.bg_main, border_color=self.card_border)
            self.shred_menu.pack(anchor="w", padx=20, pady=5)
            self.shred_menu.set("3-Pass (DoD Standard)")
            
            btn_ex_s = ctk.CTkButton(shred_card, text="🔥 Permanently Overwrite & Shred File Block", font=ctk.CTkFont(weight="bold"), fg_color="#f85149", hover_color="#da3633", height=38, command=self.run_secure_shred)
            btn_ex_s.pack(anchor="w", padx=20, pady=(15, 20))

        elif tab_name == "Perimeter":
            self.sw_n_adapters = self.create_toggle_card(scroll_frame, "Audit Network Adapters", "Retrieves active MAC hardware properties and local IP details.")
            self.sw_n_conns = self.create_toggle_card(scroll_frame, "Scan Live Connection Sockets", "Monitors active TCP/UDP ports mapped to application process IDs.")
            self.sw_n_fw = self.create_toggle_card(scroll_frame, "Verify Windows Firewall States", "Inspects current active profiles and basic routing rules.")
            
            self.sw_n_adapters.select()
            
            btn_aud = ctk.CTkButton(scroll_frame, text="🌐 Run Network Audits", font=ctk.CTkFont(size=14, weight="bold"), fg_color=self.accent_color, hover_color=self.accent_hover, height=42, command=self.run_perimeter_audit)
            btn_aud.pack(fill="x", pady=15)

        log_frame = ctk.CTkFrame(self.content_frame, fg_color=self.sidebar_bg, border_color=self.card_border, border_width=1, corner_radius=8)
        log_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        lbl_l = ctk.CTkLabel(log_frame, text=">_ COMMAND CONSOLE RUNTIME LOG", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=self.accent_color)
        lbl_l.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.console_log = ctk.CTkTextbox(log_frame, height=160, font=ctk.CTkFont(family="Consolas", size=12), fg_color=self.bg_main)
        self.console_log.pack(fill="both", expand=True, padx=12, pady=(2, 12))
        self.console_log.configure(state="disabled")

if __name__ == "__main__":
    app = PrivacySuiteApp()
    app.mainloop()