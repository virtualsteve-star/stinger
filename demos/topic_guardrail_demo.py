#!/usr/bin/env python3
"""
Topic Guardrail Demo

This demo showcases the topic guardrail capabilities including:
- Allow/deny list modes
- Case sensitivity
- Regex pattern matching
- Confidence thresholds
- Different use cases
"""

import asyncio
import yaml
from pathlib import Path
from stinger.guardrails.topic_guardrail import TopicGuardrail
from stinger.core.pipeline import GuardrailPipeline


class TopicGuardrailDemo:
    """Demo class for topic guardrail capabilities."""
    
    def __init__(self):
        self.demo_configs = {
            'customer_service_whitelist': {
                'name': 'customer_service_whitelist',
                'mode': 'allow',
                'allow_topics': [
                    'account', 'billing', 'support', 'help', 'service',
                    'payment', 'refund', 'technical', 'login', 'password'
                ],
                'confidence_threshold': 0.7
            },
            'content_moderation_blacklist': {
                'name': 'content_moderation_blacklist',
                'mode': 'deny',
                'deny_topics': [
                    'hate speech', 'violence', 'harassment', 'discrimination',
                    'threats', 'bullying', 'inappropriate', 'offensive'
                ],
                'confidence_threshold': 0.6
            },
            'academic_content': {
                'name': 'academic_content',
                'mode': 'both',
                'allow_topics': [
                    'research', 'study', 'education', 'learning', 'academic',
                    'scholarly', 'university', 'college', 'course', 'assignment'
                ],
                'deny_topics': [
                    'cheating', 'plagiarism', 'academic dishonesty', 'unauthorized help'
                ],
                'confidence_threshold': 0.8
            },
            'regex_filter': {
                'name': 'regex_filter',
                'mode': 'deny',
                'use_regex': True,
                'deny_topics': [
                    r'\b(spam|scam|phishing)\b',
                    r'\b(click here|free money|lottery)\b',
                    r'\b(viagra|cialis|weight loss)\b'
                ],
                'confidence_threshold': 0.9
            }
        }
        
        self.test_content = [
            # Customer service content
            "I need help with my account billing and payment issues",
            "Can you help me reset my password?",
            "I want to discuss politics and religion",
            
            # Content moderation content
            "This is a normal conversation about technology",
            "I want to make threats and bully people",
            "This content contains hate speech and discrimination",
            
            # Academic content
            "I need help with my research assignment",
            "Can you help me cheat on my exam?",
            "I want to discuss sports and entertainment",
            
            # Spam content
            "Click here for free money and lottery prizes",
            "Buy viagra and cialis for weight loss",
            "This is legitimate business content"
        ]
    
    async def run_single_guardrail_demo(self, config_name: str, config: dict):
        """Run demo for a single guardrail configuration."""
        print(f"\n{'='*60}")
        print(f"DEMO: {config_name.upper()}")
        print(f"{'='*60}")
        
        # Create guardrail
        guardrail_obj = TopicGuardrail(config)
        print(f"Guardrail: {guardrail_obj.name}")
        print(f"Mode: {guardrail_obj.mode}")
        print(f"Allow topics: {len(guardrail_obj.allow_topics)}")
        print(f"Deny topics: {len(guardrail_obj.deny_topics)}")
        print(f"Confidence threshold: {guardrail_obj.confidence_threshold}")
        print(f"Case sensitive: {guardrail_obj.case_sensitive}")
        print(f"Use regex: {guardrail_obj.use_regex}")
        
        # Test content
        print(f"\nTesting {len(self.test_content)} content samples:")
        print("-" * 40)
        
        for i, content in enumerate(self.test_content, 1):
            result = await guardrail_obj.analyze(content)
            
            status = "🚫 BLOCKED" if result.blocked else "✅ ALLOWED"
            print(f"{i:2d}. {status} | {content[:50]}{'...' if len(content) > 50 else ''}")
            print(f"    Reason: {result.reason}")
            print(f"    Confidence: {result.confidence:.2f}")
            print()
    
    async def run_pipeline_demo(self):
        """Run demo with multiple guardrails in a pipeline."""
        print(f"\n{'='*60}")
        print("PIPELINE DEMO: Multiple Topic Guardrails")
        print(f"{'='*60}")
        
        # Create temporary config file for pipeline
        import tempfile
        import yaml
        
        pipeline_config = {
            'version': '1.0',
            'pipeline': {
                'input': [
                    {
                        'type': 'content_moderation',
                        'name': 'customer_service_guardrail',
                        'mode': 'allow',
                        'allow_topics': ['account', 'billing', 'support', 'help'],
                        'confidence_threshold': 0.5,
                        'enabled': True,
                        'on_error': 'block'
                    },
                    {
                        'type': 'content_moderation',
                        'name': 'content_moderation_guardrail',
                        'mode': 'deny',
                        'deny_topics': ['hate speech', 'violence', 'threats'],
                        'confidence_threshold': 0.6,
                        'enabled': True,
                        'on_error': 'block'
                    }
                ],
                'output': []
            }
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(pipeline_config, f)
            temp_config_path = f.name
        
        try:
            pipeline = GuardrailPipeline(temp_config_path)
            
            # Test content
            test_content = [
                "I need help with my account billing",
                "I want to make threats and use hate speech",
                "This is a normal conversation about technology",
                "Can you help me with support issues?"
            ]
            
            print("Testing pipeline with multiple guardrails:")
            print("-" * 40)
            
            for i, content in enumerate(test_content, 1):
                print(f"\n{i}. Content: {content}")
                
                # Check input
                input_result = pipeline.check_input(content)
                print(f"   Input check: {'🚫 BLOCKED' if input_result['blocked'] else '✅ ALLOWED'}")
                if input_result['reasons']:
                    print(f"   Reasons: {', '.join(input_result['reasons'])}")
                
                # Check output (same content for demo)
                output_result = pipeline.check_output(content)
                print(f"   Output check: {'🚫 BLOCKED' if output_result['blocked'] else '✅ ALLOWED'}")
                if output_result['reasons']:
                    print(f"   Reasons: {', '.join(output_result['reasons'])}")
        
        finally:
            # Clean up temp file
            Path(temp_config_path).unlink()
    
    async def run_analysis_demo(self):
        """Run demo showing analysis capabilities."""
        print(f"\n{'='*60}")
        print("ANALYSIS DEMO: Content Analysis")
        print(f"{'='*60}")
        
        # Create guardrail for analysis
        config = {
            'name': 'analysis_guardrail',
            'mode': 'both',
            'allow_topics': ['technology', 'science', 'education'],
            'deny_topics': ['politics', 'religion', 'gambling'],
            'confidence_threshold': 0.0  # Show all matches
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Test content
        analysis_content = [
            "I want to discuss technology and science education",
            "This involves politics, religion, and gambling",
            "Let's talk about technology but also politics",
            "Pure science and education content"
        ]
        
        print("Content analysis results:")
        print("-" * 40)
        
        for i, content in enumerate(analysis_content, 1):
            print(f"\n{i}. Content: {content}")
            
            # Analyze content
            analysis = guardrail_obj.analyze(content)
            
            print(f"   Confidence: {analysis['confidence']:.2f}")
            print(f"   Allow matches: {analysis['matches']['allow']}")
            print(f"   Deny matches: {analysis['matches']['deny']}")
            print(f"   Total matches: {analysis['details']['total_matches']}")
    
    async def run_performance_demo(self):
        """Run demo showing performance characteristics."""
        print(f"\n{'='*60}")
        print("PERFORMANCE DEMO: Large Topic Lists")
        print(f"{'='*60}")
        
        # Create guardrail with many topics
        allow_topics = [f"topic_{i}" for i in range(50)]
        deny_topics = [f"deny_{i}" for i in range(50)]
        
        config = {
            'name': 'performance_guardrail',
            'mode': 'both',
            'allow_topics': allow_topics,
            'deny_topics': deny_topics,
            'confidence_threshold': 0.5
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Performance test
        import time
        
        test_content = [
            "This is content with topic_25 and deny_30",
            "No matches in this content",
            "Multiple matches: topic_10, topic_20, deny_15",
            "Just some random content without matches"
        ]
        
        print(f"Testing with {len(allow_topics)} allow topics and {len(deny_topics)} deny topics")
        print("-" * 40)
        
        start_time = time.time()
        
        for i, content in enumerate(test_content, 1):
            result = await guardrail_obj.analyze(content)
            
            print(f"{i}. Content: {content[:40]}...")
            print(f"   Action: {result.blocked}")
            print(f"   Confidence: {result.confidence:.2f}")
            if hasattr(result, 'details') and 'total_matches' in result.details:
                print(f"   Total matches: {result.details['total_matches']}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\nPerformance: {len(test_content)} checks in {elapsed:.3f} seconds")
        print(f"Average: {elapsed/len(test_content):.3f} seconds per check")
    
    async def run_all_demos(self):
        """Run all demos."""
        print("TOPIC GUARDRAIL DEMO")
        print("=" * 60)
        print("This demo showcases topic guardrail capabilities including")
        print("allow/deny lists, different modes, regex support, and more.")
        
        # Run individual guardrail demos
        for config_name, config in self.demo_configs.items():
            await self.run_single_guardrail_demo(config_name, config)
        
        # Run pipeline demo
        await self.run_pipeline_demo()
        
        # Run analysis demo
        await self.run_analysis_demo()
        
        # Run performance demo
        await self.run_performance_demo()
        
        print(f"\n{'='*60}")
        print("DEMO COMPLETE")
        print(f"{'='*60}")
        print("The topic guardrail provides flexible content filtering based on")
        print("topic allow/deny lists with support for:")
        print("• Multiple modes (allow, deny, both)")
        print("• Case sensitivity control")
        print("• Regex pattern matching")
        print("• Confidence thresholds")
        print("• Performance optimization")
        print("• Integration with guardrail pipelines")


async def main():
    """Main demo function."""
    demo = TopicGuardrailDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main()) 