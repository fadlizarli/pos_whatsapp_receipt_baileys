import 'dotenv/config';
import makeWASocket, {
    useMultiFileAuthState,
    DisconnectReason,
    getUrlInfo,
} from 'baileys';
import { Boom } from '@hapi/boom';
import express from 'express';
import pino from 'pino';
import QRCode from 'qrcode';

const app = express();
app.use(express.json());

const API_KEY = process.env.API_KEY;
const PORT = process.env.PORT || 3000;

if (!API_KEY) {
    console.error('ERROR: API_KEY tidak diset di .env');
    process.exit(1);
}

let sock = null;
let qrDataUrl = null;
let isConnected = false;
let isConnecting = false;

const logger = pino({ level: 'warn' });

function authMiddleware(req, res, next) {
    if (req.headers['x-api-key'] !== API_KEY) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
}

function formatPhone(phone) {
    let p = String(phone).replace(/[^0-9]/g, '');
    if (p.startsWith('0')) p = '62' + p.slice(1);
    return p + '@s.whatsapp.net';
}

async function connectToWhatsApp() {
    if (isConnecting) return;
    isConnecting = true;

    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');

    sock = makeWASocket({
        auth: state,
        logger,
        printQRInTerminal: true,
        browser: ['Baileys Server', 'Chrome', '10.0'],
        generateHighQualityLinkPreview: true,
    });

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            qrDataUrl = await QRCode.toDataURL(qr);
            isConnected = false;
            console.log('QR siap — buka GET /qr untuk scan');
        }

        if (connection === 'close') {
            isConnected = false;
            isConnecting = false;
            qrDataUrl = null;

            const statusCode = (lastDisconnect?.error instanceof Boom)
                ? lastDisconnect.error.output.statusCode
                : null;

            if (statusCode === DisconnectReason.loggedOut) {
                console.log('WhatsApp logout — hapus folder auth_info dan restart');
            } else {
                console.log('Koneksi terputus, mencoba reconnect...');
                setTimeout(connectToWhatsApp, 5000);
            }
        } else if (connection === 'open') {
            isConnected = true;
            isConnecting = false;
            qrDataUrl = null;
            console.log('WhatsApp terhubung!');
        }
    });

    sock.ev.on('creds.update', saveCreds);
}

// --- Endpoints ---

app.get('/status', authMiddleware, (req, res) => {
    res.json({
        connected: isConnected,
        hasQR: !!qrDataUrl,
    });
});

app.get('/qr', (req, res) => {
    if (isConnected) {
        return res.json({ connected: true, message: 'Sudah terhubung' });
    }
    if (!qrDataUrl) {
        return res.json({ connected: false, qr: null, message: 'QR belum siap, tunggu beberapa detik' });
    }
    res.send(`<!DOCTYPE html><html><head><title>Scan QR WhatsApp</title></head>
<body style="text-align:center;font-family:sans-serif;padding:40px">
<h2>Scan QR dengan WhatsApp</h2>
<img src="${qrDataUrl}" style="max-width:300px"/>
<p>Buka WhatsApp > Perangkat Tertaut > Tautkan Perangkat</p>
<p><small>Halaman ini akan otomatis kadaluarsa saat QR berubah</small></p>
</body></html>`);
});

app.post('/send-message', authMiddleware, async (req, res) => {
    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp belum terhubung. Scan QR terlebih dahulu di GET /qr' });
    }

    const { phone, message, receipt_url, logo_url } = req.body;
    if (!phone || !message) {
        return res.status(400).json({ error: 'Field phone dan message wajib diisi' });
    }

    const jid = formatPhone(phone);

    try {
        let msgPayload = { text: message };

        if (logo_url) {
            // Kirim sebagai image message — thumbnail besar, upload ke WA CDN
            console.log('[image] Sending with logo:', logo_url);
            msgPayload = {
                image: { url: logo_url },
                caption: message,
            };
        } else if (receipt_url) {
            // Fallback: compact link preview card
            try {
                console.log('[preview] Fetching:', receipt_url);
                const urlInfo = await getUrlInfo(receipt_url, {
                    thumbnailWidth: 300,
                    timeoutMs: 10000,
                });
                console.log('[preview] title:', urlInfo?.title);
                console.log('[preview] jpegThumbnail size:', urlInfo?.jpegThumbnail?.length ?? 0);
                if (urlInfo) {
                    msgPayload = {
                        text: message,
                        linkPreview: urlInfo,
                    };
                }
            } catch (e) {
                console.error('[preview] Error:', e.message);
            }
        }

        await sock.sendMessage(jid, msgPayload);
        res.json({ success: true });
    } catch (err) {
        console.error('Gagal kirim pesan:', err.message);
        res.status(500).json({ error: err.message });
    }
});

connectToWhatsApp();

app.listen(PORT, () => {
    console.log(`Baileys server berjalan di port ${PORT}`);
    console.log(`Scan QR: GET http://localhost:${PORT}/qr`);
});
