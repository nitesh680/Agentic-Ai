const sendBtn = document.getElementById('send');
const input = document.getElementById('input');
const responseEl = document.getElementById('response');

sendBtn.addEventListener('click', async () => {
  const prompt = input.value.trim();
  if (!prompt) { alert('Please type a prompt'); return; }
  responseEl.textContent = 'Loading...';

  try {
    const res = await fetch('http://localhost:8000/api/agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const data = await res.json();

    // show nicely formatted response
    responseEl.textContent = data.answer || JSON.stringify(data, null, 2);
  } catch (err) {
    responseEl.textContent = 'Error: ' + err.message;
  }
});
