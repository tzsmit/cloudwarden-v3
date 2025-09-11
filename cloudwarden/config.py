"""
CloudWarden v3 Configuration Management
Handles all configuration loading, validation, and management
"""

import os
import yaml
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AWSConfig:
    """AWS-specific configuration settings"""
    regions: List[str] = field(default_factory=lambda: ['us-east-1'])
    profile: Optional[str] = None
    max_retries: int = 3
    timeout: int = 60

    def validate(self) -> bool:
        """Validate AWS configuration"""
        if not self.regions:
            raise ValueError("At least one AWS region must be specified")
        return True


@dataclass
class AIAgentConfig:
    """Configuration for local AI agent using Ollama"""
    enabled: bool = True
    model: str = "llama3.1:8b"
    fallback_model: str = "deepseek-r1:7b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.1
    timeout_seconds: int = 120

    def validate(self) -> bool:
        """Validate AI agent configuration"""
        if self.enabled and not self.model:
            raise ValueError("AI model must be specified when agent is enabled")
        return True


@dataclass
class ScanningConfig:
    """Configuration for security scanning behavior"""
    iam_analysis: bool = True
    iot_security: bool = True
    attack_paths: bool = True
    services: List[str] = field(default_factory=lambda: ['iam', 'iot', 's3', 'ec2'])
    parallel_workers: int = 4
    timeout_seconds: int = 600

    def validate(self) -> bool:
        """Validate scanning configuration"""
        if self.parallel_workers <= 0:
            raise ValueError("parallel_workers must be positive")
        return True


@dataclass
class ReportingConfig:
    """Configuration for report generation"""
    formats: List[str] = field(default_factory=lambda: ['json', 'html'])
    output_directory: str = './reports'
    company_name: str = "Nova Titan Systems"
    primary_color: str = "#00F5A0"

    def validate(self) -> bool:
        """Validate reporting configuration"""
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        return True


class CloudWardenConfig:
    """Main configuration class for CloudWarden v3"""

    def __init__(self, config_file: Optional[str] = None):
        self.metadata = {
            'version': '3.0.0',
            'tool_name': 'CloudWarden',
            'organization': 'Nova Titan Systems'
        }

        # Initialize configuration sections
        self.aws = AWSConfig()
        self.ai_agent = AIAgentConfig()
        self.scanning = ScanningConfig()
        self.reporting = ReportingConfig()

        # Load configuration
        self._load_from_environment()

        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)

        logger.info("CloudWarden configuration initialized")

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        if os.getenv('AWS_PROFILE'):
            self.aws.profile = os.getenv('AWS_PROFILE')

        if os.getenv('AWS_REGION'):
            self.aws.regions = [os.getenv('AWS_REGION')]

        if os.getenv('CLOUDWARDEN_AI_MODEL'):
            self.ai_agent.model = os.getenv('CLOUDWARDEN_AI_MODEL')

    def load_from_file(self, config_path: str):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}

            if 'aws' in data:
                aws_data = data['aws'] or {}
                if 'regions' in aws_data:
                    self.aws.regions = aws_data['regions']
                if 'profile' in aws_data:
                    self.aws.profile = aws_data['profile']

            logger.info(f"Configuration loaded from: {config_path}")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def validate_all(self) -> bool:
        """Validate all configuration sections"""
        try:
            self.aws.validate()
            self.ai_agent.validate()
            self.scanning.validate()
            self.reporting.validate()
            logger.info("Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise


def load_config(config_file: Optional[str] = None) -> CloudWardenConfig:
    """Load and validate CloudWarden configuration"""
    config = CloudWardenConfig(config_file)
    config.validate_all()
    return config
