const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createApp } = require('./server');

test('imports preserve original bytes, deduplicate, and survive a restart', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'poker-inbox-test-'));
  let server = createApp(dir);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let base = 'http://127.0.0.1:' + server.address().port;
  const post = input => fetch(base + '/api/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input) });
  try {
    const bytes = Buffer.from('A saved hand for setup verification.\r\n', 'utf8');
    const input = { name: 'session.txt', source: 'clubwpt-gold', content: bytes.toString('base64') };
    const first = await post(input); assert.equal(first.status, 201);
    const item = (await first.json()).file;
    const downloaded = Buffer.from(await (await fetch(base + '/api/files/' + item.id)).arrayBuffer());
    assert.deepEqual(downloaded, bytes);
    assert.equal((await (await post(input)).json()).duplicate, true);
    assert.equal((await (await fetch(base + '/api/files')).json()).files.length, 1);
    assert.equal((await post({ ...input, source: 'gto-wizard' })).status, 201);
    await new Promise(resolve => server.close(resolve));
    server = createApp(dir); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    base = 'http://127.0.0.1:' + server.address().port;
    assert.equal((await (await fetch(base + '/api/files')).json()).files.length, 2);
    assert.equal((await post({ ...input, name: '../../outside.txt', content: Buffer.from('another hand').toString('base64') })).status, 201);
    const rows = (await (await fetch(base + '/api/files')).json()).files;
    assert.equal(rows[0].name, 'outside.txt');
    assert.equal(fs.existsSync(path.join(dir, '..', 'outside.txt')), false);
    assert.equal((await post({ ...input, source: 'unknown' })).status, 400);
    assert.equal((await post({ ...input, name: 'script.exe' })).status, 400);
    assert.equal((await post({ ...input, content: 'not base64!' })).status, 400);
    const crossOrigin = await fetch(base + '/api/import', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://unrelated.example' }, body: JSON.stringify(input) });
    assert.equal(crossOrigin.status, 403);
  } finally {
    await new Promise(resolve => server.close(resolve));
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
