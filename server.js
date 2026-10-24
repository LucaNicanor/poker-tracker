const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const MAX_BYTES = 50 * 1024 * 1024;
const SOURCES = new Set(['clubwpt-gold', 'gto-wizard']);
const EXTENSIONS = new Set(['.txt', '.csv', '.json', '.zip', '.png', '.jpg', '.jpeg', '.webp']);

function createApp(dataDir = path.join(__dirname, 'hands')) {
  const archiveDir = path.join(dataDir, 'archive');
  const indexPath = path.join(dataDir, 'index.json');
  fs.mkdirSync(archiveDir, { recursive: true });
  const readIndex = () => fs.existsSync(indexPath) ? JSON.parse(fs.readFileSync(indexPath, 'utf8')) : [];

  return http.createServer(async (req, res) => {
    const send = (status, data) => {
      res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
      res.end(JSON.stringify(data));
    };
    try {
      const url = new URL(req.url, 'http://127.0.0.1');
      if (req.method === 'GET' && ['/','/index.html'].includes(url.pathname)) {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'X-Content-Type-Options': 'nosniff' });
        return res.end(fs.readFileSync(path.join(__dirname, 'index.html')));
      }
      if (req.method === 'GET' && url.pathname === '/favicon.ico') {
        res.writeHead(204); return res.end();
      }
      if (req.method === 'GET' && url.pathname === '/api/health') return send(200, { status: 'ok', files: readIndex().length });
      if (req.method === 'GET' && url.pathname === '/api/files') {
        return send(200, { files: readIndex().map(({ storedName, ...item }) => item) });
      }
      if (req.method === 'GET' && /^\/api\/files\/[a-f0-9]{64}$/.test(url.pathname)) {
        const id = url.pathname.split('/').at(-1);
        const item = readIndex().find(row => row.id === id);
        if (!item) return send(404, { error: 'File not found.' });
        res.writeHead(200, { 'Content-Type': 'application/octet-stream', 'X-Content-Type-Options': 'nosniff', 'Content-Disposition': "attachment; filename*=UTF-8''" + encodeURIComponent(item.name) });
        return fs.createReadStream(path.join(archiveDir, item.storedName)).on('error', () => res.destroy()).pipe(res);
      }
      if (req.method !== 'POST' || url.pathname !== '/api/import') return send(404, { error: 'Not found.' });
      if (!req.headers['content-type']?.startsWith('application/json')) return send(415, { error: 'Use JSON upload format.' });
      if (req.headers.origin && req.headers.origin !== 'http://' + req.headers.host) return send(403, { error: 'Open the local inbox to import files.' });
      const chunks = []; let size = 0;
      for await (const chunk of req) {
        size += chunk.length;
        if (size > Math.ceil(MAX_BYTES * 4 / 3) + 65536) return send(413, { error: 'Files must be under 50 MB.' });
        chunks.push(chunk);
      }
      let input;
      try { input = JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { return send(400, { error: 'Invalid upload data.' }); }
      if (!input || typeof input !== 'object' || !SOURCES.has(input.source)) return send(400, { error: 'Choose ClubWPT Gold or GTO Wizard.' });
      if (typeof input.name !== 'string' || !input.name || input.name.length > 240) return send(400, { error: 'A valid file name is required.' });
      const name = path.basename(input.name.replaceAll('\\', '/')).replace(/[\x00-\x1f\x7f]/g, '');
      const extension = path.extname(name).toLowerCase();
      if (!EXTENSIONS.has(extension)) return send(400, { error: 'Use a history text file, CSV, JSON, ZIP, or image.' });
      if (typeof input.content !== 'string' || !input.content || input.content.length % 4 !== 0 || !/^[A-Za-z0-9+/]*={0,2}$/.test(input.content)) return send(400, { error: 'Invalid file content.' });
      const bytes = Buffer.from(input.content, 'base64');
      if (bytes.length > MAX_BYTES) return send(413, { error: 'Files must be under 50 MB.' });
      const id = crypto.createHash('sha256').update(input.source).update('\0').update(bytes).digest('hex');
      const rows = readIndex();
      if (rows.some(row => row.id === id)) return send(200, { duplicate: true, id });
      const storedName = id + extension;
      fs.writeFileSync(path.join(archiveDir, storedName), bytes, { flag: 'wx' });
      const item = { id, name, source: input.source, bytes: bytes.length, importedAt: new Date().toISOString(), storedName };
      rows.unshift(item);
      try {
        fs.writeFileSync(indexPath + '.tmp', JSON.stringify(rows, null, 2));
        fs.renameSync(indexPath + '.tmp', indexPath);
      } catch (error) {
        // Keep original bytes available even if updating the catalog fails.
        console.error('Catalog update failed:', error.message);
        return send(500, { error: 'File preserved, but the catalog could not be updated. Check the local server log before retrying.' });
      }
      const { storedName: _, ...publicItem } = item;
      return send(201, { duplicate: false, file: publicItem });
    } catch (error) {
      console.error('Inbox error:', error.message);
      if (!res.headersSent) send(500, { error: 'The local archive could not be read or updated. Check the server log.' });
      else res.destroy();
    }
  });
}

if (require.main === module) {
  const server = createApp();
  server.listen(process.env.PORT || 3316, '127.0.0.1', () => console.log('Hand history inbox: http://127.0.0.1:' + server.address().port));
}
module.exports = { createApp };
