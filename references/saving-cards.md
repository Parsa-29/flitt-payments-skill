# Flitt Saving Cards Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/getting-started/recurring/

Use this reference when the task is about obtaining a Flitt saved-card token (`rectoken`) before later charging it with `/api/recurring`.

## Scope

Flitt describes saved-card payments as a 2-step recurring-payment flow:

1. Save card and obtain `rectoken`
2. Execute recurring payment without customer participation

This reference covers step 1. For step 2, use [payment-saved-card.md](/Users/khvichaparsadanashvili/.codex/skills/flitt-payments/references/payment-saved-card.md).

`rectoken` is a token that references card data securely stored on the payment-gateway side.

## Obtain Rectoken

To receive a token, send `required_rectoken=Y` during the create-order request.

Flitt documents two supported options.

### Option 1: Card Verification Flow

Use this when the merchant wants to save the card before the first real charge.

Send:

- `required_rectoken=Y`
- `verification=Y`
- a small `amount`, for example `100`

Documented behavior:

- the amount is held on the card
- the amount is reversed
- `rectoken` is returned in the response to `response_url`
- `rectoken` is also returned in the callback to `server_callback_url`

This is the better choice when the product needs to vault a card before later unscheduled billing.

### Option 2: First Purchase Flow

Use this when the first real purchase should also save the card for later reuse.

Send:

- `required_rectoken=Y`
- the actual purchase `amount`

Documented behavior:

- the actual purchase amount is charged
- `rectoken` is returned in the response to `response_url`
- `rectoken` is also returned in the callback to `server_callback_url`

This is the better choice when the user is already making a live purchase and you want to avoid a separate tokenization step.

## Response Handling

Token return is documented on:

- `response_url`
- `server_callback_url`

Practical guidance:

- prefer `server_callback_url` as the reliable system-of-record path
- verify the callback/response signature before trusting `rectoken`
- store `rectoken` only after the related payment/verification result is accepted
- treat `rectoken` as sensitive tokenized payment data and redact it in logs

## Integration Notes

- Token acquisition happens during the create-order flow, not through `/api/recurring`.
- A saved-card token flow and a saved-card charge flow are separate concerns; do not mix their parameter expectations.
- If the product needs a no-customer later charge, first obtain `rectoken`, then use `/api/recurring`.
- Verification-based tokenization is useful when the merchant wants to save a card without completing a real sale.

## Implementation Checklist

- Decide whether to save the card during verification or during the first real purchase.
- Add `required_rectoken=Y` to the create-order request.
- If using verification flow, also set `verification=Y` and use a small amount.
- Implement both `response_url` and `server_callback_url` handling for token return.
- Verify signatures before persisting `rectoken`.
- Store `rectoken` with the customer/payment-method record, not just the order.
- Use [payment-saved-card.md](/Users/khvichaparsadanashvili/.codex/skills/flitt-payments/references/payment-saved-card.md) for the later `/api/recurring` charge.
