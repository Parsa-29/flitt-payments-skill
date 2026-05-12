# Flitt Sending Request Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/payment-flow/
- https://docs.flitt.com/api/request/

## Hosted Payment Flow Options

Use hosted checkout for standard online card and payment-method collection. Flitt supports two main hosted checkout interaction schemes.

### Scheme A: Browser POST Redirect

Use when the merchant app can create and submit an HTML form from the customer browser.

Endpoint:

```text
https://pay.flitt.com/api/checkout/redirect/
```

Flow:

1. Customer fills cart in merchant app.
2. Merchant creates an HTML form with signed order parameters.
3. Customer submits the form.
4. Browser sends HTTPS `POST` to Flitt checkout redirect endpoint.
5. Flitt creates the order and displays the hosted payment page.
6. Customer enters payment details.
7. Flitt performs 3DS/SCA when required.
8. Flitt redirects customer back to merchant with payment result.
9. Flitt also sends a server-to-server HTTPS `POST` callback with payment result.

Implementation notes:

- The customer browser is involved in the initial request to Flitt.
- Do not put payment secret key or signature generation in frontend code. Generate the signed form server-side.
- Treat browser return as user-facing navigation, not the only source of truth.

### Scheme B: Host-To-Host Checkout URL

Use when the merchant backend should create the Flitt order first and receive a checkout URL before redirecting the customer.

Endpoint:

```text
https://pay.flitt.com/api/checkout/url/
```

Flow:

1. Customer fills cart in merchant app.
2. Merchant backend sends a signed JSON request to Flitt.
3. Flitt returns an interim response with `checkout_url`.
4. Merchant redirects customer to `checkout_url`.
5. Customer enters payment details on Flitt hosted payment page.
6. Flitt performs 3DS/SCA when required.
7. Flitt redirects customer back to merchant with payment result.
8. Flitt also sends a server-to-server HTTPS `POST` callback with payment result.

Implementation notes:

- Prefer this scheme for API-first backends because the secret key and signature generation stay server-side.
- Persist local order state before redirecting the customer.
- Store Flitt `payment_id` when returned.

## JSON Request And Response Envelope

Every JSON request contains root `request`:

```json
{
  "request": {
    "version": "1.0.1",
    "order_id": "test_order_id_132412412",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test order",
    "amount": 10025,
    "response_url": "https://example.com/thankyoupage",
    "server_callback_url": "https://example.com/api/callback",
    "signature": "..."
  }
}
```

Every JSON response contains root `response`:

```json
{
  "response": {
    "response_status": "success",
    "order_status": "approved",
    "payment_id": 805243692
  }
}
```

`response_status` only indicates request processing status. It does not mean the payment, reversal, or capture succeeded.

Use these fields for operation results:

| Operation | Result field |
| --- | --- |
| Payment/order | `order_status` |
| Reversal | `reversal_amount` has a non-zero value |
| Capture | `capture_status` |

## Callback Handling

Implement `server_callback_url` for reliable server-to-server payment status updates.

- Accept HTTPS `POST` callbacks.
- Verify callback signature with the payment secret key.
- Exclude `signature` and `response_signature_string` before verification.
- Treat callbacks idempotently by `order_id` and/or `payment_id`.
- Update local order state from verified callback data.
- Use `response_url` primarily for customer-facing result display.

## Request Checklist

- Use HTTPS `POST`.
- Generate signatures only on the server.
- Include root `request` for JSON API calls.
- Use root `response` when parsing JSON API responses.
- Persist merchant order before redirect.
- Configure both `response_url` and `server_callback_url` where the endpoint supports them.
- Verify callback signatures before trusting payment result data.
