# POS WhatsApp Receipt for Odoo 17

![Odoo](https://img.shields.io/badge/Odoo-17.0-purple)
![License](https://img.shields.io/badge/License-LGPL--3-blue)
![WhatsApp](https://img.shields.io/badge/WhatsApp-OpenWA-green)

Module Odoo 17 untuk mengirim struk POS via WhatsApp menggunakan [OpenWA](https://github.com/fadlizarli/openwa) — WhatsApp API gateway open-source yang self-hosted.

---

## Fitur

- Kirim struk otomatis ke WhatsApp pelanggan setelah transaksi
- Nomor WA customer **otomatis terisi** dari data kontak pelanggan
- Tampilan struk lengkap: logo toko, kasir, item, metode pembayaran, kembalian
- Link struk bisa dibuka tanpa login (public access)
- Responsive di mobile
- Integrasi dengan OpenWA (self-hosted, gratis, open-source)
- Template pesan yang bisa dikustomisasi
- Nomor WA otomatis diformat ke format internasional (08xxx → 628xxx)

---

## Requirement

- Odoo 17.0
- OpenWA berjalan di server (lihat [panduan instalasi OpenWA](https://github.com/fadlizarli/openwa))
- Module Odoo: `point_of_sale`, `web`

---

## Instalasi

**1. Clone module ke addon path:**

```bash
cd /opt/odoo/custom-addons
git clone https://github.com/fadlizarli/pos_whatsapp_receipt_openwa.git pos_whatsapp_receipt
```

**2. Tambahkan path di `odoo.conf`:**

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
```

**3. Restart Odoo:**

```bash
sudo systemctl restart odoo
```

**4. Install module:**

Masuk Odoo → Apps → Search `POS WhatsApp Receipt` → Install

---

## Setup OpenWA

Sebelum mengkonfigurasi module ini, pastikan OpenWA sudah berjalan:

**1. Jalankan OpenWA via Docker:**

```bash
git clone https://github.com/fadlizarli/openwa.git
cd openwa
cp .env.minimal .env
docker compose up -d
```

**2. Buka dashboard OpenWA:**

```
http://IP-SERVER:2886
```

**3. Buat sesi WhatsApp baru:**
- Klik **New Session** → beri nama (contoh: `default`)
- Scan QR code dengan WhatsApp di HP

**4. Buat API Key:**
- Menu **Auth → API Keys** → **Create Key**
- Salin API key yang dihasilkan

---

## Konfigurasi di Odoo

Masuk ke **Settings → WhatsApp Receipt**:

### OpenWA

| Field | Keterangan | Contoh |
|-------|-----------|--------|
| **Base URL** | URL server OpenWA | `http://192.168.1.10:2785` |
| **API Key** | API key dari OpenWA (buat di menu Auth > API Keys) | `owa_k1_xxxxxxxxxxxx` |
| **Session ID** | UUID sesi WhatsApp (bukan nama) | `086fa308-03f2-4725-9fba-c339de489394` |
| **Template Pesan** | Template dengan variabel `{total}`, `{date}`, `{receipt_url}` | Lihat contoh di bawah |

> **Penting:** Session ID harus menggunakan **UUID**, bukan nama sesi. Dapatkan UUID dari dashboard OpenWA atau via API:
> ```bash
> curl -s http://IP-SERVER:2785/api/sessions -H "x-api-key: API_KEY_ANDA"
> ```
> Salin nilai `"id"` dari response JSON.
>
> **Catatan:** UUID berubah setiap kali sesi dihapus dan dibuat ulang. Jika mengganti sesi, update kembali Session ID di **Settings → WhatsApp Receipt**.

### YOURLS URL Shortener (Opsional)

| Field | Keterangan | Contoh |
|-------|-----------|--------|
| **YOURLS URL** | URL server YOURLS | `https://s.domain.com` |
| **Signature Token** | Token dari YOURLS (Tools > Secure passwordless API call) | `abc123xyz` |

Jika YOURLS dikonfigurasi, link struk di pesan WA akan dipersingkat otomatis. Jika tidak dikonfigurasi, link panjang tetap digunakan.

**Cara mendapatkan Signature Token YOURLS:**
1. Login ke dashboard YOURLS
2. Buka **Tools → Secure passwordless API call**
3. Salin **Secret signature token**

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
3. Setelah payment, kolom WhatsApp **otomatis terisi** nomor customer
4. Jika belum terisi, masukkan manual (format: `08xxx` atau `628xxx`)
5. Klik tombol hijau WhatsApp
6. Pelanggan menerima pesan WA dengan link struk lengkap
7. Link struk dapat dibuka tanpa perlu login ke Odoo

---

## Troubleshooting

**Link struk 404 / Not Found**
- Pastikan module sudah ter-install di database yang aktif
- Cek `web.base.url` sudah sesuai domain
- Pastikan `dbfilter` di `odoo.conf` tidak memblokir akses publik

**WA tidak terkirim**
- Cek Base URL dan API Key OpenWA di Settings
- Pastikan sesi WhatsApp di OpenWA statusnya `CONNECTED`
- Cek log Odoo: `sudo journalctl -u odoo -n 50`
- Cek log OpenWA: `docker compose logs -f`

**Sesi WhatsApp disconnect / failed setelah VPS restart**

Cek status sesi via API:
```bash
curl -s 'http://localhost:2785/api/sessions' -H 'x-api-key: API_KEY_ANDA' | python3 -m json.tool
```
Jika status `disconnected` atau `failed`, restart sesi dengan UUID-nya:
```bash
curl -s -X POST 'http://localhost:2785/api/sessions/UUID_SESI/start' -H 'x-api-key: API_KEY_ANDA'
```
Kemudian buka dashboard OpenWA → klik sesi → **View** → scan QR code ulang.

**Session ID di Odoo perlu diupdate**

Jika sesi dihapus dan dibuat ulang, UUID berubah. Update di:
**Settings → WhatsApp Receipt → Session ID** → isi UUID baru → Save.

Test kirim pesan untuk verifikasi:
```bash
curl -s -X POST 'http://localhost:2785/api/sessions/UUID_SESI/messages/send-text' \
  -H 'x-api-key: API_KEY_ANDA' \
  -H 'Content-Type: application/json' \
  -d '{"chatId":"628xxxxxxxxxx@c.us","text":"Test dari OpenWA"}' | python3 -m json.tool
```
Jika muncul `messageId` di response → berhasil.

**Error koneksi ke OpenWA**
- Pastikan port `2785` bisa diakses dari server Odoo
- Jika Odoo dan OpenWA di server berbeda, pastikan firewall mengizinkan koneksi

---

## Perbedaan dengan Versi Fonnte

| | Versi Lama (Fonnte) | Versi Ini (OpenWA) |
|--|--------------------|--------------------|
| **Biaya** | Berbayar (per pesan/bulan) | Gratis |
| **Data** | Di server Fonnte | Di server sendiri |
| **Setup** | Daftar akun Fonnte | Install OpenWA sendiri |
| **Konfigurasi** | Token + Nomor pengirim | Base URL + API Key + Session ID |

---

## Struktur Module

```
pos_whatsapp_receipt/
├── controllers/
│   └── main.py
├── models/
│   ├── pos_order.py
│   ├── res_config_settings.py
│   └── short_url.py
├── static/src/
│   ├── js/receipt_button.js
│   └── xml/receipt_button.xml
├── views/
│   ├── res_config_settings_views.xml
│   └── receipt_template.xml
├── __manifest__.py
└── README.md
```

---

## Changelog

### v17.0.2.2.0
- Integrasi YOURLS untuk mempersingkat link struk di pesan WA
- Ganti TinyURL dengan YOURLS self-hosted (konfigurasi opsional)

### v17.0.2.1.0
- Nomor WA customer otomatis terisi dari kontak saat layar struk terbuka
- Fix asset path sesuai nama folder module

### v17.0.2.0.0
- Migrasi dari Fonnte ke OpenWA (self-hosted)
- Ganti konfigurasi token/sender dengan Base URL, API Key, Session ID (UUID)
- Update endpoint API ke format OpenWA

### v17.0.1.0.0
- Initial release dengan Fonnte

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
Menggunakan OpenWA sebagai WhatsApp API gateway open-source.
