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
- **WhatsApp otomatis generate preview dari OG tags** — kirim plain text, biarkan WhatsApp crawl OG tags untuk generate preview card dengan logo, title, deskripsi
- **Reliable dan sederhana** — plain text message, tidak perlu kirim image thumbnail atau link preview parsing
- **Tampilan konsisten** di semua device (Web, Mobile, Desktop) — sama untuk sender dan receiver
- Integrasi dengan Baileys server (self-hosted, gratis, open-source, tanpa Chromium)
- Template pesan yang bisa dikustomisasi
- Nomor WA otomatis diformat ke format internasional (08xxx → 628xxx)
- **Built-in URL shortener** — otomatis generate short code `/struk/XXXXXXX` per order, disimpan di database
- **Large Thumbnail Preview** — externalAdReply dengan `renderLargerThumbnail: true` untuk tampilan thumbnail besar di atas pesan

---

## Requirement

- Odoo 17.0
- Node.js >= 18.0.0 (untuk Baileys server v7 dengan ESM support)
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

> **Note**: Baileys v7 menggunakan ESM modules. Jika upgrade dari v6, auth session lama mungkin tidak kompatibel.
> 
> **Thumbnail Preview Configuration**: Server menggunakan `getUrlInfo()` native Baileys untuk extract metadata (title, description, thumbnail) dari URL struk. Timeout 10 detik untuk fetch metadata agar tidak mengganggu pengiriman pesan. Jika timeout, fallback otomatis ke plain text message.

### 4. Scan QR WhatsApp

Buka browser dan akses:
```
http://IP-SERVER:3000/qr
```

Scan QR code dengan WhatsApp di HP → **Perangkat Tertaut → Tautkan Perangkat**.

> **Catatan untuk upgrade v6→v7**: Jika mendapat error atau koneksi gagal setelah upgrade, hapus folder `auth_info` dan scan QR ulang:
> ```bash
> rm -rf /opt/odoo/custom-addons/pos_whatsapp_receipt_baileys/baileys-server/auth_info
> # Restart server
> ```

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

### URL Shortener (Built-in)

Sistem URL shortener sudah **built-in** dan **otomatis**:
- Setiap order mendapat short code **7 karakter** (huruf besar + angka) yang unik
- Contoh: `/struk/VP69O8A` → redirect ke `/resit/lihat?access_token=...`
- Disimpan di model `pos.short.url` di database Odoo
- **Tidak perlu konfigurasi eksternal** — bekerja otomatis saat kirim WA

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

### WhatsApp Receipt dengan Large Thumbnail Preview

Saat struk dikirim via WhatsApp:
- **Text Message + External Ad Reply**: Pesan dari template dikirim dengan metadata preview menggunakan `externalAdReply`
- **Large Thumbnail**: Menggunakan `renderLargerThumbnail: true` untuk tampilan thumbnail **besar di atas pesan** (seperti preview artikel/iklan bisnis)
- **Auto-Generated Metadata**: Baileys otomatis extract metadata dari URL menggunakan `getUrlInfo()`:
  - Title dari OG tags / `<title>` tag
  - Description dari `og:description` / `<meta name="description">`
  - Thumbnail JPEG dari `og:image` atau preview dari halaman
- **Preview Card Include**: 
  - `title` — "Struk Pembayaran - {nama toko}"
  - `body` — total transaksi + ringkasan item
  - `jpegThumbnail` — logo toko dalam format JPEG (auto-generated dari URL metadata)

**Keuntungan:**
- **Tampilan menonjol** — thumbnail besar di atas (lebih eye-catching dibanding compact link preview)
- **Konsisten di receiver** — externalAdReply langsung embedded di pesan, tidak tergantung WhatsApp crawl
- **Graceful fallback** — jika metadata extraction gagal, pesan plain text tetap terkirim
- **Self-hosted** — semua processing di Baileys server, tidak ada dependency eksternal
- **10 detik timeout** — cukup untuk fetch metadata, jika gagal langsung fallback ke plain text

> **Catatan**: Jika `externalAdReply` tidak muncul di receiver, kemungkinan WhatsApp server strip field tersebut. Fallback otomatis ke plain text message saja. URL struk menggunakan short code `/struk/XXXXXXX` yang redirect ke `/resit/lihat?access_token=...` untuk akses publik tanpa login.

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

**Error: "Cannot use import statement outside a module"**

Baileys v7 menggunakan ESM. Pastikan:
1. Node.js >= 18.0.0
2. File `baileys-server/package.json` punya `"type": "module"`
3. Server.js menggunakan `import` (bukan `require`)
4. Jika custom code, ganti semua `require()` dengan `import`

**Test kirim pesan manual:**
```bash
curl -s -X POST http://localhost:3000/send-message \
  -H "x-api-key: API_KEY_ANDA" \
  -H "Content-Type: application/json" \
  -d '{"phone":"628xxxxxxxxxx","message":"Test dari Baileys"}'
```
Jika muncul `{"success": true}` → berhasil.

---

## API Odoo

