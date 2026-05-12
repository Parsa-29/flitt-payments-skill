# Flitt Additional Data Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/api/reservation_data/

Use this reference for Flitt `reservation_data`: attaching extra customer, device, checkout-field, settlement, or fiscalisation data to a create-purchase request.

## Scope

`reservation_data` is an optional parameter sent with a create-purchase request. Its value is a JSON object encoded with BASE64.

Use it when the merchant needs to send:

- payer/customer metadata
- merchant account identifiers
- device UUID
- settlement reconciliation ID
- custom checkout fields
- product/fiscalisation line items
- Flitt-approved 3DS behavior override

This is purchase-request metadata, not a standalone API.

## Request Placement

Attach `reservation_data` as a normal purchase parameter inside the root `request` object for JSON flows, or as a signed form field for redirect flows.

Example:

```json
{
  "request": {
    "response_url": "https://site.com/responsepage/",
    "order_id": "test_reservation_data_12345",
    "order_desc": "Test payment",
    "currency": "GEL",
    "amount": "100",
    "merchant_id": "1549901",
    "reservation_data": "BASE64_ENCODED_JSON",
    "signature": "..."
  }
}
```

Encode the JSON bytes as BASE64 before signing and sending the request.

## Base JSON Structure

Example decoded JSON:

```json
{
  "phonemobile": "+12345678",
  "customer_address": "15 gannet street elspark",
  "customer_country": "US",
  "customer_state": "NY",
  "customer_name": "Brandon Nyathi",
  "customer_city": "New York",
  "customer_zip": "1401",
  "account": "id32648480",
  "uuid": "00002415-0000-1000-8000-00805F9B34FB"
}
```

The docs state that all parameters must be alphanumeric and use Latin characters, digits, and separator symbols.

## Common Fields

| Field | Required | Notes |
| --- | --- | --- |
| `phonemobile` | no | Client mobile phone, max 16 chars. |
| `customer_address` | no | Client address, max 1024 chars. |
| `customer_country` | no | Billing country ISO code, 2 chars. |
| `customer_state` | no | Billing state/region. Present in example payload. |
| `customer_name` | no | Payer name, max 1024 chars. |
| `customer_city` | no | Payer city, max 1024 chars. |
| `customer_zip` | no | ZIP/postal code, max 250 chars. |
| `account` | no | Merchant-side customer/account ID, max 250 chars. |
| `uuid` | no | Device UUID, max 250 chars. |
| `settlement_id` | no | Settlement reconciliation identifier, max 32 chars. |
| `3ds_mandatory` | no | Boolean flag related to forcing payment without 3DS. Use only after Flitt risk-team approval. |
| `fields_custom[]` | no | JSON array of extra fields shown on checkout. |
| `products[]` | no | JSON array of products for fiscalisation. |

## Custom Checkout Fields

`fields_custom` is a JSON array used to add custom input fields to the Flitt checkout page.

Example:

```json
{
  "fields_custom": [
    {
      "name": "id-1",
      "label": "label1",
      "value": "1",
      "valid": {
        "pattern": "^[0-9]+$",
        "max_length": 222,
        "min_length": 10
      },
      "readonly": false,
      "required": true,
      "type": "input",
      "p": 1
    },
    {
      "name": "id-2",
      "label": "label2",
      "value": "",
      "p": 2
    },
    {
      "name": "id-3",
      "label": "label3",
      "type": "checkbox",
      "required": true,
      "p": 3
    }
  ]
}
```

Useful field attributes from the example:

- `name`: stable field identifier
- `label`: field label shown to customer
- `value`: default value
- `valid.pattern`: regex validation rule
- `valid.max_length` / `valid.min_length`: length constraints
- `readonly`: whether the field is editable
- `required`: whether the field must be completed
- `type`: field type such as `input` or `checkbox`
- `p`: display order/position

## Fiscalisation Products

`products` is a JSON array with product data used for fiscalisation.

Example:

```json
{
  "products": [
    {
      "id": 1,
      "name": "Product A",
      "price": 100.0,
      "quantity": 2,
      "vat_percent": 20,
      "code": "00702001001000001",
      "units": 1,
      "discount": 10.0,
      "package_code": "5678",
      "total_amount": 190.0
    }
  ]
}
```

Documented product fields:

| Field | Required | Notes |
| --- | --- | --- |
| `id` | no | Product identifier. |
| `name` | no | Product name. |
| `price` | no | Price per unit. |
| `quantity` | no | Quantity. |
| `vat_percent` | no | VAT percentage. |
| `code` | no | Product/service identification code. |
| `units` | no | Unit code. |
| `discount` | no | Discount amount. |
| `package_code` | no | Product packaging code. |
| `total_amount` | no | Total amount for all units of the item. |

## Implementation Notes

- Build the reservation JSON object first, then BASE64-encode it, then place the encoded string in `reservation_data`.
- Sign the final request with the encoded `reservation_data` string, not the decoded JSON.
- Keep payload content ASCII-safe unless the project has already verified broader character support with Flitt.
- Treat `fields_custom` names and validation rules as part of the checkout contract; keep them stable once clients depend on them.
- Use `settlement_id` when the merchant needs downstream reconciliation against settlement reports.
- Use `products` only when fiscalisation or product-level reporting is actually required.
- Do not set `3ds_mandatory` unless the merchant has explicit approval from Flitt.
