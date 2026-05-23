# POS WhatsApp Receipt for Odoo 17 (Baileys)

![Odoo](https://img.shields.io/badge/Odoo-17.0-purple)
![License](https://img.shields.io/badge/License-LGPL--3-blue)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Baileys-green)

Module Odoo 17 untuk mengirim struk POS via WhatsApp menggunakan **Baileys** — library WhatsApp Web open-source berbasis Node.js. Tidak membutuhkan Chromium/browser.

---

## Fitur

- Kirim struk ke WhatsApp pelanggan setelah transaksi POS
- Input field WhatsApp inline di layar struk (bukan popup dialog)
- Nomor WA customer **otomatis terisi** dari data kontak pelanggan (mobile → phone)
- Tombol hijau WhatsApp di sebelah kanan input dengan spinner loading
- Status message (sukses/gagal) ditampilkan inline di bawah input
- Tampilan struk lengkap: logo toko, kasir, item, metode pembayaran, kembalian
- Link struk bisa dibuka tanpa login (public access)
- **Responsive di mobile**
- **Logo toko dikirim sebagai gambar WhatsApp** — bukan preview card, dengan teks pesan sebagai caption
- **Logo di-resize otomatis** ke JPEG dari logo company data Odoo
- **Konsisten di semua device** — tampilan sama di sender dan receiver, kompatibel dengan semua versi WhatsApp (Web, Mobile, Desktop)
- **Reliable tanpa dependency eksternal** — tidak perlu fetch URL dari server, tidak perlu parsing HTML
- Integrasi dengan Baileys server (self-hosted, gratis, open-source, tanpa Chromium)
- Template pesan yang bisa dikustomisasi
- Nomor WA otomatis diformat ke format internasional (08xxx → 628xxx)
- URL shortener opsional via YOURLS (self-hosted)

---

## Requirement

- Odoo 17.0
- Node.js >= 18.0.0 (untuk Baileys server)
- Module Odoo: `point_of_sale`, `web`

---

## Instalasi

### 1. Clone module ke addon path

```bash
cd /opt/odoo/custom-addons
git clone https://github.com/fadlizarli/pos_whatsapp_receipt_baileys.git pos_whatsapp_receipt_baileys
```

### 2. Tambahkan path di `odoo.conf`

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
```

### 3. Restart Odoo

```bash
sudo systemctl restart odoo
```

### 4. Install module

Masuk Odoo → Apps → Search `POS WhatsApp Receipt` → Install

---

## Setup Baileys Server

Baileys server adalah REST API ringan yang menghubungkan Odoo ke WhatsApp via Baileys (tanpa Chromium).

### 1. Masuk ke folder baileys-server

```bash
cd /opt/odoo/custom-addons/pos_whatsapp_receipt_baileys/baileys-server
```

### 2. Buat file `.env`

```bash
cp .env.example .env
nano .env
```

Isi dengan nilai bebas — `API_KEY` adalah kunci rahasia yang **kamu tentukan sendiri**:
```
PORT=3000
API_KEY=isi-string-acak-sesukamu
```

> Nilai `API_KEY` ini yang nanti dimasukkan ke field **API Key** di Settings Odoo.
> Gunakan string acak yang susah ditebak, contoh: `xK9mP2qL7vR4nW1j`

### 3. Install dependensi dan jalankan

```bash
npm install
npm start
```

### 4. Scan QR WhatsApp

Buka browser dan akses:
```
http://IP-SERVER:3000/qr
```

Scan QR code dengan WhatsApp di HP → **Perangkat Tertaut → Tautkan Perangkat**.

### 5. Verifikasi status koneksi

```bash
curl -s http://localhost:3000/status -H "x-api-key: API_KEY_ANDA"
# → {"connected": true, "hasQR": false}
```

### Menjalankan sebagai service (opsional)

**Pilihan 1: Menggunakan PM2 (mudah, universal)**

```bash
# Install pm2
npm install -g pm2

# Jalankan
pm2 start /opt/odoo/custom-addons/pos_whatsapp_receipt_baileys/baileys-server/server.js --name baileys-wa

# Auto-start saat reboot
pm2 startup
pm2 save
```

**Pilihan 2: Menggunakan Systemd (native Linux, recommended untuk VPS)**

Buat file service:
```bash
sudo nano /etc/systemd/system/baileys-wa.service
```

Isi file dengan:
```ini
[Unit]
Description=Baileys WhatsApp Server
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/odoo/custom-addons/pos_whatsapp_receipt_baileys/baileys-server
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Aktifkan dan jalankan:
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable auto-start saat reboot
sudo systemctl enable baileys-wa

# Start service sekarang
sudo systemctl start baileys-wa

# Cek status
sudo systemctl status baileys-wa

# View logs real-time
sudo journalctl -u baileys-wa -f
```

> **Keuntungan Systemd**: Auto-restart jika process crash, auto-start saat VPS reboot, logs terintegrasi dengan journalctl, tidak perlu npm global, standar sistem Linux.

---

## Konfigurasi di Odoo

Masuk ke **Settings → WhatsApp Receipt**:

### Baileys WhatsApp Server

| Field | Keterangan | Contoh |
|-------|-----------|--------|
| **Server URL** | URL server Baileys | `http://localhost:3000` |
| **API Key** | Bebas ditentukan sendiri — harus sama persis dengan nilai `API_KEY` di file `baileys-server/.env` | `string-acak-rahasia` |
| **Template Pesan** | Template dengan variabel `{total}`, `{date}`, `{receipt_url}` | Lihat contoh di bawah |

### YOURLS URL Shortener (Opsional)

| Field | Keterangan | Contoh |
|-------|-----------|--------|
| **YOURLS URL** | URL server YOURLS | `https://s.domain.com` |
| **Signature Token** | Token dari YOURLS (Tools > Secure passwordless API call) | `abc123xyz` |

Jika YOURLS dikonfigurasi, link struk di pesan WA akan dipersingkat otomatis.

**Contoh template pesan:**

```
Terima kasih telah berbelanja!

Total: {total}
Tanggal: {date}

Lihat struk lengkap:
{receipt_url}
```

**Set base URL agar link struk menggunakan domain yang benar:**

```bash
sudo -u odoo psql -d NAMA_DATABASE -c \
  "UPDATE ir_config_parameter SET value='https://domain-kamu.com' WHERE key='web.base.url';"
```

---

## Cara Pakai

1. Buka POS dan lakukan transaksi seperti biasa
2. Pilih customer yang sudah ada nomor HP-nya di kontak Odoo
3. Setelah payment, layar struk menampilkan:
   - Input field WhatsApp dengan nomor customer **otomatis terisi** dari kontak
   - Tombol hijau WhatsApp di sebelah kanan input
4. Jika nomor belum terisi, masukkan manual (format: `08xxx` atau `628xxx`)
5. Klik tombol hijau — spinner akan muncul saat proses kirim
6. Pesan sukses/gagal ditampilkan di bawah input field
7. Pelanggan menerima pesan WA dengan link struk lengkap yang dapat dibuka tanpa login

### WhatsApp Receipt dengan Logo

Saat struk dikirim via WhatsApp:
- **Gambar**: Logo toko dikirim sebagai gambar WhatsApp (format JPEG)
- **Caption**: Teks pesan dari template (total, tanggal, link struk)

**Keuntungan:**
- Tampilan **konsisten di semua device** (Web, Mobile, Desktop)
- Sama untuk **sender dan receiver** (tidak ada perbedaan tampilan)
- **Reliable** — tidak perlu fetch URL dari server, tidak perlu parsing HTML
- **Cepat** — logo sudah di-resize dari company data Odoo
- Tidak perlu `extendedTextMessage` atau preview card metadata extraction
- **Graceful fallback** — jika tidak ada logo, teks pesan tetap terkirim dengan sukses

> **Catatan**: Link struk menggunakan `receipt_url` (bisa short URL dari YOURLS atau full URL). Pastikan `web.base.url` sudah diatur dengan domain yang benar di Odoo settings.

---

## Troubleshooting

**Link struk 404 / Not Found**
- Pastikan module sudah ter-install di database yang aktif
- Cek `web.base.url` sudah sesuai domain
- Pastikan `dbfilter` di `odoo.conf` tidak memblokir akses publik

**WA tidak terkirim**
- Cek Server URL dan API Key Baileys di Settings
- Pastikan Baileys server berjalan: `curl http://localhost:3000/status -H "x-api-key: KEY"`
- Cek status koneksi: `{"connected": true}` harus muncul
- Cek log Odoo: `sudo journalctl -u odoo -n 50`
- Cek log Baileys: `pm2 logs baileys-wa` atau `node server.js`

**WhatsApp disconnect setelah server restart**

```bash
# Cek status
curl -s http://localhost:3000/status -H "x-api-key: API_KEY_ANDA"
```

Jika `connected: false`, buka `/qr` di browser dan scan ulang QR code.

Jika logout permanen (status `loggedOut`):
```bash
# Hapus sesi lama
rm -rf /path/to/baileys-server/auth_info

# Restart server (gunakan command sesuai pilihan service manager)
# Jika menggunakan PM2:
pm2 restart baileys-wa

# Jika menggunakan Systemd:
sudo systemctl restart baileys-wa
```

Kemudian scan QR ulang.

**Baileys server tidak jalan setelah VPS reboot**

Jika Baileys dijalankan dengan `nohup` atau tanpa service manager, process akan mati saat VPS reboot. Solusi:

1. **Gunakan Systemd service** (recommended) — lihat bagian "Menjalankan sebagai service" di atas
2. **Atau gunakan PM2** dengan `pm2 startup` dan `pm2 save`

Verifikasi:
```bash
# Jika menggunakan Systemd:
sudo systemctl status baileys-wa

# Jika menggunakan PM2:
pm2 list
```

Keduanya akan memastikan Baileys **auto-start saat VPS reboot** dan **auto-restart jika process crash**.

**Test kirim pesan manual:**
```bash
curl -s -X POST http://localhost:3000/send-message \
  -H "x-api-key: API_KEY_ANDA" \
  -H "Content-Type: application/json" \
  -d '{"phone":"628xxxxxxxxxx","message":"Test dari Baileys"}'
```
Jika muncul `{"success": true}` → berhasil.

---

## API Baileys Server

| Endpoint | Method | Keterangan | Auth |
|----------|--------|-----------|------|
| `/status` | GET | Cek status koneksi WhatsApp | Required |
| `/qr` | GET | Tampilkan QR code (HTML) untuk scan | **Tidak ada** |
| `/send-message` | POST | Kirim pesan teks | Required |

Endpoint dengan Auth Required membutuhkan header: `x-api-key: API_KEY_ANDA`

**Catatan:** Endpoint `/qr` tidak memerlukan API key agar bisa dibuka langsung di browser tanpa perlu konfigurasi tambahan.

**Body `/send-message`:**
```json
{
  "phone": "628xxxxxxxxxx",
  "message": "Terima kasih! Total: Rp 100.000. Lihat struk: https://domain.com/resit/lihat?access_token=...",
  "preview": {
    "jpeg_thumbnail": "base64_encoded_jpeg_image"
  }
}
```

**Fitur Logo sebagai Gambar WhatsApp:**
1. Odoo kirim `preview` object ke Baileys dengan:
   - `jpeg_thumbnail`: Logo toko yang sudah di-resize ke JPEG (base64)
2. **Baileys kirim sebagai gambar WhatsApp** dengan caption teks pesan
3. Gambar ditampilkan di atas teks pesan (seperti kirim gambar biasa di WhatsApp)
4. Tampilan **konsisten di semua device** — gambar tampil sama di Web, Mobile, Desktop
5. **Lebih reliable** — tidak perlu parsing URL atau fetch metadata, hanya kirim gambar + teks
6. **Graceful fallback** — jika tidak ada `jpeg_thumbnail`, hanya kirim teks pesan saja

---

## Struktur Module

```
pos_whatsapp_receipt_baileys/
├── baileys-server/
│   ├── server.js           ← REST API Node.js (Baileys)
│   ├── package.json
│   └── .env.example
├── controllers/
│   └── main.py             ← Endpoint kirim WA + view struk publik
├── models/
│   ├── pos_order.py        ← Method send_whatsapp_receipt (via ORM)
│   ├── res_config_settings.py
│   └── short_url.py
├── static/src/
│   ├── js/receipt_button.js   ← OWL patch ReceiptScreen: auto-fill nomor, handler kirim WA
│   └── xml/receipt_button.xml ← Template: inline input WhatsApp + tombol hijau + status message
├── views/
│   ├── res_config_settings_views.xml
│   └── receipt_template.xml
├── __manifest__.py
└── README.md
```

---

## Changelog

### v17.0.2.8.0 (Current)
- **Revert ke Image+Caption** (dari Manual Link Preview):
  - Logo toko dikirim sebagai **gambar WhatsApp** (format JPEG) dengan teks pesan sebagai caption
  - **Lebih reliable & sederhana** — tidak perlu build `extendedTextMessage`, tidak perlu metadata extraction
  - Tampilan **konsisten di semua device** (Web, Mobile, Desktop) — gambar tampil sama di sender & receiver
  - **Graceful fallback** — jika tidak ada logo, teks pesan tetap terkirim tanpa error
  - Menghilangkan kompleksitas `extendedTextMessage` yang terkadang tidak stabil di beberapa client WhatsApp
  - Odoo resize logo dari company data dan encode ke base64, Baileys tinggal kirim sebagai gambar

### v17.0.2.7.0
- **Manual Link Preview Build** (deprecated di v17.0.2.8.0):
  - Odoo prepare metadata: title, description, logo thumbnail (resize ke 300px JPEG)
  - Baileys build `extendedTextMessage` dengan format yang sama saat paste URL manual di WhatsApp
  - Preview card muncul di bawah teks pesan — konsisten di semua device

### v17.0.2.6.0
- **Revert ke Automatic Link Preview dengan Fix `timeoutMs`** (deprecated di v17.0.2.7.0):
  - Menggunakan Baileys `getUrlInfo()` dengan opsi `timeoutMs` (bukan `fetchOpts.timeout`)
  - Pass `receipt_url` dari Odoo ke Baileys untuk metadata extraction
  - Graceful fallback jika `getUrlInfo` timeout/error

### v17.0.2.5.0
- **Logo otomatis di-resize ke JPEG 512px sebelum kirim** (deprecated di v17.0.2.6.0):
  - Konversi dari format asli (PNG, JPG, dll) ke JPEG dengan quality 85
  - Dikompres ke maksimal 512x512 pixels agar lebih kecil dan cepat upload
  - Mengurangi beban jaringan dan waktu pengiriman
  - Kompatibel dengan semua versi WhatsApp (Web, Mobile, Desktop)
  - Graceful fallback: jika resize gagal, teks pesan tetap terkirim tanpa logo

### v17.0.2.4.0
- **Logo dikirim sebagai Image WhatsApp** — bukan preview card (deprecated di v17.0.2.6.0):
  - Logo toko dikirim sebagai gambar WhatsApp dengan teks pesan sebagai caption
  - Tampilan **konsisten di semua device** (Web, Mobile, Desktop)
  - Sama untuk **sender dan receiver** — tidak ada perbedaan tampilan
  - Tidak perlu parsing URL atau fetch metadata
  - Graceful fallback: jika tidak ada logo, teks pesan tetap terkirim

### v17.0.2.3.0
- **WhatsApp Preview Card dengan Logo dari Odoo**:
  - Awalnya menggunakan `externalAdReply` untuk render preview card
  - Diganti dengan image+caption di v17.0.2.4.0 karena lebih konsisten di semua device
  - Dikembali ke automatic link preview di v17.0.2.6.0 dengan fix timeout

### v17.0.2.2.0
- **Automatic link preview extraction** menggunakan Baileys `getUrlInfo()`:
  - Saat pesan WhatsApp mengandung URL, Baileys server otomatis mengekstrak metadata (title, description, thumbnail)
  - Preview card WhatsApp muncul tanpa perlu paste URL manual
  - Fallback graceful jika server tidak bisa fetch metadata — pesan tetap terkirim tanpa preview
- Timeout 5 detik untuk metadata fetch agar tidak mengganggu pengiriman pesan
- **Note**: v17.0.2.2.0 punya timeout bug, di-fix di v17.0.2.6.0 dengan `timeoutMs`

### v17.0.2.1.0
- **Open Graph (OG) meta tags** untuk preview WhatsApp:
  - `og:title` → "Struk Pembayaran - {nama toko}"
  - `og:description` → total transaksi + ringkasan item (max 3 item)
  - `og:image` → logo toko dari company data
  - Twitter card fallback untuk kompatibilitas
- Saat URL struk dibagikan ke WhatsApp, akan menampilkan preview card dengan logo toko, judul struk, dan ringkasan transaksi

### v17.0.2.0.0
- **UI Rewrite**: Input WhatsApp dan tombol hijau sekarang inline di bawah email input (bukan popup dialog)
- Auto-fill nomor WA dari kontak customer (mobile → phone)
- Spinner indicator saat proses pengiriman
- Status message (success/error) ditampilkan inline di bawah input
- Styling sejalan dengan implementasi OpenWA yang terbukti stabil

### v17.0.1.0.0
- Initial release dengan Baileys (Node.js, tanpa Chromium)
- Baileys server: REST API sederhana dengan endpoint `/send-message`, `/status`, `/qr`
- Konfigurasi: Server URL + API Key
- OWL component: tombol "Kirim via WhatsApp" di ReceiptScreen POS
- Dialog input nomor HP dengan auto-fill dari kontak customer

---

## Kontribusi

1. Fork repo ini
2. Buat branch baru: `git checkout -b fitur-baru`
3. Commit: `git commit -m 'Tambah fitur X'`
4. Push: `git push origin fitur-baru`
5. Buat Pull Request

---

## Lisensi

LGPL-3

---

## Developer

Dibuat untuk kebutuhan bisnis ritel Indonesia.
Menggunakan Baileys sebagai WhatsApp Web library open-source ringan tanpa Chromium.
