# Flitt Response Codes Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/api/response-codes/

Use this reference when interpreting Flitt API `response_code` values or embedded-checkout JavaScript error codes.

## How To Read Flitt Failures

There are two layers of code in the docs:

- API response codes: numeric codes such as `1014`, `1024`, `1109`
- JavaScript response codes: embedded checkout/browser-side codes such as `2000` to `2005`

Do not treat all failures the same way. First classify the owner of the fix:

- merchant-side input/configuration problem
- issuing-bank/customer card problem
- Flitt/platform/acquirer problem

The docs include a "Where client can solve the problem" column. Use it as ownership guidance.

## High-Value API Codes

These are the codes most likely to matter during implementation and testing.

### Merchant request construction issues

| Code | Text | Practical meaning |
| --- | --- | --- |
| `1007` | Parameter `{param_name}` is incorrect | Wrong format, size, or invalid value in request. |
| `1009` | Parameter `{param_name}` is empty | Required field was sent empty. |
| `1010` | Request is empty | Request body missing or malformed. |
| `1011` | Parameter `{param_name}` is missing | Required field omitted. |
| `1012` | Currency not available for this merchant | `currency` not configured/allowed for merchant. |
| `1013` | Duplicate order `{order_id}` | `order_id` is not unique. |
| `1014` | Invalid signature | Signature generation is wrong. |
| `1021` | Unsupported Content-Type | Wrong `Content-Type` header. |
| `1023` | Invalid amount | `amount` is malformed or unsupported. |
| `1034` | Please do not use symbol `{separator}` in parameters | Request values contain forbidden separator characters. |
| `1046` | Request contains non utf-8 symbol | Request payload encoding is invalid. |

### Merchant flow/state issues

| Code | Text | Practical meaning |
| --- | --- | --- |
| `1019` | Order already has been completed | Attempt to pay or reuse an expired/completed order. |
| `1026` | Only redirect method allowed | Wrong integration protocol for merchant setup. |
| `1028` | Custom design not found | Referenced checkout design/config does not exist. |
| `1035` | Token not found | `rectoken` invalid, expired, or deactivated. |
| `1052` | Order has expired | Order lifetime elapsed. |
| `1054` | Session expired | Customer/session flow timed out. |
| `1072` | Recurring chain declined | Stored-card recurring chain rejected. |
| `1073` | 3DSecure is mandatory for Maestro cards | Merchant must use a 3DS-capable flow. |
| `1075` | 3DSecure is mandatory | Non-3DS flow is not allowed for this payment. |
| `1082` | Token has expired | Stored token expired. |
| `1084` | Only full refund allowed | Merchant attempted unsupported partial refund. |
| `1086` | Transaction already finished | Operation repeated against already-finalized transaction. |
| `1109` | Order already captured with different amount | Re-capture attempt after partial or different-amount capture. |
| `1114` | Settlement not allowed until order is captured | Preauth must be captured before downstream split/settlement operations. |

### Issuer/customer card declines

| Code | Text | Practical meaning |
| --- | --- | --- |
| `1003` | Invalid CVV2 code | CVV2 or sometimes expiry/card data is wrong. |
| `1004` | Do not honor | Issuer generic decline or internet-payments block. |
| `1015` | Invalid card number | PAN is invalid. |
| `1024` | 3DSecure authentication failed | Cardholder 3DS auth failed. |
| `1025` | Invalid card expiry date | Expiry is invalid. |
| `1037` | Decline, not sufficient funds | Not enough funds. |
| `1040` | Transaction amount exceeds card internet limit | Issuer/card online limit hit. |
| `1053` | 3DSecure card verification failed. Directory server or issuer not available. | 3DS verification infrastructure unavailable. |
| `1064` | Call your bank | Customer must contact issuer. |
| `1065` | Invalid transaction | Issuer rejected transaction type/state. |
| `1067` | Incorrect PIN | PIN error in relevant payment flow. |
| `1097` | Decline, refer to card issuer | Issuer declined transaction. |