| Endpoint | Method | Keterangan | Auth |
|----------|--------|-----------|------|
| `/pos/send_whatsapp_receipt` | POST | Kirim struk ke WhatsApp | Required (user) |
| `/struk/<code>` | GET | Redirect short URL ke struk lengkap | Public |
| `/resit/lihat` | GET | Tampilkan struk lengkap (HTML) | Public |

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
  "message": "Terima kasih! Total: Rp 100.000. Lihat struk: https://domain.com/struk/VP69O8A",
  "receipt_url": "https://domain.com/struk/VP69O8A"
}
```

**Parameter `/send-message`:**
| Parameter | Tipe | Required | Keterangan |
|-----------|------|----------|-----------|
| `phone` | String | Ya | Nomor WhatsApp (format: `628xxxxxxxxxx` atau `08xxxxxxxxxx`) |
| `message` | String | Ya | Pesan teks yang akan dikirim |
| `receipt_url` | String | Tidak | URL struk untuk auto-extract metadata (OG tags, title, description, image) untuk preview card |

**Fitur Large Thumbnail Preview dengan Auto-Detection:**
1. Odoo prepare `message` dari template dengan URL struk (short code `/struk/XXXXXXX`)
2. Odoo kirim ke Baileys API dengan `receipt_url` parameter
3. **Baileys auto-extract metadata** menggunakan `getUrlInfo()` dari Baileys library:
   - `getUrlInfo(receipt_url, { thumbnailWidth: 300, timeoutMs: 10000 })` extract metadata dari URL
   - Result include: `title`, `description`, `jpegThumbnail`, `canonical-url`, `matched-text`
   - **Struktur pesan**: Gunakan `externalAdReply` dengan `renderLargerThumbnail: true` untuk tampilan besar di atas
   - Preview card dengan title, body (description), dan jpegThumbnail
   - **Keuntungan**: Thumbnail besar more eye-catching dibanding compact link preview
4. WhatsApp menerima pesan dengan externalAdReply yang sudah embedded
5. Tampilan **large thumbnail di atas pesan** — eye-catching untuk receipt/business preview
6. **Reliable** — `getUrlInfo()` built-in Baileys, tidak ada external dependency
7. **Graceful fallback** — jika metadata extraction gagal (timeout/network), plain text message tetap terkirim dengan fallback msgPayload

---

## Struktur Module

```
pos_whatsapp_receipt_baileys/
├── baileys-server/
│   ├── server.js           ← REST API Node.js (Baileys)
│   ├── package.json
│   └── .env.example
├── controllers/
│   └── main.py             ← Endpoint kirim WA + redirect short URL + view struk publik
├── models/
│   ├── pos_order.py        ← Method send_whatsapp_receipt (via ORM)
│   ├── res_config_settings.py
│   ├── short_url.py        ← Model pos.short.url: menyimpan short code → long URL mapping
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

### v17.0.1.0.4 (Current - Testing externalAdReply)
- **Experiment: Large Thumbnail Preview dengan `externalAdReply + renderLargerThumbnail`**:
  - Ubah dari `linkPreview` (compact) ke `externalAdReply` dengan `renderLargerThumbnail: true`
  - Ganti metadata extraction dari `link-preview-js` ke `getUrlInfo()` native Baileys
  - `getUrlInfo()` extract title, description, jpegThumbnail dari URL dengan 10 detik timeout
  - Thumbnail besar di atas pesan lebih eye-catching untuk receipt (seperti preview artikel/bisnis)
  - **Graceful fallback**: Jika `getUrlInfo()` timeout/error, fallback ke plain text message saja
  - **Testing**: Jika `externalAdReply` tidak muncul di receiver, rollback ke `linkPreview`
  - Removed: `link-preview-js` dependency (sekarang gunakan native `getUrlInfo()`)
  - Logger tetap `warn` untuk visibility error internal Baileys

### v17.0.1.0.3 (Deprecated - linkPreview approach)
- **CRITICAL FIX: `linkPreview` field structure (WAUrlInfo dengan hyphenated keys)**:
  - **Root cause found**: Sebelumnya pass camelCase fields di top-level (`canonicalUrl`, `matchedText`, `title`, dll) — tapi Baileys **silently ignore** semua itu
  - **Correct structure**: Pass `linkPreview: urlInfo` dimana `urlInfo` adalah WAUrlInfo object dengan **hyphenated keys** (`canonical-url`, `matched-text`, dll)
  - Baileys membaca **hanya** `message.linkPreview` field, field top-level lain diabaikan
  - Logger diubah dari `silent` ke `warn` agar error internal Baileys terlihat
  - **Keuntungan**: Preview card sekarang muncul di receiver dengan sempurna, bukan hanya di sender saja
- **Baileys Link Preview Auto-Detection dengan `link-preview-js`**:
  - Added dependency: `link-preview-js` v3 (ESM-compatible dengan Baileys v7)
  - Added config: `generateHighQualityLinkPreview: true` di Baileys socket initialization
  - Baileys otomatis detect URL di pesan dan generate high-quality link preview menggunakan `link-preview-js`
  - Preview card auto-generated dari OG tags tanpa perlu manual extraction di Odoo
  - Odoo pass `receipt_url` ke Baileys API untuk URL metadata extraction
  - **Seamless integration**: Preview card generated langsung oleh Baileys sebelum kirim ke WhatsApp

