const form = document.getElementById('post-form');
const status = document.getElementById('download-status');
const dateInput = form.elements.date;

const todayParts = new Intl.DateTimeFormat('en-US', {
  timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit'
}).formatToParts(new Date());
const today = Object.fromEntries(todayParts.map(({type, value}) => [type, value]));
dateInput.value = `${today.year}-${today.month}-${today.day}`;

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;

  const title = form.elements.title.value.trim();
  const category = form.elements.category.value.trim();
  const body = form.elements.body.value.trim().replace(/\r\n?/g, '\n');
  const date = dateInput.value;
  if (!title || !category || !body || !/^\d{4}-\d{2}-\d{2}$/.test(date)) return;

  const description = form.elements.description.value.trim() || body.replace(/\s+/g, ' ').slice(0, 110);
  const slug = title.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 45) || 'story';
  const filename = `${date}-${slug}-${Date.now().toString(36)}.md`;
  const content = `---\nlayout: post\ntitle: ${JSON.stringify(title)}\ndate: ${date}\ncategory: ${JSON.stringify(category)}\ndescription: ${JSON.stringify(description)}\n---\n\n${body}\n`;
  const url = URL.createObjectURL(new Blob([content], {type: 'text/markdown;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  status.textContent = `${filename} 파일을 내려받았습니다. 아래 버튼으로 GitHub에 올려 주세요.`;
});
