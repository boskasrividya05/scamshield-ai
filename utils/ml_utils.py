"""
utils/ml_utils.py
------------------
Wraps the trained ML model and adds an explainability layer so every
prediction comes with a human-readable "why" and prevention tips -
this is a core requirement of PS6 (AI for Digital Public Safety).

Design (beginner-friendly, explained in the report):
1. TEXT CLASSIFIER (SMS / Email / generic text)
   - TF-IDF + Logistic Regression predicts: safe / suspicious / fraud
   - A curated keyword dictionary is matched against the input to build
     the "explanation" shown to the user (which red-flag words/phrases
     were found) - this makes the AI's decision transparent.

2. URL CHECKER (rule-based, lightweight - no external API needed)
   - Looks for classic phishing indicators: IP-based URLs, suspicious
     TLDs (.tk/.ml/.ga/.cf/.xyz), URL shorteners, "-" heavy domains,
     brand-name + extra words (e.g. "sbi-kyc-update"), no HTTPS, etc.

3. DIGITAL ARREST SCAM DETECTOR
   - India-specific scam pattern where fraudsters impersonate
     police/CBI/customs/narcotics officers on video calls and coerce
     victims into transferring money under threat of arrest.
   - Detected via a dedicated keyword/pattern list layered on top of
     the general classifier, since this is a distinct, high-severity
     scam category called out explicitly in the problem statement.

4. UPI / QR AWARENESS CHECK
   - Validates UPI ID format and flags common fraud patterns
     (e.g. "collect request" scams, fake cashback QR codes).

All of this is intentionally simple and transparent (no black-box
deep learning) so a 2nd-year student can explain every line in a viva.
"""

import re
import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
VEC_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

_model = None
_vectorizer = None


def _load():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VEC_PATH)
    return _model, _vectorizer


# ---------------------------------------------------------------------------
# Keyword banks used purely for EXPLAINABILITY (not for the ML prediction
# itself). Keeping them separate from the model lets us show *why* something
# was flagged even though the ML model works on TF-IDF math internally.
# ---------------------------------------------------------------------------
FRAUD_KEYWORDS = [
    "lottery", "won", "winner", "prize", "claim your", "kyc", "aadhar", "aadhaar",
    "otp", "pan card", "blocked", "suspend", "urgent", "immediately", "customs",
    "parcel", "seized", "penalty", "refund", "cashback", "free iphone", "loan",
    "zero documents", "registration fee", "job offer", "earn rs", "bank details",
    "share your otp", "share otp", "transfer funds", "escrow", "legal action",
    "arrest", "cbi", "narcotics", "enforcement directorate", "money laundering",
    "video call", "digital arrest", "police", "cyber cell", "warrant",
]

SUSPICIOUS_KEYWORDS = [
    "verify your account", "confirm your identity", "unusual activity",
    "limited time offer", "click below", "update your details", "sign in",
    "new device", "renew now", "discount coupon", "subscription payment",
    "re-verification", "billing details",
]

DIGITAL_ARREST_KEYWORDS = [
    "digital arrest", "cbi officer", "narcotics", "money laundering case",
    "do not disconnect", "stay on video call", "video call with our officer",
    "under investigation", "enforcement directorate", "customs department",
    "arrest warrant", "do not tell", "do not tell anyone", "cyber cell",
    "trai", "sim card will be deactivated", "courier contains illegal",
]

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".xyz", ".info", ".top", ".gq"]
URL_SHORTENERS = ["bit.ly", "tinyurl", "cutt.ly", "is.gd", "t.co", "shorturl"]
TRUSTED_BRAND_WORDS = ["sbi", "hdfc", "icici", "paytm", "google", "amazon",
                        "netflix", "rbi", "uidai", "irctc", "whatsapp"]


def _contains_any(text_lower, keyword_list):
    return [kw for kw in keyword_list if kw in text_lower]


def classify_text(text: str):
    """
    Classifies free text (SMS / Email body) into safe / suspicious / fraud
    using the trained ML model, and builds an explanation + prevention tips.
    Returns a dict.
    """
    model, vectorizer = _load()
    text_clean = text.strip()
    text_lower = text_clean.lower()

    vec = vectorizer.transform([text_clean])
    proba = model.predict_proba(vec)[0]
    classes = model.classes_
    pred_idx = proba.argmax()
    prediction = classes[pred_idx]
    confidence = round(float(proba[pred_idx]) * 100, 2)

    matched_fraud = _contains_any(text_lower, FRAUD_KEYWORDS)
    matched_suspicious = _contains_any(text_lower, SUSPICIOUS_KEYWORDS)
    matched_digital_arrest = _contains_any(text_lower, DIGITAL_ARREST_KEYWORDS)

    is_digital_arrest = len(matched_digital_arrest) >= 2

    # Nudge the ML prediction with strong rule-based evidence for the
    # extremely high-severity Digital Arrest pattern (safety-critical override)
    if is_digital_arrest:
        prediction = "fraud"
        confidence = max(confidence, 97.0)

    reasons = []
    if matched_fraud:
        reasons.append(
            f"Contains high-risk fraud keywords: {', '.join(sorted(set(matched_fraud))[:6])}"
        )
    if matched_suspicious:
        reasons.append(
            f"Contains suspicious phrases commonly used in scams: {', '.join(sorted(set(matched_suspicious))[:6])}"
        )
    if is_digital_arrest:
        reasons.append(
            "Matches known 'Digital Arrest' scam pattern - impersonation of police/"
            "government officials to threaten and extort victims via video call."
        )
    if not reasons:
        reasons.append("No known fraud/scam keyword patterns detected in the text.")

    tips = _get_tips(prediction, is_digital_arrest)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "reasons": reasons,
        "tips": tips,
        "is_digital_arrest": is_digital_arrest,
        "input_type": "text",
    }


