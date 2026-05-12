# Flitt Currencies Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/api/currencies/

Use this reference when validating the Flitt `currency` field for bank-card processing.

## Supported Currencies

The Flitt docs list supported bank-card processing currencies by merchant country:

| Merchant country | Currency code | Currency name |
| --- | --- | --- |
| Georgia | `GEL` | Georgian Lari |
| Georgia | `USD` | United States dollar |
| Georgia | `EUR` | Euro |
| Armenia | `AMD` | Armenian Dram |
| Azerbaijan | `AZN` | Azerbaijanian Manat |
| Kazakhstan | `KZT` | Tenge |
| Moldova | `MDL` | Moldovian Leu |
| Uzbekistan | `UZS` | Uzbekistan Sum |

## Implementation Notes

- Validate `currency` against the merchant's country configuration before sending the request.
- Treat this table as the bank-card processing matrix documented by Flitt, not a universal availability statement for every product or payment method.
- Georgia is the only country in this page with multiple listed currencies: `GEL`, `USD`, and `EUR`.
- If the merchant account geography is unclear, do not guess from the app locale; verify the merchant setup first.
