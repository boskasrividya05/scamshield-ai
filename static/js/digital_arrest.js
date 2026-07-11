// digital_arrest.js - handles the Digital Arrest scam pattern checker

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('daAnalyzeBtn');
  const inputText = document.getElementById('daInputText');
  const loadingState = document.getElementById('daLoadingState');
  const resultBox = document.getElementById('daResultBox');
  const resultBadge = document.getElementById('daResultBadge');
  const resultConfidence = document.getElementById('daResultConfidence');
  const reasonsList = document.getElementById('daReasonsList');
  const tipsList = document.getElementById('daTipsList');

  btn.addEventListener('click', async () => {
    const text = inputText.value.trim();
    if (!text) {
      alert('Please paste the message or call transcript first.');
      return;
    }

    resultBox.classList.add('hidden');
    loadingState.classList.remove('hidden');
    btn.disabled = true;

    try {
      const res = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_type: 'sms', text }),
      });
      const data = await res.json();

      if (!res.ok) {
        alert(data.error || 'Something went wrong.');
        return;
      }

      renderVerdict({
        badgeEl: resultBadge,
        confidenceEl: resultConfidence,
        reasonsListEl: reasonsList,
        tipsListEl: tipsList,
        data,
      });

      resultBox.classList.remove('hidden');
    } catch (err) {
      alert('Network error. Please try again.');
    } finally {
      loadingState.classList.add('hidden');
      btn.disabled = false;
    }
  });
});
