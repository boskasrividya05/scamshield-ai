// detect.js - handles the SMS/Email/URL fraud detector page

document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const inputText = document.getElementById('inputText');
  const loadingState = document.getElementById('loadingState');
  const resultBox = document.getElementById('resultBox');
  const resultBadge = document.getElementById('resultBadge');
  const resultConfidence = document.getElementById('resultConfidence');
  const reasonsList = document.getElementById('reasonsList');
  const tipsList = document.getElementById('tipsList');
  const digitalArrestAlert = document.getElementById('digitalArrestAlert');

  analyzeBtn.addEventListener('click', async () => {
    const text = inputText.value.trim();
    if (!text) {
      alert('Please enter some text to analyze.');
      return;
    }

    const activeTab = document.querySelector('.tab-btn.active');
    const inputType = activeTab ? activeTab.dataset.type : 'sms';

    resultBox.classList.add('hidden');
    loadingState.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
      const res = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_type: inputType, text }),
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

      digitalArrestAlert.classList.toggle('hidden', !data.is_digital_arrest);
      resultBox.classList.remove('hidden');
    } catch (err) {
      alert('Network error. Please try again.');
    } finally {
      loadingState.classList.add('hidden');
      analyzeBtn.disabled = false;
    }
  });
});
