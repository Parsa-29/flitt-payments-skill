# Flitt Payment Redirect Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/order-parameters/
- https://docs.flitt.com/api/create-order/
- https://docs.flitt.com/api/order-status/

Use this reference for the Payment (redirect) API section: accept purchase parameters, hosted checkout URL creation, browser form redirect, embedded checkout token creation, and order status polling.

## Required Purchase Parameters

Minimum signed purchase request fields:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | yes | Merchant-generated order ID. |
| `merchant_id` | integer | yes | Flitt merchant ID. |
| `order_desc` | string | yes | Merchant order description, always UTF-8. |
| `amount` | integer | yes | Amount without decimal separator, usually minor units. |
| `currency` | string | yes | ISO-like 3-letter currency code, for example `GEL`. |
| `signature` | string | yes | SHA1 request signature. |

Common optional fields:

| Parameter | Notes |
| --- | --- |
| `version` | Protocol version. Default is `1.0.1`; version `1.0` is deprecated. |
| `response_url` | Customer return URL after payment completion. |
| `server_callback_url` | Server-to-server callback URL after payment completion. Prefer this for reliable status updates. |
| `lifetime` | Order lifetime in seconds. Default `36000`; maximum `69120000`. |
| `merchant_data` | Arbitrary data returned in `response_url`, `server_callback_url`, and reports. |
| `preauth` | `N` charges immediately; `Y` holds funds for later capture. Default `N`. Visa/MasterCard only. |
| `delayed` | `Y` lets customer retry same `order_id` during lifetime; `N` sends one callback after decline. Default `Y`. |
| `lang` | Checkout language, such as `en`, `ka`, `uk`, `ru`, `de`, `fr`, `es`. |
| `product_id` | Merchant product/service ID. |
| `required_rectoken` | `Y` requests card token in response; default `N`. |
| `verification` | `Y` automatically reverses after successful approval; default `N`. |
| `rectoken` | Card token for recurring transactions. |
| `design_id` | Checkout design ID configured in merchant portal. |
| `subscription` | `Y` enables scheduled payments. |
| `subscription_callback_url` | Callback URL for scheduled payment completion. |
| `chargeback_callback_url` | Chargeback callback URL. |
| `cancel_url` | URL used when customer clicks Cancel on checkout. |
| `reservation_data` | Base64-encoded JSON for additional data. |

## Create Order Endpoints

### Hosted Checkout URL

Use for backend-created hosted checkout:

```text
POST https://pay.flitt.com/api/checkout/url
Content-Type: application/json
```

Request body:

```json
{
  "request": {
    "server_callback_url": "https://example.com/api/flitt/callback",
    "response_url": "https://example.com/payment-result",
    "order_id": "order_123",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test payment",
    "amount": 1000,
    "signature": "..."
  }
}
```

Normal response contains `response.checkout_url`; redirect the customer there:

```json
{
  "response": {
    "response_status": "success",
    "checkout_url": "https://pay.flitt.com/merchants/.../index.html?token=..."
  }
}
```

Some successful responses can also include `payment_id`; store it when present.

### Hosted Checkout Redirect

Use for direct browser form POST:

```text
POST https://pay.flitt.com/api/checkout/redirect
Content-Type: application/x-www-form-urlencoded or multipart form submission
```

HTML form fields are the same signed purchase parameters, but without the JSON root envelope:

```html
<form method="POST" action="https://pay.flitt.com/api/checkout/redirect">
  <input name="order_id" value="order_123">
  <input name="merchant_id" value="1549901">
  <input name="order_desc" value="Test order">
  <input name="amount" value="1000">
  <input name="currency" value="GEL">
  <input name="response_url" value="https://example.com/payment-result">
  <input name="server_callback_url" value="https://example.com/api/flitt/callback">
  <input name="signature" value="...">
  <button type="submit">Pay</button>
</form>
```

Normal response is HTTP `302 Found` with `Location` pointing to the Flitt checkout page. Error responses are HTML content containing request ID, a 4-digit `2XXX` error code, and localized description.

### Embedded Checkout Token

Use for mobile apps, Apple Pay, Google Pay, mobile card form, or JavaScript SDK integrations:

```text
POST https://pay.flitt.com/api/checkout/token
Content-Type: application/json
```

Request parameters are similar to `/api/checkout/url`. Normal response contains `response.token`.

## Get Order Status

Use status polling when callback delivery is delayed, customer return is unreliable, or the order remains in `created` / `processing`.

Endpoint:

```text
POST https://pay.flitt.com/api/status/order_id
Content-Type: application/json
```

Request parameters:

| Parameter | Required | Notes |
| --- | --- | --- |
| `order_id` | yes | Merchant-generated order ID. |
| `merchant_id` | yes | Flitt merchant ID. |
| `signature` | yes | Signature over status request parameters. |
| `version` | no | Default `1.0.1`. |

Example:

```json
{
  "request": {
    "order_id": "order_123",
    "version": "1.0.1",
    "merchant_id": 1549901,
    "signature": "..."
  }
}
```

Normal response contains the same response parameters as an accept-purchase response.

## Important Response Fields

| Field | Meaning |
| --- | --- |
| `response_status` | API request processing status: `success` or `failure`. Not the payment result. |
| `order_status` | Payment/order state: `created`, `processing`, `declined`, `approved`, `expired`, `reversed`. |
| `payment_id` | Unique Flitt payment ID. Store it when available. |
| `response_code` / `response_description` | Decline code and description. |
| `actual_amount` / `actual_currency` | Amount/currency actually authorized or charged. |
| `reversal_amount` | Total reversed amount for current order. |
| `additional_info` | JSON string with bank/card/capture/payment-method metadata. Parse as JSON when needed. |
| `signature` | Response signature to verify before trusting callback/status result data. |

Order status meanings:

| `order_status` | Meaning |
| --- | --- |
| `created` | Order exists but customer has not entered payment details; keep polling or wait for callback. |
| `processing` | Gateway is still processing; continue polling or wait for callback. |
| `declined` | Payment was declined by gateway, bank, or external payment system. |
| `approved` | Payment completed successfully; merchant can provide service or ship goods. |
| `expired` | Order lifetime expired. |
| `reversed` | Approved transaction was fully reversed; `reversal_amount` equals `actual_amount`. |

## Implementation Checklist

- Generate `order_id` server-side and persist the local order before calling Flitt.
- Sign only non-empty request parameters, excluding `signature`.
- For `/api/checkout/url` and `/api/status/order_id`, wrap parameters in root `request`.
- For `/api/checkout/redirect`, submit signed form fields directly.
- Include `server_callback_url` where possible and verify callback signatures.
- Use `response_url` for user-facing result display, not as the only status source.
- Poll `/api/status/order_id` for unresolved `created` or `processing` orders.
- Treat `response_status=failure` as request validation/API failure and inspect `error_code` / `error_message`.
