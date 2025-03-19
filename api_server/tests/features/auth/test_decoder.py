from features.auth.decoder import decode_token

def test_decode_valid_token():
    token = "valid_token_string"
    decoded_data = decode_token(token)
    assert decoded_data is not None