const fs = require('fs');
const path = require('path');

const srcDir = 'frontend/src';
const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.js') && f !== 'i18n.js');

files.forEach(file => {
  const content = fs.readFileSync(path.join(srcDir, file), 'utf8');
  const lines = content.split('\n');
  const viLines = [];
  lines.forEach((l, idx) => {
    const trimmed = l.trim();
    if (!trimmed.startsWith('//') && !trimmed.startsWith('*') && !trimmed.startsWith('/*')) {
      if (/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(l)) {
        viLines.push({ line: idx + 1, text: trimmed });
      }
    }
  });
  console.log(`=== ${file}: ${viLines.length} lines ===`);
  viLines.slice(0, 15).forEach(v => console.log(`  L${v.line}: ${v.text.substring(0, 90)}`));
});
