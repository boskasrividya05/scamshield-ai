# ScamShield AI — API Documentation

Base URL (local): `http://127.0.0.1:5000`

All `/api/*` endpoints require an active login session (the browser session
cookie set at `/login`). They are intended to be called via `fetch()` from
the app's own frontend, but can be tested with any HTTP client that supports
cookies (e.g. Postman with "Login" run first, or `curl -c/-b` for the cookie jar).

---

## POST `/api/detect`

Classifies an SMS, email body, or website URL as **safe**, **suspicious**, or **fraud**.

### Request

```http
POST /api/detect
Content-Type: application/json
```

```json
{
  "input_type": "sms",
  "text": "URGENT: Your account will be blocked in 24 hours. Click here: http://kyc-verify-sbi.tk"
}
```

| Field | Type | Required | Values |
|---|---|---|---|
| `input_type` | string | Yes | `"sms"`, `"email"`, `"url"` |
| `text` | string | Yes | The message body or URL to analyze |

### Response `200 OK`

```json
{
  "prediction": "fraud",
  "confidence": 98.0,
  "reasons": [
    "Contains high-risk fraud keywords: kyc, blocked, urgent",
    "URL does not use secure HTTPS protocol.",
    "Uses a free/suspicious domain extension '.tk' often used by scammers."
  ],
  "tips": [
    "Do not click any links, share OTPs, or make any payments related to this message.",
    "Block and report the sender on your messaging app / email provider.",
    "Report the incident on the National Cyber Crime Reporting Portal: cybercrime.gov.in or call 1930."
  ],
  "is_digital_arrest": false,
  "input_type": "sms"
}
```

### Error `400 Bad Request`
```json
{ "error": "Please enter some text to analyze." }
```

Every successful call is automatically logged to the `scan_history` table
for the logged-in user, which powers the Dashboard.

---

## POST `/api/check-upi`

Validates a UPI ID's format and flags common fraud patterns.

### Request
```json
{ "upi_id": "winner.lottery@upi" }
```

### Response `200 OK`
```json
{
  "prediction": "fraud",
  "confidence": 80,
  "reasons": [
    "UPI ID / request references a lottery, prize or cashback - a major red flag."
  ],
  "tips": [
    "Do not scan QR codes received from unknown numbers promising cashback or prizes.",
    "Scanning a QR code and entering your UPI PIN can authorize a payment OUT of your account, not in."
  ],
  "is_digital_arrest": false,
  "input_type": "upi"
}
```

---

## GET `/api/dashboard-data`

Returns the count of Safe / Suspicious / Fraud scans for the currently
logged-in user (used to redraw the dashboard chart without a full page reload).

### Response `200 OK`
```json
{ "safe": 12, "suspicious": 4, "fraud": 7 }
```

---

## POST `/admin/update-status/<report_id>`

**Admin only.** Updates the status of a community scam report.

### Request (form-encoded, sent by the Admin Panel's dropdown)
```
status=resolved
```

### Response
`302 Redirect` back to `/admin` with a flash confirmation message.

---

## Authentication Notes

ScamShield AI uses Flask's signed session cookies (not token/JWT-based) for
simplicity, since this is a server-rendered app. There is no separate
`/api/login` JSON endpoint — authentication happens via the standard
`/login` HTML form, after which the session cookie authorizes all
subsequent `/api/*` calls.

| Route | Method | Auth |
|---|---|---|
| `/register` | GET, POST | Public |
| `/login` | GET, POST | Public |
| `/logout` | GET | Logged in |
| `/dashboard` | GET | Logged in |
| `/detect`, `/digital-arrest`, `/upi-qr`, `/report`, `/safety-tips` | GET | Logged in |
| `/admin` | GET | Admin only |