def classify_url(url: str):
    """
    Rule-based URL / website safety checker.
    Beginner-friendly & explainable: every rule that fires is shown to the user.
    """
    url_clean = url.strip()
    url_lower = url_clean.lower()
    score = 0
    reasons = []

    if not url_lower.startswith("https://"):
        score += 1
        reasons.append("URL does not use secure HTTPS protocol.")

    if re.search(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url_lower):
        score += 3
        reasons.append("URL uses a raw IP address instead of a domain name (classic phishing sign).")

    for tld in SUSPICIOUS_TLDS:
        if tld in url_lower:
            score += 2
            reasons.append(f"Uses a free/suspicious domain extension '{tld}' often used by scammers.")
            break

    for short in URL_SHORTENERS:
        if short in url_lower:
            score += 2
            reasons.append(f"Uses a URL shortener ('{short}') which can hide the real destination.")
            break

    if url_lower.count("-") >= 2:
        score += 1
        reasons.append("Domain contains multiple hyphens, often used to mimic real brand names.")

    for brand in TRUSTED_BRAND_WORDS:
        if brand in url_lower and not url_lower.startswith((f"https://{brand}.", f"https://www.{brand}.")):
            score += 2
            reasons.append(
                f"Mentions trusted brand '{brand.upper()}' but is not the brand's official domain - likely spoofed."
            )
            break

    if any(word in url_lower for word in ["kyc", "verify", "update", "claim", "prize", "refund", "win"]):
        score += 1
        reasons.append("URL path contains urgency/reward related words typical of phishing links.")

    if score >= 4:
        prediction = "fraud"
        confidence = min(95 + score, 99)
    elif score >= 2:
        prediction = "suspicious"
        confidence = 70 + score * 3
    else:
        prediction = "safe"
        confidence = 90
        reasons = ["No major phishing indicators detected in this URL."]

    tips = _get_tips(prediction, False)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "reasons": reasons,
        "tips": tips,
        "is_digital_arrest": False,
        "input_type": "url",
    }


def check_upi_id(upi_id: str):
    """
    Simple pattern-based UPI ID sanity checker for the
    'Fake UPI & QR Code Awareness' module.
    """
    upi = upi_id.strip().lower()
    reasons = []
    score = 0

    valid_format = bool(re.match(r"^[a-z0-9.\-_]{2,256}@[a-z]{2,64}$", upi))
    if not valid_format:
        score += 3
        reasons.append("This does not look like a valid UPI ID format (should be like name@bank).")

    suspicious_handles = ["okaxis", "oksbi", "paytm", "ybl", "ibl", "axl", "upi"]
    handle = upi.split("@")[-1] if "@" in upi else ""
    if valid_format and handle not in suspicious_handles and len(handle) < 3:
        score += 1
        reasons.append("UPI handle looks unusual or unrecognized.")

    if "lottery" in upi or "prize" in upi or "cashback" in upi or "gift" in upi:
        score += 3
        reasons.append("UPI ID / request references a lottery, prize or cashback - a major red flag.")

    if score >= 3:
        prediction = "fraud"
    elif score >= 1:
        prediction = "suspicious"
    else:
        prediction = "safe"
        reasons.append("UPI ID format looks valid. Always verify the receiver's name shown by your UPI app before paying.")

    return {
        "prediction": prediction,
        "confidence": 80,
        "reasons": reasons,
        "tips": _get_tips(prediction, False, upi_context=True),
        "is_digital_arrest": False,
        "input_type": "upi",
    }


def _get_tips(prediction, is_digital_arrest, upi_context=False):
    if is_digital_arrest:
        return [
            "Real police/CBI/government officials NEVER make arrests or demand money over a phone or video call.",
            "Do not panic, do not share OTP/bank details, and do not stay on the call under threat.",
            "Hang up immediately and verify by calling the official helpline (Cyber Crime Helpline: 1930).",
            "Never transfer money to 'safety' or 'escrow' accounts suggested by a caller.",
            "Inform a trusted family member or the nearest police station before taking any action.",
        ]

    if upi_context:
        if prediction == "safe":
            return [
                "Always check the recipient name shown by your UPI app before confirming payment.",
                "Never scan a QR code to RECEIVE money - QR/UPI collect requests are only for making payments.",
                "Do not share your UPI PIN with anyone, including bank staff or delivery agents.",
            ]
        return [
            "Do not scan QR codes received from unknown numbers promising cashback or prizes.",
            "Scanning a QR code and entering your UPI PIN can authorize a payment OUT of your account, not in.",
            "Verify UPI IDs directly with the concerned bank/company through official channels only.",
            "Report suspicious UPI requests on the NPCI website or via your bank's fraud helpline.",
        ]

    if prediction == "fraud":
        return [
            "Do not click any links, share OTPs, or make any payments related to this message.",
            "Block and report the sender on your messaging app / email provider.",
            "Report the incident on the National Cyber Crime Reporting Portal: cybercrime.gov.in or call 1930.",
            "Verify claims (bank, courier, tax refund, etc.) only via the official website or customer care number.",
        ]
    if prediction == "suspicious":
        return [
            "Do not click links directly - open the official app/website separately to check.",
            "Verify the sender's identity through an independent, official channel before acting.",
            "Watch for urgency and pressure tactics - legitimate organisations rarely demand instant action.",
        ]
    return [
        "This message looks safe, but always stay cautious with unexpected requests for personal information.",
        "Keep your OTP, PIN and passwords private under all circumstances.",
    ]
