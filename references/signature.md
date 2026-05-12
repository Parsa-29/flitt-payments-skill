# Flitt Signature Reference

Source checked on 2026-05-12:

- https://docs.flitt.com/api/building-signature/

Use this reference for Flitt request/response/callback signature generation and signature mismatch debugging.

## Signature Algorithm

Flitt uses SHA1 for the `signature` parameter in:

- create-order requests
- create-order responses
- callbacks
- redirect/response payloads

Build the signature string as:

1. Start with the merchant payment secret key.
2. Add all non-empty request or response parameter values.
3. Sort parameters alphabetically by key before taking values.
4. Exclude `signature`.
5. When verifying responses/callbacks, also exclude `response_signature_string`.
6. Join values with `|`.
7. Hash the UTF-8 encoded string with SHA1.
8. Use lowercase hex output.

Example string from the docs:

```text
test|1000|GEL|1549901|Test payment|TestOrder2|http://myshop/callback/
```

If a parameter is absent or empty, do not include its separator.

## Official Python Example

The Flitt docs provide this Python logic:

```python
from hashlib import sha1

def get_signature(secret_key, params):
    data = [secret_key]
    data.extend(
        [
            str(params[key])
            for key in sorted(iter(params.keys()))
            if params[key] != "" and params[key] is not None and key != "signature"
        ]
    )
    return sha1("|".join(data).encode("utf-8")).hexdigest()
```

For callback/response verification, remove `response_signature_string` before applying the same algorithm.

## Request And Callback Verification

The bundled helper in this skill matches the documented flat-parameter algorithm:

```bash
python3 ~/.codex/skills/flitt-payments/scripts/flitt_signature.py \
  --secret "$FLITT_PAYMENT_KEY" \
  --params-file payload.json
```

To verify against a known signature:

```bash
python3 ~/.codex/skills/flitt-payments/scripts/flitt_signature.py \
  --secret "$FLITT_PAYMENT_KEY" \
  --params-file payload.json \
  --verify "$EXPECTED_SIGNATURE"
```

The helper automatically signs the inner `request` or `response` object when present.

## Troubleshooting Invalid Signature

When Flitt returns `error_message: "Invalid signature"` for an API call, the docs recommend checking:

- the correct payment secret key for the environment/merchant
- UTF-8 encoding for non-Latin input
- that a numeric `0` value was not converted to null/empty
- the exact pre-hash string used by your code
- omission of separators for empty parameters
- lowercase SHA1 output
- exclusion of the `signature` parameter from the calculation
- endpoint-specific parameter sets, especially `/api/recurring`

The docs also suggest comparing your pre-hash string with Flitt’s returned `response_signature_string` diagnostic when it is present in an error context.

## Callback Or Redirect Signature Mismatch

When verifying a POST callback to `server_callback_url` or a POST redirect to `response_url`, common causes are:

- forgetting to remove `response_signature_string`
- including empty values in the signature string
- uppercasing the SHA1 digest
- signing the wrong JSON level
- using the wrong secret key

For callback/redirect payloads, verify the flat payload object and exclude:

- `signature`
- `response_signature_string`

## Recurring Endpoint Caveat

Flitt explicitly notes that `/api/recurring` should include only the parameters necessary for that endpoint in the signature calculation. Do not accidentally sign parameters that belong to redirect or other flows.

## Implementation Checklist

- Generate signatures only on the server.
- Log the pre-hash string locally when debugging, but never expose the unmasked secret in shared logs.
- Exclude `signature` from all calculations.
- Exclude `response_signature_string` from response/callback verification.
- Omit empty/null fields entirely.
- Preserve zero values.
- Encode as UTF-8.
- Keep SHA1 output lowercase.
- Use endpoint-specific parameter sets.
