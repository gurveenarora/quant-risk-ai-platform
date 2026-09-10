import pytest
import asyncio
from app.ai.quant_agent import agent_workflow_instance
from app.core.security import security_manager

def test_quant_agent_prompt_execution():
    """Verify that quant agent handles VaR, risk, backtest, and Kupiec prompts without NameError."""
    prompts = [
        "What is the portfolio VaR risk?",
        "Execute a Kupiec POF backtest",
        "Run Hypothesis PBT suite",
        "Scrape AAPL market indicators"
    ]
    
    async def run_all():
        for p in prompts:
            res = await agent_workflow_instance.process_user_query(p, user_role="QuantAnalyst")
            assert res["status"] in ["COMPLETED", "SECURITY_BLOCK"]
            assert "tool_calls_executed" in res
            assert len(res["tool_calls_executed"]) > 0

    asyncio.run(run_all())

def test_jwt_signature_verification_and_tampering():
    """Verify cryptographic HMAC signature verification rejects forged tokens."""
    token = security_manager.create_jwt_token("admin@quant.ai", role="Admin")
    session = security_manager.decode_jwt_token(token)
    
    assert session is not None
    assert session.username == "admin@quant.ai"
    assert session.role == "Admin"
    
    # Tamper with token payload (attempt role escalation)
    parts = token.split(".")
    forged_token = f"{parts[0]}.eyJ1c2VybmFtZSI6ImFkbWluQHF1YW50LmFpIiwicm9sZSI6IkFkbWluIiwiZXhwIjoyMDAwMDAwMDAwfQ.{parts[2]}"
    assert security_manager.decode_jwt_token(forged_token) is None

def test_pbkdf2_salted_password_hashing():
    """Verify PBKDF2 HMAC SHA-256 salted password hashing."""
    hash_val, salt_hex = security_manager.hash_password("SuperSecret123!")
    
    assert security_manager.verify_password("SuperSecret123!", hash_val, salt_hex)
    assert not security_manager.verify_password("WrongPassword!", hash_val, salt_hex)

def test_aes_field_encryption_and_decryption():
    """Verify AES-256 stream cipher encryption & authenticated decryption."""
    plaintext = "SensitivePortfolioDataValue=$10,000,000"
    ciphertext = security_manager.encrypt_sensitive_field(plaintext)
    
    assert ciphertext != plaintext
    decrypted = security_manager.decrypt_sensitive_field(ciphertext)
    assert decrypted == plaintext
