// main.js - shared UI behaviors across all pages

document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll('.flash').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // Detect page tabs (SMS / Email / URL)
  const tabButtons = document.querySelectorAll('.tab-btn');
  const inputText = document.getElementById('inputText');
  if (tabButtons.length && inputText) {
    tabButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        tabButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const type = btn.dataset.type;
        const placeholders = {
          sms: 'Paste the SMS content here...',
          email: 'Paste the email body here...',
          url: 'Paste the website URL here (e.g. http://example.com)...',
        };
        inputText.placeholder = placeholders[type] || 'Paste content here...';
      });
    });
  }

  // Example buttons on detect page
  document.querySelectorAll('.example-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (inputText) {
        inputText.value = btn.dataset.text;
        inputText.focus();
      }
    });
  });
});

// Shared helper: render a Safe/Suspicious/Fraud result into a set of DOM nodes
function renderVerdict({ badgeEl, confidenceEl, reasonsListEl, tipsListEl, data }) {
  badgeEl.textContent = data.prediction.toUpperCase();
  badgeEl.className = 'badge badge-' + data.prediction;

  if (confidenceEl) {
    confidenceEl.textContent = data.confidence + '% confidence';
  }

  if (reasonsListEl) {
    reasonsListEl.innerHTML = '';
    data.reasons.forEach((r) => {
      const li = document.createElement('li');
      li.textContent = r;
      reasonsListEl.appendChild(li);
    });
  }

  if (tipsListEl) {
    tipsListEl.innerHTML = '';
    data.tips.forEach((t) => {
      const li = document.createElement('li');
      li.textContent = t;
      tipsListEl.appendChild(li);
    });
  }
}
