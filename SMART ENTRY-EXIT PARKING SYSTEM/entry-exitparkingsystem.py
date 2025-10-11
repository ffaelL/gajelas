from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# database
def init_db():
    conn = sqlite3.connect('parking_system.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS parking_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT NOT NULL,
                    status TEXT NOT NULL,
                    waktu_masuk TEXT,
                    waktu_keluar TEXT,
                    slot TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS slot_parkir (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_name TEXT UNIQUE,
                    available INTEGER DEFAULT 1
                )''')

    for i in range(1, 13):
        try:
            c.execute("INSERT INTO slot_parkir (slot_name, available) VALUES (?, 1)", (f"A:{i}",))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

init_db()

# main page
@app.route('/')
def home():
    conn = sqlite3.connect('parking_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM parking_log WHERE status='IN'")
    aktif = c.fetchall()

    # Urutkan slot berdasarkan angka, bukan string
    c.execute("""
        SELECT slot_name, available 
        FROM slot_parkir 
        ORDER BY CAST(SUBSTR(slot_name, INSTR(slot_name, ':')+1) AS INTEGER)
    """)
    slots = c.fetchall()
    conn.close()

    return render_template_string('''
    <html>
    <head>
        <title>Smart Parking System Kampus</title>
        <style>
            body { font-family: 'Poppins', sans-serif; background: #eef3f8; text-align: center; margin: 0; padding: 0; }
            header { background: linear-gradient(90deg, #007bff, #00b4d8); color: white; padding: 20px 0; font-size: 24px; letter-spacing: 1px; }
            h2 { color: #007bff; }
            .form-container { display: flex; justify-content: center; gap: 20px; margin-top: 20px; flex-wrap: wrap; }
            form { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 0 15px rgba(0,0,0,0.1); width: 280px; }
            input { padding: 8px; width: 80%; margin-bottom: 10px; border-radius: 8px; border: 1px solid #aaa; }
            button { background: #007bff; color: white; border: none; border-radius: 8px; padding: 8px 20px; cursor: pointer; }
            button:hover { background: #0056b3; }
            table { margin: 30px auto; border-collapse: collapse; width: 80%; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
            th { background-color: #007bff; color: white; }
            .slots-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 30px; }
            .slot { width: 70px; height: 70px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
            .kosong { background: #28a745; }
            .isi { background: #dc3545; }
            footer { margin-top: 40px; color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <header>🚗 Smart Parking System Kampus</header>

        <div class="form-container">
            <form action="/scan_in" method="post">
                <h3>Masuk Parkir</h3>
                <input type="text" name="plate" placeholder="Plat Nomor" required><br>
                <button type="submit">Scan Masuk</button>
            </form>

            <form action="/scan_out" method="post">
                <h3>Keluar Parkir</h3>
                <input type="text" name="plate" placeholder="Plat Nomor" required><br>
                <button type="submit" style="background:#dc3545;">Scan Keluar</button>
            </form>
        </div>

        <h3>🚘 Kendaraan Sedang Parkir</h3>
        <table>
            <tr><th>Plat Nomor</th><th>Waktu Masuk</th><th>Slot</th></tr>
            {% for row in aktif %}
                <tr>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[3] }}</td>
                    <td><b>{{ row[5] }}</b></td>
                </tr>
            {% endfor %}
        </table>

        <h3>📋 Status Slot Parkir</h3>
        <div class="slots-container">
            {% for slot in slots %}
                <div class="slot {% if slot[1]==1 %}kosong{% else %}isi{% endif %}">
                    {{ slot[0] }}
                </div>
            {% endfor %}
        </div>

        <footer>© 2025 Sistem Parkir Otomatis | @fzrilsntsa_</footer>
    </body>
    </html>
    ''', aktif=aktif, slots=slots)

# scan in
@app.route('/scan_in', methods=['POST'])
def scan_in():
    plate = request.form['plate'].upper()
    waktu_masuk = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect('parking_system.db')
    c = conn.cursor()
    c.execute("""
        SELECT slot_name FROM slot_parkir 
        WHERE available=1 
        ORDER BY CAST(SUBSTR(slot_name, INSTR(slot_name, ':')+1) AS INTEGER)
        LIMIT 1
    """)
    slot = c.fetchone()

    if not slot:
        conn.close()
        return "<h2>❌ Parkiran penuh!</h2><a href='/'>Kembali</a>"

    slot = slot[0]

    c.execute("INSERT INTO parking_log (plate_number, status, waktu_masuk, slot) VALUES (?, 'IN', ?, ?)", 
              (plate, waktu_masuk, slot))
    c.execute("UPDATE slot_parkir SET available=0 WHERE slot_name=?", (slot,))
    conn.commit()
    conn.close()

    return render_template_string('''
        <body style="font-family: Poppins; text-align:center; background:#f1f9f2;">
            <h2 style="color:green;">✅ Kendaraan Berhasil Masuk</h2>
            <p>Plat Nomor: <b>{{ plate }}</b></p>
            <p>Waktu Masuk: <b>{{ waktu }}</b></p>
            <p style="font-size:18px;">Silakan menuju <b style="color:green;">Slot {{ slot }}</b></p>
            <a href="/" style="text-decoration:none;color:#007bff;">Kembali ke Halaman Utama</a>
        </body>
    ''', plate=plate, waktu=waktu_masuk, slot=slot)

# scan out
@app.route('/scan_out', methods=['POST'])
def scan_out():
    plate = request.form['plate'].upper()
    conn = sqlite3.connect('parking_system.db')
    c = conn.cursor()

    c.execute("SELECT slot FROM parking_log WHERE plate_number=? AND status='IN' ORDER BY id DESC LIMIT 1", (plate,))
    data = c.fetchone()
    if not data:
        conn.close()
        return "<h2>❌ Plat tidak ditemukan / sudah keluar.</h2><a href='/'>Kembali</a>"

    slot = data[0]
    waktu_keluar = datetime.now().strftime("%H:%M:%S")
    c.execute("UPDATE parking_log SET status='OUT', waktu_keluar=? WHERE plate_number=? AND status='IN'", (waktu_keluar, plate))
    c.execute("UPDATE slot_parkir SET available=1 WHERE slot_name=?", (slot,))
    conn.commit()
    conn.close()

    return render_template_string('''
        <body style="font-family:Poppins; text-align:center; background:#fff5f5;">
            <h2 style="color:#dc3545;">🚗 Kendaraan Keluar</h2>
            <p>Plat Nomor: <b>{{ plate }}</b></p>
            <p>Slot yang dikosongkan: <b style="color:red;">{{ slot }}</b></p>
            <a href="/" style="text-decoration:none;color:#007bff;">Kembali ke Halaman Utama</a>
        </body>
    ''', plate=plate, slot=slot)

# main
if __name__ == '__main__':
    app.run(debug=True)
