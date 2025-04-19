import sys
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Controller
import keyboard
import subprocess

class AudioMuter:
    def __init__(self):
        self.running = False
        self.muted = True
        self.energy_threshold = 300  # Adjust for sensitivity
        self.silence_timeout = 2.0  # Seconds of silence before muting
        self.last_sound_time = time.time()
        self.keyboard = Controller()
        self.mute_hotkey = 'alt+m'  # Default mute hotkey
        
        # Get list of input devices
        try:
            self.devices = self._get_audio_devices()
        except Exception as e:
            print(f"Error getting audio devices: {e}")
            self.devices = [{"name": "Default", "id": "default"}]
        
        self.input_device = "default"
        self.chunk_size = 1024
        self.audio_thread = None
        
    def _get_audio_devices(self):
        """Get audio input devices using system commands"""
        # For Linux
        if sys.platform.startswith('linux'):
            try:
                result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                devices = []
                for line in lines:
                    if line.startswith('card '):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            card_num = parts[0].strip().split(' ')[1]
                            device_name = parts[1].strip()
                            devices.append({"name": device_name, "id": f"plughw:{card_num},0"})
                return devices
            except Exception as e:
                print(f"Error getting Linux audio devices: {e}")
                
        # Fallback
        return [{"name": "Default", "id": "default"}]
    
    def _record_and_process_audio(self):
        """Record audio and process it for voice detection"""
        if sys.platform.startswith('linux'):
            cmd = ['arecord', '-D', self.input_device, '-f', 'S16_LE', '-c', '1', '-r', '16000', '-t', 'raw']
        elif sys.platform == 'darwin':  # macOS
            cmd = ['rec', '-q', '-t', 'raw', '-r', '16000', '-c', '1', '-b', '16', '-e', 'signed', '-']
        elif sys.platform == 'win32':  # Windows
            cmd = ['ffmpeg', '-f', 'dshow', '-i', 'audio=default', '-ar', '16000', '-ac', '1', '-f', 's16le', '-']
        else:
            print("Unsupported platform")
            return

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            
            while self.running:
                # Read chunk of audio data
                raw_data = process.stdout.read(self.chunk_size * 2)  # 16-bit = 2 bytes per sample
                if not raw_data:
                    break
                    
                # Calculate audio energy
                import struct
                fmt = f"{len(raw_data)//2}h"
                data = struct.unpack(fmt, raw_data)
                energy = np.sqrt(np.mean(np.array(data) ** 2))
                
                # If speaking is detected
                if energy > self.energy_threshold:
                    self.last_sound_time = time.time()
                    if self.muted:
                        self.toggle_mute()
                # If silence for longer than timeout
                elif not self.muted and time.time() - self.last_sound_time > self.silence_timeout:
                    self.toggle_mute()
                    
                # Small sleep to prevent CPU hogging
                time.sleep(0.01)
                
            # Clean up
            process.terminate()
            
        except Exception as e:
            print(f"Error in audio processing: {e}")
            self.running = False
    
    def toggle_mute(self):
        """Toggle mute status and trigger the keyboard shortcut"""
        if self.running:
            keyboard.press_and_release(self.mute_hotkey)
            self.muted = not self.muted
            # Print status update
            status = "Muted" if self.muted else "Unmuted"
            print(f"Auto: {status}")
            
            # Update GUI if it exists
            if hasattr(self, 'status_label') and self.status_label:
                mute_text = "Muted" if self.muted else "Unmuted"
                self.status_label.config(text=f"Current State: {mute_text}")
    
    def start(self):
        """Start monitoring and auto-muting"""
        if self.running:
            return
            
        self.running = True
        self.muted = True  # Assume we start muted
        self.last_sound_time = time.time()
        
        # Start audio monitoring in a separate thread
        self.audio_thread = threading.Thread(target=self._record_and_process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        # Update GUI if it exists
        if hasattr(self, 'run_status_label') and self.run_status_label:
            self.run_status_label.config(text="Status: Running")
            
        print("Auto-Muter started!")
    
    def stop(self):
        """Stop monitoring"""
        if not self.running:
            return
            
        self.running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        
        # Update GUI if it exists
        if hasattr(self, 'run_status_label') and self.run_status_label:
            self.run_status_label.config(text="Status: Stopped")
            
        print("Auto-Muter stopped!")
        
    def create_gui(self):
        """Create Tkinter GUI"""
        root = tk.Tk()
        root.title("Auto Muter")
        root.geometry("500x400")
        
        # Create a frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Auto Muter", font=("Helvetica", 16)).pack(pady=10)
        
        # Device selection
        ttk.Label(main_frame, text="Select Input Device:").pack(anchor="w")
        device_names = [f"{dev['name']} ({dev['id']})" for dev in self.devices]
        self.device_var = tk.StringVar()
        if device_names:
            self.device_var.set(device_names[0])
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var, values=device_names, width=50)
        device_combo.pack(fill=tk.X, pady=5)
        
        # Energy threshold
        ttk.Label(main_frame, text="Energy Threshold:").pack(anchor="w")
        self.threshold_var = tk.IntVar(value=self.energy_threshold)
        threshold_scale = ttk.Scale(main_frame, from_=100, to=2000, variable=self.threshold_var)
        threshold_scale.pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, textvariable=self.threshold_var).pack()
        
        # Silence timeout
        ttk.Label(main_frame, text="Silence Timeout (seconds):").pack(anchor="w")
        self.timeout_var = tk.DoubleVar(value=self.silence_timeout)
        timeout_scale = ttk.Scale(main_frame, from_=0.5, to=10.0, variable=self.timeout_var)
        timeout_scale.pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, textvariable=self.timeout_var).pack()
        
        # Mute hotkey
        ttk.Label(main_frame, text="Mute Hotkey:").pack(anchor="w")
        self.hotkey_var = tk.StringVar(value=self.mute_hotkey)
        ttk.Entry(main_frame, textvariable=self.hotkey_var).pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Start", command=self.start_from_gui).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Mute", command=self.toggle_mute).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Status labels
        self.run_status_label = ttk.Label(main_frame, text="Status: Stopped")
        self.run_status_label.pack(pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Current State: Muted")
        self.status_label.pack(pady=5)
        
        # Setup update loop for GUI
        def update_gui():
            if self.running:
                mute_text = "Muted" if self.muted else "Unmuted"
                self.status_label.config(text=f"Current State: {mute_text}")
            root.after(100, update_gui)
            
        update_gui()
        
        # When closing window
        def on_close():
            self.stop()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_close)
        
        # Start the GUI main loop
        root.mainloop()
    
    def start_from_gui(self):
        """Start from GUI with updated settings"""
        # Update settings
        device_str = self.device_var.get()
        if device_str:
            try:
                # Extract device ID from string like "Device Name (device_id)"
                device_id = device_str.split('(')[-1].strip(')')
                self.input_device = device_id
            except:
                # Fallback if format is different
                self.input_device = "default"
                
        self.energy_threshold = self.threshold_var.get()
        self.silence_timeout = self.timeout_var.get()
        self.mute_hotkey = self.hotkey_var.get()
        
        # Start service
        self.start()
        
def main():
    app = AudioMuter()
    app.create_gui()

if __name__ == '__main__':
    main()