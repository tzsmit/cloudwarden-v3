"""
CloudWarden v3 AI Agent System
Revolutionary local LLM integration for security analysis
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Try to import AI libraries with graceful fallback
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not installed. AI features will be limited.")

logger = logging.getLogger(__name__)

# --- performance knobs (override via env) ---
MAX_TOKENS = int(os.getenv("CLOUDWARDEN_AI_MAX_TOKENS", "192"))   # cap output
KEEP_ALIVE = os.getenv("CLOUDWARDEN_KEEP_ALIVE", "5m")            # keep model in RAM
CTX_LEN = int(os.getenv("CLOUDWARDEN_AI_CTX", "2048"))            # context hint
# ------------------------------------------------


@dataclass
class AIAnalysis:
    """Container for AI-generated analysis results"""
    business_impact: str
    technical_explanation: str
    remediation_steps: List[str]
    risk_factors: List[str]
    confidence_score: float = 0.0


class CloudWardenAIAgent:
    """Main AI agent for CloudWarden security analysis"""

    def __init__(self, config):
        self.config = config
        self.ollama_client = None
        self.available = False

        # Initialize AI capabilities
        self._initialize_ollama()

    def _initialize_ollama(self):
        """Initialize connection to local Ollama server"""
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama not installed. AI features disabled.")
            return

        try:
            # Test connection to Ollama
            response = requests.get(
                f"{self.config.ai_agent.ollama_base_url}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                self.ollama_client = ollama.Client(
                    host=self.config.ai_agent.ollama_base_url
                )

                # Check if models are available
                data = response.json() or {}
                available_models = data.get('models', [])
                model_names = [m.get('name') for m in available_models if 'name' in m]

                # Prefer primary model; fall back if needed
                model_to_use = None
                if self.config.ai_agent.model in model_names:
                    model_to_use = self.config.ai_agent.model
                elif getattr(self.config.ai_agent, "fallback_model", None) in model_names:
                    model_to_use = self.config.ai_agent.fallback_model
                    logger.info(
                        f"Primary model '{self.config.ai_agent.model}' not found; "
                        f"using fallback '{model_to_use}'."
                    )
                else:
                    logger.warning(
                        f"Configured model '{self.config.ai_agent.model}' not found. "
                        f"Available: {model_names}"
                    )

                if model_to_use:
                    # update to the chosen model so subsequent calls use it
                    self.config.ai_agent.model = model_to_use
                    self.available = True
                    logger.info(f"AI agent initialized with model: {model_to_use}")

        except Exception as e:
            logger.warning(f"Failed to connect to Ollama: {e}")

    def is_available(self) -> bool:
        """Check if AI agent is available"""
        return self.available and self.ollama_client is not None

    def analyze_finding(self, finding: Dict[str, Any]) -> AIAnalysis:
        """Perform AI analysis of a security finding"""
        if not self.is_available():
            return self._generate_fallback_analysis(finding)

        # Try fast single-call JSON mode first; fall back to 3 calls
        combined = self._analyze_combined(finding)
        if combined:
            return combined

        try:
            # Generate business impact explanation
            business_impact = self._generate_business_impact(finding)

            # Generate technical explanation
            technical_explanation = self._generate_technical_explanation(finding)

            # Generate remediation steps
            remediation_steps = self._generate_remediation_steps(finding)

            # Identify risk factors
            risk_factors = self._identify_risk_factors(finding)

            return AIAnalysis(
                business_impact=business_impact,
                technical_explanation=technical_explanation,
                remediation_steps=remediation_steps,
                risk_factors=risk_factors,
                confidence_score=0.85
            )

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._generate_fallback_analysis(finding)

    def _generate_business_impact(self, finding: Dict[str, Any]) -> str:
        """Generate business impact explanation (concise)"""
        prompt = f"""
        Explain the business impact of this security finding in simple terms:

        Type: {finding.get('type', 'Security Issue')}
        Severity: {finding.get('severity', 'Unknown')}
        Resource: {finding.get('resource_id', 'Unknown')}

        Focus on: financial impact, operational risk, and compliance concerns.
        Keep it under 80 words. Be concise and non-technical.
        """.strip()

        return self._query_ai(prompt)

    def _generate_technical_explanation(self, finding: Dict[str, Any]) -> str:
        """Generate technical explanation for engineers (concise)"""
        prompt = f"""
        Provide a technical explanation of this security vulnerability:

        Type: {finding.get('type', 'Security Issue')}
        Details: {finding.get('description', 'No details available')}

        Explain: what it is, how it could be exploited, why it's dangerous.
        Keep it under 120 words. Be concise.
        """.strip()

        return self._query_ai(prompt)

    def _generate_remediation_steps(self, finding: Dict[str, Any]) -> List[str]:
        """Generate step-by-step remediation"""
        prompt = f"""
        Provide step-by-step remediation for this security issue:

        Type: {finding.get('type', 'Security Issue')}
        Resource: {finding.get('resource_id', 'Unknown')}

        Return 3-5 short, numbered steps that can be followed directly.
        """.strip()

        response = self._query_ai(prompt)

        # Parse response into steps
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith(('-', '•'))):
                step = line.lstrip('0123456789.-•) ').strip()
                if step:
                    steps.append(step)

        return steps if steps else [response]

    def _identify_risk_factors(self, finding: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        risk_factors = []

        # Common risk patterns
        text = str(finding).lower()
        if 'wildcard' in text or '*:*' in text:
            risk_factors.append("Overly broad permissions")
        if 'public' in text:
            risk_factors.append("Public internet exposure")
        if 'mfa' in text:
            risk_factors.append("Multi-factor authentication issues")

        severity = (finding.get('severity') or '').lower()
        if severity in ['critical', 'high']:
            risk_factors.append("High severity security vulnerability")

        return risk_factors

    def _query_ai(self, prompt: str) -> str:
        """Send prompt to AI model and get response (capped + kept alive)"""
        if not self.is_available():
            return "AI analysis not available"

        try:
            response = self.ollama_client.generate(
                model=self.config.ai_agent.model,
                prompt=prompt,
                options={
                    'temperature': self.config.ai_agent.temperature,
                    'num_predict': MAX_TOKENS,
                    'num_ctx': CTX_LEN,
                },
                keep_alive=KEEP_ALIVE,
            )
            return (response.get('response') or '').strip()

        except Exception as e:
            logger.error(f"AI query failed: {e}")
            return f"AI analysis failed: {str(e)}"

    def _analyze_combined(self, finding: Dict[str, Any]) -> Optional[AIAnalysis]:
        """Faster single-call analysis that returns all fields at once (JSON)."""
        prompt = f"""
        You are a cloud security assistant. Given the finding below, return a JSON object with keys:
        - business_impact (<=80 words)
        - technical_explanation (<=120 words)
        - remediation_steps (array of 3-5 short steps)
        - risk_factors (array of short phrases)

        Finding:
        {json.dumps(finding, ensure_ascii=False)}

        Return ONLY JSON, no preamble or backticks.
        """.strip()

        raw = self._query_ai(prompt)
        try:
            data = json.loads(raw)
            return AIAnalysis(
                business_impact=(data.get("business_impact") or "").strip(),
                technical_explanation=(data.get("technical_explanation") or "").strip(),
                remediation_steps=[s.strip() for s in (data.get("remediation_steps") or []) if str(s).strip()],
                risk_factors=[s.strip() for s in (data.get("risk_factors") or []) if str(s).strip()],
                confidence_score=0.85,
            )
        except Exception:
            logger.debug("Combined analysis JSON parse failed; falling back to multi-call.")
            return None

    def _generate_fallback_analysis(self, finding: Dict[str, Any]) -> AIAnalysis:
        """Generate basic analysis when AI is unavailable"""
        finding_type = finding.get('type', 'Security Issue')
        severity = finding.get('severity', 'Medium')

        return AIAnalysis(
            business_impact=f"This {severity} severity {finding_type} requires attention to maintain security posture.",
            technical_explanation=f"Security issue detected: {finding.get('description', 'No details available')}",
            remediation_steps=[
                "Review the security finding details",
                "Consult AWS security best practices",
                "Implement appropriate security controls",
                "Validate and test the remediation"
            ],
            risk_factors=self._identify_risk_factors(finding),
            confidence_score=0.3
        )


def test_ai_agent():
    """Test AI agent functionality"""
    # Mock configuration for testing
    class MockConfig:
        def __init__(self):
            self.ai_agent = MockAIConfig()

    class MockAIConfig:
        model = "llama3.1:8b"
        ollama_base_url = "http://localhost:11434"
        temperature = 0.1

    config = MockConfig()
    agent = CloudWardenAIAgent(config)

    print("=== CloudWarden AI Agent Test ===")
    print(f"AI Available: {agent.is_available()}")

    # Test with sample finding
    sample_finding = {
        'type': 'iam_wildcard_policy',
        'severity': 'High',
        'resource_id': 'arn:aws:iam::123:role/test',
        'description': 'IAM role has wildcard permissions'
    }

    analysis = agent.analyze_finding(sample_finding)
    print(f"Business Impact: {analysis.business_impact}")
    print(f"Confidence: {analysis.confidence_score}")


if __name__ == "__main__":
    test_ai_agent()