### Flitt/platform/acquirer-side issues

| Code | Text | Practical meaning |
| --- | --- | --- |
| `1000` | General decline | Unknown cause, requires deeper analysis. |
| `1002` | Application error | Unknown platform/application issue. |
| `1006` | Merchant is not configured correctly | Merchant misconfigured on Flitt side. |
| `1016` | Merchant not found | Merchant is not registered. |
| `1017` | No available payment systems | Merchant cannot use provided payment methods. |
| `1018` | Order not found | Status/reversal request references missing order. |
| `1027` | Preauth not allowed | Merchant is not enabled for preauth. |
| `1041` | Card is in black list | Risk/blacklist block. |
| `1045` | Card is blocked by acquirer bank | Acquirer-side block. |
| `1049` | Unknown payment system error | Upstream payment-system problem. |
| `1051` | Declined by antifraud | Risk engine declined transaction. |
| `1055` | P2P limit exceeded | P2P limit on platform side. |
| `1059` | Transaction with rectoken not allowed for merchant | Merchant not enabled for token charges. |
| `1060` | Recurring transaction not allowed for merchant | Merchant not enabled for recurring. |
| `1062` | Not permitted to merchant | Operation not permitted for merchant. |
| `1066` | System malfunction | Acquirer system problem. |
| `1069` | Reverse not allowed. Turnover is not enough. | Reversal disallowed by platform/acquirer state. |
| `1074` | P2P credit allowed only by rectoken | P2P credit method restriction. |
| `1078` | Token deactivated by bank | Token invalidated upstream. |
| `1081` | Insufficient funds on balance (p2p credit) | Platform-side balance issue. |
| `1087` | Terminal closed by acquiring bank | Acquirer terminal blocked. |
| `1089` | Acquiring bank request timeout | Upstream timeout. |
| `1090` | P2P card credit not allowed for this country | Country restriction. |
| `1099` | P2P credit is not available for this IP address | Merchant must register server IPs with Flitt support. |
| `1100` | Operation not allowed | API operation not enabled for merchant. |
| `1104` | Country not allowed by bank-acquirer | Acquirer country restriction. |
| `1105` | Antifraud decline. Only full 3D-Secure allowed. | Merchant flow must enforce full 3DS. |
| `1122` | Connection closed unexpectedly | Technical connectivity failure. |
| `1123` | Acquiring bank request timeout. Transaction reversed. | Upstream timeout with technical reversal performed. |

## JavaScript Response Codes

These apply to embedded checkout JavaScript callbacks:

| Code | Text |
| --- | --- |
| `2000` | Payment declined by issuing bank. Possibly internet payments not allowed for this card. Please refer to your bank for details. |
| `2001` | This currency not allowed. |
| `2002` | Possibly your cookies are disabled. Please enable cookies in browser settings and try again. |
| `2003` | Merchant is configured incorrectly. |
| `2004` | Duplicate order. Please return to the shop site and try again. |
| `2005` | No available payment methods |

Map these to UI behavior carefully:

- `2001`, `2003`, `2004`, `2005`: merchant/integration handling
- `2000`: issuer/customer-card decline
- `2002`: client/browser setup problem

## Practical Triage

When a Flitt payment fails:

1. Check `response_status` first.
2. Read `response_code` and `response_description`.
3. Classify ownership: merchant, issuer, or Flitt.
4. Decide retry behavior:
   Retry with same logical request only when the operation is documented as retry-safe.
5. Decide customer message:
   Input/configuration errors should not be shown as generic bank declines.

## Implementation Notes

- Persist both `response_code` and `response_description` for support/debugging.
- Avoid exposing raw internal codes directly to end users unless the product explicitly wants that.
- Build product-facing error mapping by ownership category, not by dumping raw Flitt text into the UI.
- Pay special attention to codes tied to earlier skill sections: `1012` currencies, `1014` signatures, `1035`/`1082` tokens, `1027` preauth, `1109` capture, `1084` reversal.
