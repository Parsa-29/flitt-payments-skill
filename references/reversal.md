# Flitt Reversal Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/reversal-parameters/
- https://docs.flitt.com/api/create-reversal/
- https://docs.flitt.com/api/get-reversal-status/

Use this reference for reversal/refund workflows: create full or partial reversals, use idempotent `reverse_id`, and check reversal status through order status.

## Scope

Reversal can be full or partial.

- Full reversal: send `amount` equal to the order `actual_amount`.
- Partial reversal: send an `amount` less than the order `actual_amount`.
- Multiple partial reversals are allowed while their sum is less than or equal to `actual_amount`.
- Reversal status is checked through the normal order status endpoint; `reversal_amount` accumulates successful reversals for the order.

## Create Reversal

Endpoint:

```text
POST https://pay.flitt.com/api/reverse/order_id
Content-Type: application/json
```

Required request parameters:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | yes | Merchant-generated order ID of the original order. |
| `merchant_id` | integer | yes | Flitt merchant ID. |
| `amount` | integer | yes | Reversal amount without decimal separator. For full reversal, equal original `actual_amount`. |
| `currency` | string | yes | Original order currency, for example `GEL`, `USD`, `EUR`, `GBP`, `CZK`, `UZS`. |
| `signature` | string | yes | SHA1 request signature. |

Optional request parameters:

| Parameter | Notes |
| --- | --- |
| `version` | Protocol version. Default `1.0.1`; version `1.0` is deprecated. |
| `email` | Merchant staff email that initiated the reversal. |
| `comment` | UTF-8 merchant comment with reversal reason. |
| `reverse_id` | Idempotent reversal key for safe refund retries. Use especially for partial reversals. |

Example request:

```json
{
  "request": {
    "order_id": "test_12343242111",
    "currency": "GEL",
    "amount": "1",
    "merchant_id": "1549901",
    "reverse_id": "refund_test_12343242111_001",
    "signature": "..."
  }
}
```

Normal response:

```json
{
  "response": {
    "reverse_status": "approved",
    "order_id": "test_12343242111",
    "response_description": "",
    "response_code": "",
    "merchant_id": 1549901,
    "response_status": "success",
    "signature": "...",
    "reverse_id": "refund_test_12343242111_001",
    "reversal_amount": "1",
    "transaction_id": "2011273408"
  }
}
```

Failure response contains `response_status=failure` with `error_code`, `error_message`, and `request_id`.

## Idempotent Reverse Key

Use `reverse_id` to make reversal retries safe.

For partial reversals, always generate and persist a stable `reverse_id` before sending the request. If a network or timeout failure happens, retry the same reversal amount with the same `reverse_id`; do not generate a new key for the same logical refund attempt.

Example:

- Original amount: `1000`
- Partial reversal request: `100`
- Retry after timeout: send `100` again with the same `reverse_id`
- Avoid duplicate refund: do not send the retry with a new `reverse_id`

Full reversal usually does not require `reverse_id`, but using one is still reasonable when the local system needs deterministic retry tracking.

## Reversal Response Fields

| Field | Meaning |
| --- | --- |
| `response_status` | API request processing status: `success` or `failure`. Not enough by itself to prove refund outcome. |
| `reverse_status` | Reversal operation status. `approved` indicates successful reversal processing. |
| `reversal_amount` | Amount reversed in the response context; in order status, accumulated successful reversals. |
| `reverse_id` | Idempotency key when supplied or returned. |
| `transaction_id` | Flitt transaction identifier for the reversal. |
| `response_code` / `response_description` | Decline/error details when reversal is not approved. |
| `signature` | Response signature to verify before trusting reversal result data. |

## Get Reversal Status

Flitt reversal status is obtained through order status:

```text
POST https://pay.flitt.com/api/status/order_id
Content-Type: application/json
```

Request body:

```json
{
  "request": {
    "order_id": "test_12343242111",
    "version": "1.0.1",
    "merchant_id": "1549901",
    "signature": "..."
  }
}
```

Interpret status using:

| Field | Meaning |
| --- | --- |
| `actual_amount` | Amount originally charged/authorized. |
| `reversal_amount` | Sum of all successfully processed reversals for the order. |

Rules:

- `reversal_amount = 0`: no successful reversals.
- `0 < reversal_amount < actual_amount`: partial reversal.
- `reversal_amount = actual_amount`: full reversal.

The order may still show `order_status=approved` after a partial reversal; use `reversal_amount` to determine refund progress.

## Implementation Checklist

- Load original order and confirm it has an approved or reversible payment state.
- Decide full vs partial reversal.
- For full reversal, use original `actual_amount`.
- For partial reversal, ensure total prior successful reversals plus new `amount` does not exceed `actual_amount`.
- Generate and persist `reverse_id` for partial reversals before calling Flitt.
- Sign all non-empty reversal request parameters, excluding `signature`.
- Send JSON under root `request`.
- Verify response signature before trusting `reverse_status`.
- Store `transaction_id`, `reverse_id`, `reverse_status`, and returned `reversal_amount`.
- Check accumulated status through `/api/status/order_id` when the result is uncertain.
