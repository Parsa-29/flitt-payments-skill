# Flitt Payment With Saved Card Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/order-parameters-recurring/
- https://docs.flitt.com/api/create-order-recurring/

Use this reference for Payment with saved card: charging an existing `rectoken` with `/api/recurring`.

## Scope

Payment with saved card charges a previously saved card token (`rectoken`). This is a host-to-host JSON API flow.

Important Flitt constraints:

- Endpoint: `POST https://pay.flitt.com/api/recurring`
- Request format: JSON with root `request`
- Response is returned in the same host-to-host request
- Redirect is not available on this endpoint
- 3DSecure is not available on this endpoint
- If 3DSecure is required, use Payment (direct) specifications instead

Treat `rectoken` as sensitive tokenized payment data. Do not log it in full; redact it in traces, errors, and analytics.

## Request Parameters

Minimum signed saved-card charge fields:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | yes | Merchant-generated order ID. |
| `merchant_id` | integer | yes | Flitt merchant ID. |
| `order_desc` | string | yes | Merchant order description, always UTF-8. |
| `amount` | integer | yes | Amount without decimal separator; `1020` GEL means 10 lari and 20 tetri. |
| `currency` | string | yes | Currency code, for example `GEL`, `USD`, `EUR`, `GBP`, `CZK`, `UZS`. |
| `rectoken` | string | yes | Card token for recurring/saved-card transaction. |
| `signature` | string | yes | SHA1 request signature. |

Common optional fields:

| Parameter | Notes |
| --- | --- |
| `version` | Protocol version. Default `1.0.1`; version `1.0` is deprecated. |
| `cvv2` | Card CVV2/CVC2 code when required by the payment scenario. Do not store or log it. |
| `client_ip` | Customer IP address. |
| `server_callback_url` | Server-to-server callback URL after payment completion. |
| `lifetime` | Order lifetime in seconds. Default `36000`; maximum `69120000`. |
| `merchant_data` | Arbitrary data returned in callbacks and reports. |
| `preauth` | `N` charges immediately; `Y` authorizes for later capture. Default `N`. Visa/MasterCard only. |
| `sender_email` | Customer email. |
| `product_id` | Merchant product or service ID. |

## Create Saved-Card Order

Endpoint:

```text
POST https://pay.flitt.com/api/recurring
Content-Type: application/json
```

Request body:

```json
{
  "request": {
    "order_id": "test_recurring_payment123",
    "order_desc": "Debit by token transaction",
    "currency": "GEL",
    "amount": 4600,
    "rectoken": "REDACTED_RECTOKEN",
    "merchant_id": 1549901,
    "signature": "..."
  }
}
```

Normal response contains standard payment response parameters:

```json
{
  "response": {
    "response_status": "success",
    "order_status": "approved",
    "payment_id": 822895805,
    "rectoken": "REDACTED_RECTOKEN",
    "actual_amount": "4600",
    "currency": "GEL"
  }
}
```

Failure response contains `response_status=failure` with `error_code`, `error_message`, and `request_id`.

## Response Handling

Use the same final-payment rules as other Flitt payment flows:

- Verify response/callback signatures before trusting final payment data.
- Treat `response_status` as API request processing state, not payment approval.
- Treat `order_status=approved` as the successful payment result.
- Store `payment_id` when returned.
- Parse `additional_info` as JSON when bank/card/payment-method metadata is needed.
- Expect `rectoken` to be present in the response and redact it in logs.

Common response fields:

| Field | Meaning |
| --- | --- |
| `order_status` | Payment state such as `approved` or `declined`. |
| `payment_id` | Unique Flitt payment ID. |
| `rectoken` | Saved card token used for/returned by the transaction. |
| `actual_amount` / `actual_currency` | Amount/currency actually charged. |
| `response_code` / `response_description` | Decline code and description when declined. |
| `additional_info.schemeid` | Scheme/client-initiated transaction identifier when returned. |
| `response_signature_string` | Test-mode diagnostic only; exclude from signature verification. |

## Obtaining A Rectoken

This reference covers charging with an existing token. To obtain a token, use a flow that requests token return, such as:

- Payment (redirect) or embedded/tokenized checkout with `required_rectoken=Y`
- Payment (direct) where token return is enabled and PCI scope is intentional

Persist tokens using the project's secure storage conventions. Associate tokens with the customer/payment method record, not only with a single order.

## Implementation Checklist

- Confirm a valid `rectoken` exists before creating `/api/recurring` order.
- Generate and persist a new merchant `order_id` for each saved-card charge.
- Sign all non-empty request parameters, including `rectoken`, excluding `signature`.
- Send JSON under root `request`.
- Do not attempt redirect or 3DS on `/api/recurring`.
- Include `server_callback_url` when possible.
- Redact `rectoken` and `cvv2` from logs.
- Verify callback/final response signature and update order idempotently.
