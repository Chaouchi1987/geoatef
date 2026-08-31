from backend.auth.security import hash_password, verify_password

def test_password_roundtrip():
    h = hash_password("CorrectHorseBattery9!")
    assert verify_password("CorrectHorseBattery9!", h)
    assert not verify_password("wrong-password", h)
