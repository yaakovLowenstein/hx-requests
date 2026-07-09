MODEL_INSTANCE_PREFIX = "model_instance__"

# Query param that carries the signed round-trip token, and the signing salt.
# The salt only namespaces the signature; secrecy comes from SECRET_KEY. A
# per-name salt is intentionally NOT used: the handler name lives inside the
# signed payload, so a token minted for one handler cannot be replayed against
# another (tampering the name invalidates the signature).
HX_TOKEN_PARAM = "hx"
HX_SIGNING_SALT = "hx-requests"
