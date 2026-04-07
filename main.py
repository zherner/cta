import jwt  # PyJWT
from jwt import PyJWKClient

# Cognito values templated via terraform sed
cognito_user_pool_id = "#cognito_user_pool_id#"
region = "#cognito_region#"
issuer = f"https://cognito-idp.{region}.amazonaws.com/{cognito_user_pool_id}"

# Fetch cognito signing keys and create jwks client
jwks_url = f"{issuer}/.well-known/jwks.json"
jwks_client = PyJWKClient(jwks_url)


def handler(event, context):
    cf_request = event["Records"][0]["cf"]["request"]
    headers = cf_request["headers"]

    try:
        # Check for Authorization header
        if "authorization" not in headers:
            print("No Authorization header found in request.")
            raise ValueError("missing header")

        # Extract JWT token (strip 'Bearer ' string)
        jwt_token = headers["authorization"][0]["value"][7:]
        print(f"jwt_token='{jwt_token}'")

        # Check issuer and token_use
        decoded_payload = jwt.decode(jwt_token, options={"verify_signature": False})
        if decoded_payload.get("iss") != issuer:
            print("Found issuer did not match expected issuer value")
            raise ValueError("invalid issuer")

        if decoded_payload.get("token_use") != "access":
            print("Incorrect token_use found, expected 'access'")
            raise ValueError("invalid token_use type")

        # Verify signature using cognito JWKS public keys
        signing_key = jwks_client.get_signing_key_from_jwt(jwt_token)
        jwt.decode(jwt_token, signing_key.key, algorithms=["RS256"], issuer=issuer)

    except Exception as e:
        print(f"Authorization failed: {e}")
        return {"status": "401", "statusDescription": "Unauthorized"}

    # For valid token - remove authorization header and continue downstream
    headers.pop("authorization", None)

    return cf_request
