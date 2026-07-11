// upi_qr.js - handles the UPI ID safety checker

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('upiCheckBtn');
  const upiInput = document.getElementById('upiInput');
  const loadingState = document.getElementById('upiLoadingState');
  const resultBox = document.getElementById('upiResultBox');
  const resultBadge = document.getElementById('upiResultBadge');
  const reasonsList = document.getElementById('upiReasonsList');
  const tipsList = document.getElementById('upiTipsList');

  btn.addEventListener('click', async () => {
    const upiId = upiInput.value.trim();
    if (!upiId) {
      alert('Please enter a UPI ID.');
      return;
    }

    resultBox.classList.add('hidden');
    loadingState.classList.remove('hidden');
    btn.disabled = true;

    try {
      const res = await fetch('/api/check-upi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ upi_id: upiId }),
      });
      const data = await res.json();

      if (!res.ok) {
        alert(data.error || 'Something went wrong.');
        return;
      }

      renderVerdict({
        badgeEl: resultBadge,
        confidenceEl: null,
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
