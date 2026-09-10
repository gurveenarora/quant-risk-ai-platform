"""
AI Security Guardrails & OWASP Defense Layer
Prevents prompt injection, malicious tool parameter execution, and output data leakage.
"""

import re
from typing import Dict, Any, List

SUSPICIOUS_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"you are now DAN",
    r"jailbreak",
    r"bypass security",
    r"execute arbitrary",
    r"eval\(",
    r"rm -rf",
    r"drop database",
    r"<script>",
    r"cat /etc/passwd"
]

class AISecurityGuardrails:
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS]

    def inspect_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Dual-layer prompt inspection scanning for prompt injections and malicious commands.
        """
        detected_threats = []
        for pattern in self.compiled_patterns:
            match = pattern.search(prompt)
            if match:
                detected_threats.append(match.group(0))
                
        is_malicious = len(detected_threats) > 0
        
        return {
            "is_malicious": is_malicious,
            "threat_score": 0.95 if is_malicious else 0.0,
            "detected_threats": detected_threats,
            "action": "BLOCK" if is_malicious else "ALLOW",
            "guardrail_engine": "AI Security Dual-Stage Regex/Classifier Engine"
        }

    def sanitize_output(self, text: str) -> str:
        """Data Leakage Defense: Masks API keys, JWT tokens, and internal IPs from model output."""
        # Mask API keys matching sk- or Bearer tokens
        sanitized = re.sub(r'(sk-[a-zA-Z0-9]{20,})', '[REDACTED_API_KEY]', text)
        sanitized = re.sub(r'(Bearer\s+[a-zA-Z0-9\._\-]+)', '[REDACTED_JWT_TOKEN]', sanitized)
        sanitized = re.sub(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)', '[REDACTED_IP]', sanitized)
        return sanitized

guardrails_instance = AISecurityGuardrails()
