# Changelog

All notable changes to the Stinger Guardrails Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0a4] - 2025-07-10

### 🛠️ Improvements

#### **Demo Experience**
- Added `--detached` flag to web demo and management console startup scripts
- Fixed timeout issues when running demos through tools/CI environments
- Updated documentation to reflect HTTP (not HTTPS) for web demo
- Simplified startup instructions across all demos

#### **Documentation**
- Corrected web demo README to remove incorrect HTTPS references
- Updated main README with simplified demo startup commands
- Added clear instructions for background mode execution
- Fixed management console startup documentation

#### **Developer Experience**
- Consistent startup patterns across web demo and management console
- Better error handling and status messages in startup scripts
- Added PID tracking for background processes

### 🐛 Bug Fixes
- Fixed web demo server crashes due to tool timeout limitations
- Resolved startup script issues in both demos

## [0.1.0a3] - 2025-07-07

### 🚀 Alpha 3 Release - PyPI Publishing & Management Console

This release completes Phases 11-12, adding the management console and publishing to PyPI.

### ✨ Major Features

#### **Management Console (Phase 11)**
- **Real-time Monitoring**: Live dashboard for all guardrail activity
- **Performance Analytics**: Charts and metrics for system health
- **Audit Log Explorer**: Search and export security audit trails
- **Zero Configuration**: No authentication required, simple deployment
- **Virtual Scrolling**: Handle large log files efficiently
- **Data Retention**: Configure retention policies for logs and metrics

#### **PyPI Publishing (Phase 12)**
- **Package Available**: Install with `pip install stinger-guardrails-alpha`
- **Automated CI/CD**: GitHub Actions for release automation
- **Documentation Updates**: Installation instructions updated
- **Version Management**: Proper versioning with bumpversion

### 🛠️ Improvements

#### **Documentation**
- Fixed outdated API examples in getting_started.md
- Updated preset names to match implementation
- Corrected CLI command examples
- Fixed health monitor import paths

#### **Repository Cleanup**
- Removed 800+ node_modules files from git history
- Cleaned up test backup files and logs
- Updated .gitignore to prevent future issues
- Removed one-time migration scripts

#### **Bug Fixes**
- Fixed management console numpy dependency issue
- Corrected rate limit API in documentation
- Updated health monitor API examples

### 📦 Installation

```bash
pip install stinger-guardrails-alpha==0.1.0a3
```

## [0.1.0a2] - 2025-07-04

### 🚀 Alpha 2 Release - Enhanced Testing & Demo Experience

This release completes Phases 7-10, bringing significant improvements to testing infrastructure, demos, and developer experience.

### ✨ Major Improvements

#### **Testing Infrastructure (Phase 7)**
- **Consolidated Test Suite**: Unified 558 tests with 96%+ code coverage
- **AI-Powered Testing**: Two-tier strategy with sanity and efficacy tests
- **Performance Metrics**: Comprehensive benchmarking for all guardrails
- **Behavioral Tests**: Real-world scenario testing for bypass attempts
- **CI/CD Enhancements**: Pre-commit hooks and local CI checks

#### **Enhanced Demos (Phase 8-10)**
- **Production Web Demo**: Full React frontend with real-time guardrail visualization
- **Performance Monitoring**: Live metrics dashboard with HealthMonitor integration
- **Interactive Panels**: Slide-out panels for guardrails, logs, and performance
- **14+ Guardrails**: Complete showcase of all guardrail types
- **Memory Optimized**: Frontend reduced from 1.4GB to normal levels

#### **Developer Experience**
- **Streamlined Examples**: Reorganized and tested all 9 progressive examples
- **Local CI Script**: Run all checks locally before pushing (`./scripts/local-ci-check.sh`)
- **Better Error Messages**: Clear guidance when setup is incomplete
- **Simplified Demos**: One-command startup for all demos

### 🛠️ Technical Improvements

#### **Web Demo Features**
- **Real-time Updates**: Smart polling for live metrics (no WebSocket complexity)
- **Audit Trail Viewer**: Conversation-aware log filtering
- **Performance Panel**: Request volumes, block rates, response times
- **Guardrail Controls**: Enable/disable guardrails on the fly
- **Export Capabilities**: Download logs and metrics

#### **Code Quality**
- **Test Organization**: Clear separation of unit, integration, and behavioral tests
- **Performance Benchmarks**: Baseline metrics for all components
- **Documentation Updates**: Comprehensive test strategy and architecture docs
- **Clean Repository**: Removed duplicate tests and organized structure

### 📊 Metrics & Performance
- **Test Coverage**: 96%+ across core modules
- **CI Runtime**: ~1.5 minutes for full test suite
- **Bundle Size**: Web demo < 200KB gzipped
- **Response Times**: < 100ms for guardrail processing

### 🔧 Developer Tools
- **Pre-commit Hooks**: Automatic formatting and linting
- **Local CI Checks**: Test before pushing
- **Debug Endpoints**: Built-in troubleshooting tools
- **Performance Tracking**: Issue #59 filed for future enhancements

## [0.1.0a1] - 2025-07-01

### 🎉 Initial Alpha Release

This is the first public alpha release of the Stinger Guardrails Framework - a comprehensive LLM safety toolkit for production environments.

### ✨ Major Features Added

#### **Guardrail System**
- **Multiple Guardrail Types**: Keyword filtering, PII detection, toxicity checking, prompt injection protection, length validation, regex patterns, URL filtering, and code generation detection
- **AI-Powered Guardrails**: Integration with OpenAI's moderation API for advanced content analysis
- **Configurable Actions**: Block, warn, or allow content based on detection results
- **Pipeline Architecture**: Compose multiple guardrails into processing pipelines

