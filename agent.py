from flask import Flask, request, jsonify
import os
import sys
import tempfile
import subprocess
import serial.tools.list_ports
import shutil
import platform
import socket
import logging
from pathlib import Path
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arduino-agent")

app = Flask(__name__)

CORS(app)  # ⚠️ This enables CORS for all routes, all origins (for testing)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_arduino_cli_path():
    system = platform.system().lower()
    binary_name = "arduino-cli.exe" if "windows" in system else "arduino-cli"
    path = resource_path(os.path.join("bin", binary_name))
    return path if os.path.exists(path) else shutil.which("arduino-cli")

ARDUINO_CLI = get_arduino_cli_path()
if not ARDUINO_CLI or not Path(ARDUINO_CLI).exists():
    logger.error("Arduino CLI not found. Make sure it's installed and in PATH.")
    sys.exit(1)

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if any(keyword in port.description.lower() for keyword in ["arduino", "usb", "ttyacm", "usbmodem"]):
            logger.info(f"Arduino detected on port: {port.device}")
            return port.device
    logger.warning("No Arduino device found.")
    return None

def compile_sketch(sketch_dir: str, fqbn: str):
    cmd = [
        ARDUINO_CLI,
        "compile",
        "--fqbn", fqbn,
        sketch_dir,
        "--verbose"
    ]
    try:
        logger.info(f"Compiling sketch: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout + "\n" + result.stderr
    except subprocess.CalledProcessError as e:
        logger.error("Compilation failed.")
        return False, e.stdout + "\n" + e.stderr

def upload_sketch(sketch_dir: str, port: str, fqbn: str):
    cmd = [
        ARDUINO_CLI,
        "upload",
        "-p", port,
        "--fqbn", fqbn,
        sketch_dir,
        "--verbose"
    ]
    try:
        logger.info(f"Uploading sketch: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout + "\n" + result.stderr
    except subprocess.CalledProcessError as e:
        logger.error("Upload failed.")
        return False, e.stdout + "\n" + e.stderr

def upload_to_arduino(code: str, port: str, fqbn: str = "arduino:avr:uno") -> tuple:
    with tempfile.TemporaryDirectory() as temp_dir:
        sketch_name = "sketch"
        sketch_dir = os.path.join(temp_dir, sketch_name)
        os.makedirs(sketch_dir, exist_ok=True)
        
        sketch_file = os.path.join(sketch_dir, f"{sketch_name}.ino")
        with open(sketch_file, "w") as f:
            f.write(code)

        # First compile
        compiled, compile_logs = compile_sketch(sketch_dir, fqbn)
        if not compiled:
            return False, f"Compilation failed:\n{compile_logs}"

        # Then upload
        uploaded, upload_logs = upload_sketch(sketch_dir, port, fqbn)
        if not uploaded:
            return False, f"Upload failed:\n{upload_logs}"

        # Success
        return True, compile_logs + "\n" + upload_logs

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "agent alive"})

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()

    if not data or 'code' not in data:
        return jsonify({"error": "Missing 'code' in request"}), 400

    code = data['code']
    port = find_arduino_port()

    if not port:
        return jsonify({"error": "Arduino device not found"}), 404

    success, output = upload_to_arduino(code, port)
    if success:
        return jsonify({"message": "Upload successful", "logs": output})
    else:
        return jsonify({"error": "Upload failed", "logs": output}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
