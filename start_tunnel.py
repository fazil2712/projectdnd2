import subprocess
import shutil
import sys

def main():
    print("==================================================")
    print("  D&D 5e AI Dungeon Master - Remote Port Tunnel")
    print("==================================================")
    print("Local Network Access (Same Wi-Fi):")
    print("  👉 http://192.168.1.3:8000\n")

    # Check for available tunnel utilities
    ngrok_path = shutil.which("ngrok")
    cloudflared_path = shutil.which("cloudflared")

    if ngrok_path:
        print(f"Found ngrok at: {ngrok_path}")
        print("Launching ngrok tunnel to port 8000...")
        subprocess.run(["ngrok", "http", "8000"])
    elif cloudflared_path:
        print(f"Found Cloudflare Tunnel at: {cloudflared_path}")
        print("Launching cloudflared quick tunnel to port 8000...")
        subprocess.run(["cloudflared", "tunnel", "--url", "http://localhost:8000"])
    else:
        print("No ngrok or cloudflared found in PATH. Using localtunnel via npx...")
        print("Starting public forwarding with npx localtunnel...")
        subprocess.run(["npx.cmd", "localtunnel", "--port", "8000"])

if __name__ == "__main__":
    main()