### v17.0.1.0.2
- **Plain Text Message dengan OG Tags Preview** (ganti image+caption):
  - Sebelumnya kirim logo sebagai gambar WhatsApp dengan teks caption
  - Sekarang kirim plain text message saja, biarkan WhatsApp crawl OG tags untuk generate preview
  - Removed: image resizing, base64 encoding, `jpeg_thumbnail` parameter
  - Baileys server: hanya terima `phone` dan `message`, tidak perlu `jpeg_thumbnail`
  - Controllers/main.py: hapus PIL image processing, kirim plain text message
  - Keuntungan: lebih sederhana, lebih reliable (tidak ada image encoding overhead), consistent dengan behavior paste URL manual
  - URL struk di halaman `/struk/<code>` include OG meta tags untuk preview generation

### v17.0.1.0.1
- **Route Changed: `/r/` → `/struk/`** (menghindari konflik dengan Odoo website module):
  - Odoo website module menggunakan `/r/<path>` untuk internal redirect
  - Ganti route short URL dari `/r/<code>` ke `/struk/<code>` agar tidak blocked
  - Dokumentasi dan contoh URL di README sudah updated
  - URL struk sekarang: `/struk/VP69O8A` instead of `/r/VP69O8A`

### v17.0.1.0.0
- **Built-in Short URL System** (ganti YOURLS):
  - Model `pos.short.url` menyimpan `code` → `url` mapping di database Odoo
  - Generate short code **7 karakter** (huruf besar + angka) otomatis per order
  - Route `/struk/<code>` redirect ke `/resit/lihat?access_token=...`
  - URL WA jadi lebih pendek dan profesional: `/struk/VP69O8A` instead of full URL
  - **Keuntungan**: Tidak perlu server eksternal YOURLS, fully self-hosted di Odoo
  - Automatic collision detection — generate ulang jika code sudah ada
  - Model `pos.short.url` include security rule via `security/ir.model.access.csv`

### v17.0.3.0.0
- **Upgrade Baileys v6 → v7** (major version jump):
  - Baileys v7 menggunakan **ESM modules** (ES6 import/export) — bukan CommonJS
  - Changed package: `@whiskeysockets/baileys@6.7.9` → `baileys@7.0.0-rc13`
  - Updated server.js: semua `require()` diganti dengan `import`, tambah `"type": "module"` di package.json
  - Removed `fetchLatestBaileysVersion()` — v7 otomatis handle version management
  - Simplified socket initialization — v7 lebih streamlined
  - **Breaking change**: Hosting WhatsApp session mungkin perlu **scan QR ulang** setelah upgrade (old auth_info tidak kompatibel)
  - **Benefits**: Lebih lightweight, lebih cepat, dukungan long-term lebih baik

### v17.0.2.9.0 (Deprecated → v17.0.1.0.2)
- **Image+Caption Approach** (diganti di v17.0.1.0.2 dengan plain text + OG tags):
  - Odoo resize logo ke JPEG 512x512px dengan quality 85
  - Logo dikirim sebagai gambar WhatsApp dengan teks pesan sebagai caption
  - Server.js: `jpeg_thumbnail` di-decode dari base64 dan dikirim sebagai `imageMessage`
  - **Diganti di v17.0.1.0.2** dengan plain text message karena lebih sederhana dan reliable

### v17.0.2.8.0
- **Automatic Link Preview dengan `link-preview-js`** (deprecated di v17.0.2.9.0):
  - Tambah dependency `link-preview-js` untuk URL metadata extraction
  - Baileys otomatis detect URL di pesan dan generate preview card menggunakan `link-preview-js`
  - **Masalah**: `link-preview-js` gagal fetch URL dari VPS → pesan tidak terkirim
  - Di-revert ke image+caption di v17.0.2.9.0

### v17.0.2.7.0
- **Manual Link Preview Build** (deprecated):
  - Odoo prepare metadata: title, description, logo thumbnail (resize ke 300px JPEG)
  - Baileys build `extendedTextMessage` dengan format yang sama saat paste URL manual di WhatsApp

### v17.0.2.6.0
- **Automatic Link Preview dengan `getUrlInfo()` dan fix `timeoutMs`** (deprecated):
  - Menggunakan Baileys `getUrlInfo()` dengan opsi `timeoutMs`
  - Pass `receipt_url` dari Odoo ke Baileys untuk metadata extraction

### v17.0.2.5.0
- **Logo otomatis di-resize ke JPEG 512px sebelum kirim** (deprecated):
  - Konversi dari format asli (PNG, JPG, dll) ke JPEG dengan quality 85
  - Dikompres ke maksimal 512x512 pixels agar lebih kecil dan cepat upload

### v17.0.2.4.0
- **Logo dikirim sebagai Image WhatsApp** — bukan preview card:
  - Logo toko dikirim sebagai gambar WhatsApp dengan teks pesan sebagai caption
  - Tampilan **konsisten di semua device** (Web, Mobile, Desktop)

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
