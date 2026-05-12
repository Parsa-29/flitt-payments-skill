# Flitt Capture Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/capture-parameters/
- https://docs.flitt.com/api/create-capture/
- https://docs.flitt.com/api/get-capture-status/

Use this reference for capture workflows: completing a card preauthorization, partial capture, and checking capture status through order status.

## Scope

Capture charges an amount previously held on a card.

Important constraints:

- The original payment must be a pre-payment/preauthorization with `preauth=Y`.
- Preauth/capture is available only for card payment methods.
- Other payment methods do not support two-stage capture and are charged in a one-stage flow.
- Capture can be full or partial.
- Multiple captures are not allowed.
- A capture with the same `amount` can be retried safely; Flitt returns the current `capture_status`.

For full capture, send `amount` equal to the original order `actual_amount`. For partial capture, send a smaller amount. If a partial capture is performed, the rest of the held amount is automatically returned to the payer card; do not also reverse the remaining held amount.

## Create Capture

Endpoint:

```text
POST https://pay.flitt.com/api/capture/order_id
Content-Type: application/json
```

Required request parameters:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | yes | Merchant-generated order ID of the preauthorized order. |
| `merchant_id` | integer | yes | Flitt merchant ID. |
| `amount` | integer | yes | Capture amount without decimal separator. For full capture, equal original `actual_amount`. |
| `currency` | string | yes | Original order currency, for example `GEL`, `USD`, `EUR`, `GBP`, `CZK`, `UZS`. |
| `signature` | string | yes | SHA1 request signature. |

Optional request parameters:

| Parameter | Notes |
| --- | --- |
| `version` | Protocol version. Default `1.0.1`; version `1.0` is deprecated. |

Example request:

```json
{
  "request": {
    "version": "1.0.1",
    "order_id": "test_12343242113",
    "currency": "GEL",
    "merchant_id": 1549901,
    "amount": 100,
    "signature": "..."
  }
}
```

Normal response:

```json
{
  "response": {
    "capture_status": "captured",
    "order_id": "test_12343242113",
    "response_description": "",
    "response_code": "",
    "merchant_id": 1549901,
    "response_status": "success"
  }
}
```

Failure response contains `response_status=failure` with `error_code`, `error_message`, and `request_id`.

## Capture Status

Direct capture response contains `capture_status`:

| `capture_status` | Meaning |
| --- | --- |
| `hold` | Capture has been created but is not approved yet; continue checking order status. |
| `captured` | Capture completed successfully; funds are charged and merchant can provide service or ship goods. |

Capture status should also be checked through normal order status:

```text
POST https://pay.flitt.com/api/status/order_id
Content-Type: application/json
```

In the order status response, parse `response.additional_info` as JSON and inspect:

| Field | Meaning |
| --- | --- |
| `capture_status` | Capture state, for example `captured`. |
| `capture_amount` | Captured amount. If lower than `actual_amount`, the order was partially captured. |

Rules:

- `capture_amount = actual_amount`: full capture.
- `0 < capture_amount < actual_amount`: partial capture.
- Missing/null `capture_amount`: capture not completed or not applicable.

## Reverse Of Pre-Payment

Before capture is completed:

- Acquiring fee is not charged for pre-payment and reverse operations.
- Reversal instantly cancels the held amount.
- Only full reversal of the held amount is available; partial reverse is not allowed for pre-payment.

If only part of the held amount should be charged, perform a partial capture for the amount to charge. The rest is automatically returned. Do not reverse the difference after a partial capture.

Example:

- Held amount: `1000`
- Desired charge: `800`
- Correct action: capture `800`
- Do not additionally reverse `200`, because the remainder is returned automatically

After a payment is captured, several sequential partial reversals are available through the reversal flow.

## Implementation Checklist

- Confirm original payment was created with `preauth=Y`.
- Confirm payment method is card.
- Confirm capture has not already been completed; multiple captures are not allowed.
- Decide full vs partial capture.
- For full capture, use original `actual_amount`.
- For partial capture, use the amount to charge and let the rest return automatically.
- Sign all non-empty capture request parameters, excluding `signature`.
- Send JSON under root `request`.
- Verify response data and store `capture_status`.
- If result is uncertain or `hold`, poll `/api/status/order_id`.
- Parse `additional_info` JSON to read `capture_status` and `capture_amount`.
