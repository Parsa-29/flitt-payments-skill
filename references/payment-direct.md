# Flitt Payment Direct Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/order-parameters-direct/
- https://docs.flitt.com/api/create-order-direct/

Use this reference for Payment (direct): PCI DSS merchant card-data collection, direct purchase request parameters, direct 3DS step 1, and direct 3DS step 2.

## Scope And Safety

Payment (direct) is for PCI DSS-compliant merchants when card data is collected on behalf of the merchant site or application.

Use hosted checkout or tokenized SDK flows unless direct card collection is explicitly required and the merchant accepts PCI scope.

Implementation guardrails:

- Do not collect card data in frontend or backend code unless the project is designed for PCI DSS compliance.
- Do not log `card_number`, `cvv2`, `expiry_date`, `cavv`, `pareq`, or `pares`.
- Do not persist raw PAN or CVV.
- Redact card fields in errors, analytics, tracing, and request dumps.
- Keep all direct payment requests server-side over HTTPS.

## Direct Purchase Parameters

Minimum signed direct purchase fields:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | yes | Merchant-generated order ID. |
| `merchant_id` | integer | yes | Flitt merchant ID. |
| `order_desc` | string | yes | Merchant order description, always UTF-8. |
| `amount` | integer | yes | Amount without decimal separator; `1020` GEL means 10 lari and 20 tetri. |
| `currency` | string | yes | Currency code, for example `GEL`, `USD`, `EUR`, `GBP`, `CZK`, `UZS`. |
| `signature` | string | yes | SHA1 request signature. |

Card and authentication fields:

| Parameter | Notes |
| --- | --- |
| `card_number` | Payer card number. |
| `cvv2` | Card CVV2/CVC2 code. |
| `expiry_date` | Card expiry date in `MMYY` format. |
| `client_ip` | Customer IP address. |
| `cavv` | Card 3DS authentication result CAVV value. |
| `eci` | Card 3DS authentication result ECI value. |
| `wallet` | Wallet type: `applepay` or `googlepay`. |
| `schemeid` | CIT identifier returned in initial purchase under `additional_info.schemeid`. |

Common optional purchase fields:

| Parameter | Notes |
| --- | --- |
| `version` | Protocol version. Default `1.0.1`; version `1.0` is deprecated. |
| `server_callback_url` | Server-to-server callback URL after payment completion. |
| `lifetime` | Order lifetime in seconds. Default `36000`; maximum `69120000`. |
| `merchant_data` | Arbitrary data returned in callbacks and reports. |
| `preauth` | `N` charges immediately; `Y` authorizes for later capture. Default `N`. Visa/MasterCard only. |
| `sender_email` | Customer email. |
| `delayed` | `Y` allows retrying same `order_id` during lifetime; default `Y`. |
| `lang` | Payment page language for pages involved in auth, such as `en`, `ka`, `uk`, `ru`, `de`. |
| `product_id` | Merchant product or service ID. |
| `required_rectoken` | `Y` requests a card token in response; default `N`. |
| `verification` | `Y` reverses automatically after successful approval; default `N`. |
| `rectoken` | Card token for recurring transactions. |

Example direct request body:

```json
{
  "request": {
    "order_id": "test_12343242",
    "merchant_id": 1549901,
    "order_desc": "Test order",
    "amount": 1000,
    "currency": "GEL",
    "card_number": "4444555566661111",
    "cvv2": "111",
    "expiry_date": "1125",
    "client_ip": "8.8.8.8",
    "server_callback_url": "https://example.com/api/flitt/callback",
    "signature": "..."
  }
}
```

## Create Direct Order Flow

Flitt documents direct order creation as a two-step flow for PCI DSS merchants.

### Step 1: Start 3DS Authentication

Endpoint:

```text
POST https://pay.flitt.com/api/3dsecure_step1
Content-Type: application/json
```

Send signed direct purchase parameters inside root `request`.

If the card is enrolled in 3DS, response contains:

| Field | Meaning |
| --- | --- |
| `response_status` | Usually `success` when the step is accepted. |
| `acs_url` | Issuer Access Control Server URL where cardholder authenticates. |
| `pareq` | Value to submit to ACS as `PaReq`. |
| `md` | Flitt-generated unique 3DS request ID. |

Build and submit an HTML form to the issuer ACS:

```html
<form name="MPIform" action="${acs_url}" method="POST">
  <input type="hidden" name="PaReq" value="${pareq}">
  <input type="hidden" name="MD" value="${md}">
  <input type="hidden" name="TermUrl" value="${term_url}">
</form>
```

`TermUrl` is the merchant URL where the customer returns after issuer authentication.

After authentication, the issuer returns these values to `TermUrl`:

| Field | Meaning |
| --- | --- |
| `pares` | Base64 payer authentication result. |
| `md` | Flitt-generated 3DS request ID. |

If 3DS is disabled or not required, Flitt returns normal payment response parameters instead.

### Step 2: Complete 3DS And Purchase

Endpoint:

```text
POST https://pay.flitt.com/api/3dsecure_step2
Content-Type: application/json
```

Required parameters:

| Parameter | Required | Notes |
| --- | --- | --- |
| `merchant_id` | yes | Flitt merchant ID. |
| `order_id` | yes | Merchant-generated order ID. |
| `pares` | yes | Value returned by issuer to `TermUrl`. |
| `md` | yes | Flitt 3DS request ID returned by step 1 and issuer. |
| `signature` | yes | Signature over step 2 parameters. |
| `version` | no | Default `1.0`. |

Request body:

```json
{
  "request": {
    "order_id": "test_12343242",
    "merchant_id": 1549901,
    "pares": "...",
    "md": "2001876637",
    "signature": "..."
  }
}
```

Normal response uses the same payment response parameters as direct purchase response.

## Response Handling

Possible direct outcomes:

- Final payment response with `response_status=success` and `order_status` such as `approved` or `declined`.
- 3DS-required response from step 1 with `acs_url`, `pareq`, and `md`.
- Failure response with `response_status=failure`, `error_code`, `error_message`, and `request_id`.

Use the same response handling rules as redirect payments:

- Verify response/callback signatures before trusting final payment data.
- Treat `response_status` as API processing state, not payment success.
- Use `order_status=approved` as the successful payment result.
- Store `payment_id` when returned.
- Parse `additional_info` as JSON when card, capture, bank, or scheme data is needed.

## Implementation Checklist

- Confirm PCI DSS scope before implementing direct card collection.
- Keep card collection, signing, and Flitt calls on secure server paths.
- Redact sensitive card and 3DS values everywhere.
- Generate and persist `order_id` before step 1.
- Include `server_callback_url`.
- Sign step 1 parameters with the payment secret key.
- If step 1 returns `acs_url`, POST `PaReq`, `MD`, and `TermUrl` to ACS.
- Receive `pares` and `md` on `TermUrl`.
- Sign and send step 2 request.
- Verify callback or final response signatures and update order idempotently.
