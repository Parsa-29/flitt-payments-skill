# Flitt Subscriptions Reference

Sources checked on 2026-05-12:

- https://docs.flitt.com/api/subscriptions_intro/
- https://docs.flitt.com/api/subscriptions/
- https://docs.flitt.com/api/cancel-subscriptions/

Use this reference for scheduled subscription payments: create subscription checkout requests, configure `recurring_data`, and start/stop existing subscriptions.

## Scope

Subscription payments charge a customer at a fixed, predictable frequency such as daily, weekly, monthly, or yearly.

Do not confuse subscriptions with Payment with saved card. Saved-card `/api/recurring` charges are tokenized host-to-host charges that are usually not scheduled. Subscriptions are scheduled and displayed to the payer on Flitt checkout after the subscription order is created.

Constraints:

- Subscription payments do not work with Payment (direct) integration.
- Open Banking does not support subscriptions.
- Supported methods are Visa/MasterCard/Amex cards, Apple Pay, and Google Pay.
- Create subscriptions through checkout endpoints: `/api/checkout/redirect`, `/api/checkout/token`, or `/api/checkout/url`.

## Create Subscription

Start with the normal create-order flow and add subscription fields.

Set:

```json
{
  "subscription": "Y",
  "recurring_data": {
    "every": 5,
    "period": "day",
    "amount": 1000,
    "state": "Y",
    "quantity": 100,
    "trial_period": "month",
    "trial_quantity": 1
  }
}
```

Example checkout URL request:

```json
{
  "request": {
    "order_id": "test_subscription5",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test payment",
    "amount": 100,
    "subscription": "Y",
    "recurring_data": {
      "every": 5,
      "period": "day",
      "amount": 1000,
      "state": "Y",
      "quantity": 100,
      "trial_period": "month",
      "trial_quantity": 1
    },
    "signature": "..."
  }
}
```

Important signing note: `recurring_data` is nested JSON. Prefer an official Flitt SDK or an existing project implementation that is already known to sign nested parameters correctly. The bundled `flitt_signature.py` helper is intended for flat request/response parameters; do not rely on it blindly for nested `recurring_data` without verifying the generated signature against Flitt.

## Recurring Data Fields

| Field | Required | Notes |
| --- | --- | --- |
| `amount` | yes | Amount of each scheduled charge, without separator. `1020` GEL means 10 lari and 20 tetri. |
| `period` | yes | Frequency unit: `day`, `week`, or `month`. |
| `every` | yes | Number of days, weeks, or months between scheduled charges. |
| `quantity` | conditional | Number of scheduled charges. Either `quantity` or `end_time` must be specified. |
| `end_time` | conditional | End date/time. Either `quantity` or `end_time` must be specified. Format `YYYY-MM-DD HH24:MI:SS`. |
| `start_time` | no | First scheduled charge time. If omitted, scheduling starts from customer initial payment approval. Format `YYYY-MM-DD HH24:MI:SS`. |
| `trial_period` | no | Trial frequency unit: `day`, `week`, or `month`. Trial is disabled by default. |
| `trial_quantity` | conditional | Number of trial periods. Required when `trial_period` is provided. |
| `state` | no | Controls checkout calendar display and availability. Default enables the subscription option. |

## State Values

Use `state` to control the subscription calendar/options on checkout.

| `state` value | Meaning |
| --- | --- |
| `y` or `Y` | Enable calendar on checkout and allow customer to disable it. |
| `n` or `N` | Disable calendar on checkout and allow customer to enable it. |
| `hidden` | Enable calendar but do not show it to customer. |
| `shown_readonly` | Enable calendar and do not allow customer to disable it. |

Some examples include `readonly`, but the documented property table describes `state` as the control for shown/hidden/readonly behavior. Prefer the documented `state` values unless the project already uses Flitt SDK conventions.

## Start Or Stop Subscription

Endpoint:

```text
POST https://pay.flitt.com/api/subscription
Content-Type: application/json
```

Required request parameters:

| Parameter | Required | Notes |
| --- | --- | --- |
| `order_id` | yes | Merchant-generated order ID for the original subscription. |
| `merchant_id` | yes | Flitt merchant ID. |
| `action` | yes | `start` or `stop`. |
| `signature` | yes | SHA1 request signature. |

Start request:

```json
{
  "request": {
    "order_id": "test_subscription11",
    "merchant_id": 1549901,
    "action": "start",
    "signature": "..."
  }
}
```

Stop request:

```json
{
  "request": {
    "order_id": "test_subscription11",
    "merchant_id": 1549901,
    "action": "stop",
    "signature": "..."
  }
}
```

Response fields:

| Field | Meaning |
| --- | --- |
| `response_status` | API request processing status. |
| `status` | Subscription status: `active` or `disabled`. |
| `order_id` | Original subscription order ID. |
| `merchant_id` | Flitt merchant ID. |
| `signature` | Response signature. |

## Implementation Checklist

- Decide whether the product needs scheduled subscription billing or unscheduled saved-card charges.
- Do not use subscriptions for Direct integration or Open Banking.
- Use a checkout endpoint and set `subscription=Y`.
- Populate `recurring_data.amount`, `period`, `every`, and either `quantity` or `end_time`.
- Handle optional trial fields together: if `trial_period` is set, also set `trial_quantity`.
- Use `state` deliberately to control whether the customer can see or change the subscription schedule on checkout.
- Persist the original subscription `order_id`.
- Implement start/stop through `/api/subscription`.
- Verify signatures on subscription responses before trusting status changes.
