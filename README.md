# flitt-payments — Claude Code & Cursor Skill

A skill for Claude Code and Cursor that provides complete Flitt payment API guidance: request signing, hosted checkout, direct card payments, saved-card charges, subscriptions, reversals, captures, callbacks, and response-code interpretation.

## Install

Works in **Claude Code** (`~/.claude/skills/`) and **Cursor** (`~/.cursor/skills/`) — the skill format is compatible with both editors.

**One-liner — Claude Code only**

```bash
git clone https://github.com/YOUR_USERNAME/flitt-payments-skill ~/.claude/skills/flitt-payments
```

**One-liner — Cursor only**

```bash
git clone https://github.com/YOUR_USERNAME/flitt-payments-skill ~/.cursor/skills/flitt-payments
```

**Both editors at once (recommended)**

```bash
git clone https://github.com/YOUR_USERNAME/flitt-payments-skill
cd flitt-payments-skill
./install.sh
```

Then restart Claude Code / Cursor (or open a new session).

## Usage

Invoke by mentioning Flitt in your prompt — Claude Code picks it up automatically — or trigger it explicitly:

```
/flitt-payments  integrate Flitt hosted checkout into this Next.js project
```

The skill covers:

| Area | What it gives you |
|---|---|
| Auth & testing | Sandbox credentials, test cards, SHA1 signature generation |
| Hosted checkout | Redirect form (Scheme A) and server-to-server URL (Scheme B) |
| Payment (redirect) | Full parameter reference, status polling |
| Payment (direct) | Raw card params, 3DS step1/step2 flow |
| Saved-card charges | `/api/recurring` params, rectoken handling |
| Card tokenisation | `required_rectoken`, verification-based save flow |
| Reversals / refunds | `/api/reverse/order_id`, partial and full |
| Captures | `/api/capture/order_id`, preauth workflow |
| Subscriptions | `recurring_data`, start/stop via `/api/subscription` |
| Additional data | `reservation_data`, custom fields, fiscalisation |
| Currencies | Merchant-country currency matrix |
| Callbacks | Webhook validation, idempotency, IP allowlist |
| Response codes | API and embedded-checkout JS error classification |

## Signature helper

```bash
python3 scripts/flitt_signature.py \
  --secret test \
  --params '{"merchant_id":1549901,"amount":1000,"currency":"GEL","order_desc":"Test","order_id":"order1"}'

# Verify a received signature
python3 scripts/flitt_signature.py \
  --secret "$FLITT_PAYMENT_KEY" \
  --params-file response.json \
  --verify "$FLITT_RESPONSE_SIGNATURE"
```

## Uninstall

```bash
rm -rf ~/.claude/skills/flitt-payments
rm -rf ~/.cursor/skills/flitt-payments
```

## Structure

```
flitt-payments/
├── SKILL.md                    # Skill definition (loaded by Claude Code)
├── install.sh                  # Install script
├── scripts/
│   └── flitt_signature.py      # SHA1 signature generator / verifier
└── references/
    ├── testing-auth.md
    ├── sending-request.md
    ├── payment-redirect.md
    ├── payment-direct.md
    ├── payment-saved-card.md
    ├── saving-cards.md
    ├── reversal.md
    ├── capture.md
    ├── subscriptions.md
    ├── additional-data.md
    ├── currencies.md
    ├── callbacks.md
    ├── signature.md
    └── response-codes.md
```
