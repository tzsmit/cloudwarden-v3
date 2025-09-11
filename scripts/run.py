
"""
CloudWarden v3 Main CLI Entry Point
"""

import click
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table

from cloudwarden import get_version_info
from cloudwarden.config import load_config
from cloudwarden.agent.explainer import CloudWardenAIAgent

console = Console()


@click.group()
@click.version_option()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--config', type=click.Path(), help='Configuration file path')
@click.pass_context
def cli(ctx, debug: bool, config: str):
    """
    CloudWarden v3 - Revolutionary AI-Powered Cloud Security Platform
    
    Find misconfigurations fast. Ship safer.
    """
    # Setup logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    ctx.obj['debug'] = debug


@cli.command()
@click.option('--ai-test', is_flag=True, help='Test AI agent functionality')
@click.pass_context
def status(ctx, ai_test: bool):
    """Check CloudWarden system status"""
    
    console.print("[bold blue]CloudWarden v3 System Status[/bold blue]")
    
    # Show version info
    version_info = get_version_info()
    
    info_table = Table(title="System Information")
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Status", style="green")
    
    info_table.add_row("Version", version_info['version'])
    info_table.add_row("Organization", version_info['author'])
    
    # Check configuration
    try:
        config = load_config(ctx.obj.get('config_file'))
        info_table.add_row("Configuration", "✅ Loaded")
        
        # Check AI agent if requested
        if ai_test:
            ai_agent = CloudWardenAIAgent(config)
            if ai_agent.is_available():
                info_table.add_row("AI Agent", f"✅ Available ({config.ai_agent.model})")
            else:
                info_table.add_row("AI Agent", "❌ Not Available")
        
    except Exception as e:
        info_table.add_row("Configuration", f"❌ Error: {e}")
    
    console.print(info_table)
    
    # Show available components
    console.print("\n[bold]Available Components:[/bold]")
    for component in version_info['components']:
        console.print(f"  • {component}")


@cli.command()
@click.option('--services', help='Comma-separated AWS services to scan')
@click.option('--regions', help='Comma-separated AWS regions')
@click.option('--output', help='Output file path')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'html', 'markdown']),
              default='json', help='Output format')
@click.pass_context
def scan(ctx, services: str, regions: str, output: str, output_format: str):
    """Run CloudWarden security scan"""
    
    console.print("[bold blue]CloudWarden Security Scan[/bold blue]")
    
    try:
        # Load configuration
        config = load_config(ctx.obj.get('config_file'))
        
        # Override with CLI options
        if services:
            config.scanning.services = services.split(',')
        if regions:
            config.aws.regions = regions.split(',')
        
        console.print(f"Scanning services: {', '.join(config.scanning.services)}")
        console.print(f"Scanning regions: {', '.join(config.aws.regions)}")
        
        # Initialize AI agent
        ai_agent = CloudWardenAIAgent(config)
        if ai_agent.is_available():
            console.print("✅ AI agent ready for enhanced analysis")
        else:
            console.print("⚠️ AI agent not available - using basic analysis")
        
        # Mock scan results for now
        console.print("\n[yellow]🔍 Scanning in progress...[/yellow]")
        
        # Sample findings for demonstration
        sample_findings = [
            {
                'type': 'iam_wildcard_policy',
                'severity': 'High',
                'resource_id': 'arn:aws:iam::123456789012:role/example-role',
                'description': 'IAM role contains policies with wildcard permissions'
            },
            {
                'type': 'public_s3_bucket',
                'severity': 'Medium',
                'resource_id': 'arn:aws:s3:::example-bucket',
                'description': 'S3 bucket allows public read access'
            }
        ]
        
        # Display results
        results_table = Table(title="Security Findings")
        results_table.add_column("Severity", style="red")
        results_table.add_column("Type", style="cyan")
        results_table.add_column("Resource", style="yellow")
        results_table.add_column("AI Analysis", style="green")
        
        for finding in sample_findings:
            # Get AI analysis if available
            ai_summary = "Basic analysis"
            if ai_agent.is_available():
                analysis = ai_agent.analyze_finding(finding)
                ai_summary = analysis.business_impact[:50] + "..." if len(analysis.business_impact) > 50 else analysis.business_impact
            
            results_table.add_row(
                finding['severity'],
                finding['type'],
                finding['resource_id'].split('/')[-1],
                ai_summary
            )
        
        console.print(results_table)
        
        # Save results if output specified
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_format == 'json':
                import json
                with open(output_path, 'w') as f:
                    json.dump({
                        'scan_metadata': {
                            'version': '3.0.0',
                            'services': config.scanning.services,
                            'regions': config.aws.regions
                        },
                        'findings': sample_findings
                    }, f, indent=2)
            
            console.print(f"\n✅ Results saved to: {output_path}")
        
    except Exception as e:
        console.print(f"[red]❌ Scan failed: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command()
def demo():
    """Run CloudWarden demonstration"""
    
    console.print("[bold magenta]🚀 CloudWarden v3 Demo[/bold magenta]")
    console.print("Nova Titan Systems - Revolutionary AI-Powered Cloud Security\n")
    
    # Demo AI capabilities
    console.print("[bold]🤖 AI Agent Demonstration[/bold]")
    
    config = load_config()
    ai_agent = CloudWardenAIAgent(config)
    
    if ai_agent.is_available():
        console.print("✅ Local AI models loaded successfully")
        
        # Demo finding analysis
        demo_finding = {
            'type': 'iam_wildcard_policy',
            'severity': 'Critical',
            'resource_id': 'arn:aws:iam::123456789012:role/admin-role',
            'description': 'Administrative role has unrestricted wildcard permissions (*:*) allowing full AWS access'
        }
        
        console.print("\n[yellow]Analyzing sample security finding...[/yellow]")
        analysis = ai_agent.analyze_finding(demo_finding)
        
        # Display AI analysis
        console.print(f"\n[bold]Business Impact:[/bold]\n{analysis.business_impact}")
        console.print(f"\n[bold]Risk Factors:[/bold]")
        for factor in analysis.risk_factors:
            console.print(f"  • {factor}")
        
        console.print(f"\n[bold]Remediation Steps:[/bold]")
        for i, step in enumerate(analysis.remediation_steps, 1):
            console.print(f"  {i}. {step}")
        
        console.print(f"\n[bold]AI Confidence:[/bold] {analysis.confidence_score:.1%}")
        
    else:
        console.print("❌ AI models not available")
        console.print("To enable AI features:")
        console.print("  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        console.print("  2. Download models: ollama pull llama3.1:8b")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()