#### **Developer Experience**
- **Easy Installation**: `pip install stinger-guardrails-alpha`
- **Quick Setup**: Interactive setup wizard (`stinger setup`) - 90 second onboarding
- **CLI Interface**: Command-line tools for testing and monitoring
- **Multiple Presets**: Ready-to-use configurations for common use cases (customer service, medical, financial)

#### **Production Features**
- **Conversation Context**: Track conversations and maintain context across interactions
- **Rate Limiting**: Global and per-conversation rate limiting with configurable thresholds
- **Audit Trail**: Comprehensive logging for security and compliance
- **Health Monitoring**: System health checks and status reporting
- **API Key Management**: Centralized, secure API key handling

#### **Web Demo**
- **Interactive Demo**: Full-featured web interface for testing guardrails
- **Real-time Chat**: Live chat interface with guardrail feedback
- **Settings Panel**: Dynamic guardrail configuration
- **Audit Logs**: View security audit trail in real-time

### 🔧 Technical Implementation

#### **Architecture**
- **GuardrailInterface**: Unified interface for all guardrail types
- **Configuration Validation**: Comprehensive YAML configuration with schema validation
- **Async/Sync Support**: Full support for both synchronous and asynchronous operations
- **Memory Efficient**: Optimized for production workloads

#### **Security**
- **Production Hardening**: Secure error handling, input validation, and resource protection
- **Encryption**: Secure API key storage and transmission
- **ReDoS Protection**: Advanced regex validation to prevent ReDoS attacks
- **PII Redaction**: Automatic PII redaction in logs and error messages

#### **Testing**
- **Comprehensive Test Suite**: 35+ test files with >90% coverage
- **Multiple Test Types**: Unit, integration, end-to-end, and performance tests
- **Real-world Scenarios**: Customer service and medical bot test scenarios
- **CI/CD Pipeline**: Automated testing across Python 3.8-3.12 and multiple platforms

### 📚 Documentation

#### **Complete Documentation**
- **Getting Started Guide**: Step-by-step tutorials from installation to advanced usage
- **API Reference**: Complete API documentation with examples
- **Configuration Guide**: Comprehensive configuration options and examples
- **Extensibility Guide**: How to create custom guardrails

#### **Examples**
- **9 Progressive Examples**: From basic installation to advanced features
- **Scenario-Based**: Real-world use cases with sample data
- **Working Examples**: All examples tested and verified with pip installation

### 🛠️ Development Tools

#### **CLI Tools**
- `stinger demo` - Run a quick demonstration
- `stinger setup` - Interactive setup wizard
- `stinger check-prompt` - Test individual prompts
- `stinger health` - System health monitoring

#### **Configuration Options**
- **YAML Configuration**: Human-readable configuration files
- **Environment Variables**: Runtime configuration via environment
- **Preset Configurations**: Pre-built configurations for common scenarios

### 🚀 Installation & Quick Start

```bash
# Install
pip install stinger-guardrails-alpha

# Quick setup
stinger setup

# Run demo
stinger demo

# Test a prompt
stinger check-prompt "Your test message here"
```

### 📊 Package Details

- **Package Name**: `stinger-guardrails-alpha`
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Optional Dependencies**: 
  - `[ai]` - OpenAI integration
  - `[dev]` - Development tools
  - `[web-demo]` - Web interface
  - `[all]` - Everything included

### 🔒 Security Features

- **API Key Security**: Secure handling with multiple storage options
- **Input Validation**: Comprehensive input sanitization and validation
- **Error Sanitization**: Production-safe error messages
- **Audit Logging**: Complete security audit trail
- **Rate Limiting**: Protection against abuse and resource exhaustion

### ⚡ Performance

- **Fast Processing**: Optimized for production workloads
- **Memory Efficient**: Minimal memory footprint
- **Concurrent Processing**: Support for high-throughput scenarios
- **Configurable Limits**: Tune performance for your environment

### 🎯 Use Cases

- **Customer Service Bots**: PII protection and professional communication
- **Medical Chatbots**: HIPAA-compliant conversation filtering
- **Financial Services**: Sensitive data protection and compliance
- **Educational Platforms**: Content moderation and safety
- **Enterprise AI**: Production-grade AI safety and monitoring

### 🤝 Contributing

This is an alpha release. We welcome feedback and contributions:
- **Issue Reporting**: [GitHub Issues](https://github.com/virtualsteve-star/stinger/issues)
- **Feature Requests**: Submit via GitHub Issues
- **Security Issues**: Follow responsible disclosure

### ⚠️ Alpha Release Notes

This is an **alpha release** intended for:
- **Testing and Evaluation**: Try the framework in development environments
- **Feedback Collection**: Help us improve before stable release
- **Early Adoption**: For teams comfortable with alpha software

**Not recommended for production use** until stable release.

### 📝 Known Limitations

- **Alpha Status**: APIs may change before stable release
- **OpenAI Dependency**: Some features require OpenAI API access
- **Documentation**: Continuously improving based on feedback

### 🙏 Acknowledgments

Built with:
- **OpenAI**: For AI-powered guardrail capabilities
- **FastAPI**: For web demo backend
- **React**: For interactive web interface
- **pytest**: For comprehensive testing

---

For detailed migration guides and breaking changes, see [UPGRADING.md](UPGRADING.md).

For the latest updates, visit our [GitHub repository](https://github.com/virtualsteve-star/stinger).