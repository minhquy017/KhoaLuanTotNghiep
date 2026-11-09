const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');

const lines = html.split('\n');
const missing = [];

lines.forEach((line, idx) => {
  const trimmed = line.trim();
  if (trimmed.startsWith('<!--') || trimmed.startsWith('*') || trimmed.startsWith('//')) return;
  if (/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(line)) {
    if (!line.includes('data-i18n')) {
      missing.push({ line: idx + 1, content: trimmed });
    }
  }
});

console.log(`Remaining Vietnamese lines WITHOUT data-i18n: ${missing.length}`);
missing.forEach(m => console.log(`L${m.line}: ${m.content}`));
