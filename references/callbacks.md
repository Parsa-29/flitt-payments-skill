# Flitt Callbacks Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/api/callbacks/

Use this reference for Flitt server callbacks/webhooks: endpoint behavior, retries, firewall allowlists, and payload verification.

## Delivery Contract

Flitt callback requests have these documented properties:

- Method: `POST`
- Content-Type: `application/json; charset=UTF-8`
- Timeout: `30` seconds
- Redirect following: `NO`

The docs show this callback `User-Agent`:

```text
Mozilla/5.0 (X11; Linux x86_64; Twisted) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36
```

Treat the user-agent as informational, not as a hard authentication mechanism.

## Firewall Allowlists

To receive Flitt callbacks, allow these source IP addresses in the merchant firewall:

- `54.154.216.60`
- `3.75.125.89`

Do not rely on IP allowlisting alone. Still verify callback signatures.

## Success And Retry Rules

Flitt considers a callback successfully processed only if the merchant returns HTTP `200 OK`.

If the callback is not processed successfully, Flitt retries with these intervals in seconds:

- `2`
- `60`
- `300`
- `600`
- `3600`
- `86400`

Practical implications:

- Do not return redirects.
- Do not perform slow synchronous work that risks exceeding the 30-second timeout.
- Prefer: verify signature, persist/idempotently enqueue the event, return `200`, then do downstream processing asynchronously.

## Payload Shape

Example callback fields from the docs include:

- `order_id`
- `payment_id`
- `merchant_id`
- `response_status`
- `order_status`
- `tran_type`
- `amount`
- `actual_amount`
- `currency`
- `actual_currency`
- `response_code`
- `response_description`
- `signature`
- `merchant_data`
- `rectoken`
- `reversal_amount`
- `additional_info`
- `response_signature_string`

Example callback body shape:

```json
{
  "order_id": "test33694502191",
  "payment_id": 805243692,
  "merchant_id": 1549901,
  "tran_type": "purchase",
  "response_status": "success",
  "order_status": "approved",
  "amount": "200",
  "actual_amount": "200",
  "currency": "GEL",
  "actual_currency": "GEL",
  "reversal_amount": "0",
  "signature": "...",
  "merchant_data": "Test merchant data",
  "additional_info": "{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": \"{}\", \"transaction_id\": 1994930931, \"payment_method\": \"card\", \"version_3ds\": 1, \"is_test\": true}"
}
```

Unlike some Flitt API responses, the callback example is shown as a flat JSON object rather than nested under `response`.

## Signature Verification

Verify callback signatures with the same merchant payment secret key used for the related environment.

Verification rules already used elsewhere in this skill still apply:

- Exclude `signature`
- Exclude `response_signature_string`
- Omit empty/null values
- Sort keys alphabetically
- Join values with `|`
- SHA1 hash the UTF-8 bytes

The `response_signature_string` field is diagnostic only. Do not include it in signature verification.

The bundled helper can verify flat callback payloads:

```bash
python3 ~/.codex/skills/flitt-payments/scripts/flitt_signature.py \
  --secret "$FLITT_PAYMENT_KEY" \
  --params-file callback.json \
  --verify "$FLITT_CALLBACK_SIGNATURE"
```

## Idempotent Processing

Process callbacks idempotently.

Recommended idempotency keys:

- `order_id`
- `payment_id`
- operation-specific identifiers when present

Because Flitt retries failed deliveries, the same callback can arrive more than once. Duplicate delivery should not create duplicate state transitions, duplicate shipments, duplicate credits, or duplicate emails.

## Parsing Additional Fields

`additional_info` is a JSON string. Parse it as JSON when the integration needs:

- `capture_status`
- `capture_amount`
- `reservation_data`
- `transaction_id`
- bank response details
- card metadata
- `payment_method`
- 3DS version
- `is_test`

Treat missing or null values as normal. The callback example includes many nullable fields.

## Implementation Checklist

- Expose a direct HTTPS endpoint for `server_callback_url`.
- Allow Flitt source IPs at the network layer if a firewall is present.
- Do not redirect callback requests.
- Verify the callback signature before trusting status changes.
- Parse `additional_info` JSON when needed.
- Store enough identifiers to deduplicate retries.
- Return HTTP `200 OK` only after the callback is accepted by local processing.
- Move slow or side-effect-heavy work off the request path.
