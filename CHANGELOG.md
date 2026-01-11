# Changelog

All notable changes to Haggl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Real-time SSE event streaming to frontend
- Payment agent with mock Stripe/ACH support
- Browserbase automation for complex payments
- x402 protocol integration for blockchain payments

## [1.0.0] - 2026-01-11

### Added
- **Multi-Agent Architecture**: Modular agent system with 6 specialized agents
  - Message Agent: WhatsApp/SMS communication via Vonage
  - Calling Agent: Voice negotiations via Vapi
  - Sourcing Agent: Vendor discovery via Exa.ai
  - Evaluation Agent: AI-powered vendor scoring via Voyage AI
  - Payment Agent: Automated payment execution
  - x402 Agent: Blockchain payment bridge

- **Real-Time Dashboard**: Live order tracking with SSE
  - Stage progress visualization
  - Call transcript display
  - Vendor comparison cards
  - One-click approval flow

- **MongoDB Integration**: Full data persistence
  - Conversation history
  - Order tracking
  - Call transcripts
  - Vendor embeddings
  - Business profiles

- **Onboarding Flow**: Business setup wizard
  - Business profile capture
  - Product catalog selection
  - Delivery preferences

- **Parallel Vendor Calling**: Concurrent negotiations
  - Up to 3 simultaneous calls
  - Real-time status updates
  - Automatic best-price selection

### Security
- Environment-based secrets management
- Input validation with Pydantic
- Webhook signature verification

### Documentation
- Comprehensive README
- API documentation
- Architecture diagrams
- Contributing guidelines

## [0.2.0] - 2026-01-08

### Added
- Vonage WhatsApp integration
- OpenAI function calling for message agent
- Sourcing agent with Exa.ai

### Changed
- Migrated from Twilio to Vonage
- Restructured agent directories

### Fixed
- Webhook endpoint methods (GET/POST support)

## [0.1.0] - 2026-01-05

### Added
- Initial Vapi calling agent
- FastAPI server setup
- Basic state machine for calls
- Environment configuration

---

[Unreleased]: https://github.com/haggl/haggl/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/haggl/haggl/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/haggl/haggl/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/haggl/haggl/releases/tag/v0.1.0
