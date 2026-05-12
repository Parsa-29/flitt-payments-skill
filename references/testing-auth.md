# Flitt Testing And Auth Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/introduction/
- https://docs.flitt.com/api/testing/
- https://docs.flitt.com/api/building-signature/
- https://docs.flitt.com/api/request/

## Request Shape

Send API requests over HTTPS with `POST`.

JSON requests use a root `request` object:

```json
{
  "request": {
    "merchant_id": 1549901,
    "order_id": "test_order_123",
    "currency": "GEL",
    "amount": 100,
    "order_desc": "Test payment",
    "signature": "..."
  }
}
```

Responses use a root `response` object. `response_status=success` means the API request was processed; payment outcome is reported separately, usually in `order_status`.

## Test Merchant Data

Use only in sandbox/test mode:

| Purpose | Value |
| --- | --- |
| merchant_id | `1549901` |
| purchase secret key | `test` |
| payout secret key | `testcredit` |
| currency | Use one of Flitt's supported currencies, commonly `GEL` in examples. |

Do not send real customer or payment data with public test keys.

## Signature Algorithm

Build `signature` as:

1. Start with the merchant payment secret key.
2. Remove `signature`.
3. Remove `response_signature_string` when verifying test callbacks/responses.
4. Omit parameters whose value is empty string or null.
5. Sort remaining parameter keys alphabetically.
6. Convert values to strings, preserving numeric zero as `0`.
7. Join secret and values with `|`.
8. SHA1 hash the UTF-8 encoded string and use lowercase hex.

Example signature string:

```text
test|1000|GEL|1549901|Test payment|TestOrder2|http://myshop/callback/
```

Use `scripts/flitt_signature.py` to generate or verify signatures.

## Test Cards

Expiry date and CVV can be any value unless the row specifies an OTP.

| Card | Brand | 3DS | Expected result |
| --- | --- | --- | --- |
| `4444555566661111` | Visa | yes | approve |
| `4444111166665555` | Visa | yes | decline |
| `4444555511116666` | Visa | no | approve |
| `4444111155556666` | Visa | no | decline |
| `5555666644441111` | MasterCard | yes | approve |
| `6666444455551111` | MasterCard | yes | approve |
| `4444555566669999` | Visa | frictionless | approve |
| `4444666655559999` | Visa | challenge | approve |
| `4444999966665555` | Visa | frictionless | decline |
| `4444666699995555` | Visa | challenge | decline |
| `2222555566663333` | MasterCard | yes | decline |
| `4444777799991111` | Visa | managed by `reservation_data` | approve |
| `9860010099998881` | Humo | yes | approve |
| `8600202020202023` | UzCard | yes | approve |
| `9860010088889992` | Humo | OTP `111111` | approve |
| `8600202020202023` | UzCard | OTP `111111` | approve |

## Wallet And Open Banking Tests

Apple Pay on web: if the merchant is in test mode, Flitt converts a real Apple Wallet tokenized card into a test token.

Apple Pay in app: use Apple Pay sandbox setup and upload certificates in the Flitt Merchant Portal before testing with sandbox wallet cards.

Open Banking: set `payment_method` to `x` or select the Demo Bank icon on checkout. Testing is possible only with Demo Bank.

## Auth Debug Checklist

- Use the correct key for the operation: `test` for purchase signatures, `testcredit` for payouts.
- Do not include `signature` in the pre-hash parameter set.
- Do not include `response_signature_string` when verifying test responses.
- Omit empty/null fields entirely from the signature string.
- Preserve `0` values.
- Sort by parameter name, not by display order.
- Hash UTF-8 bytes.
- Compare lowercase SHA1 hex strings.
