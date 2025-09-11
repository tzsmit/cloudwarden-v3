"""
CloudWarden v3 - Revolutionary AI-Powered Cloud Security Platform
Nova Titan Systems

Find misconfigurations fast. Ship safer.
"""

__version__ = "3.0.0"
__author__ = "Nova Titan Systems"
__email__ = "support@novatitan.net"
__license__ = "MIT"

def get_version_info():
    """Get detailed version information"""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "components": [
            "AI Agent System",
            "Attack Path Analysis",
            "IoT/OT Security Scanner",
            "Quantum Crypto Analyzer",
            "Executive Reporting",
        ],
    }

__all__ = ["__version__", "get_version_info"]

if __name__ == "__main__":
    # Only prints when you run this file directly, not on import
    print(f"CloudWarden v{__version__} - Nova Titan Systems")
    print("🛡️ Revolutionary AI-Powered Cloud Security Platform")

