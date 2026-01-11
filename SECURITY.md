# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously at Haggl. If you discover a security vulnerability, please report it responsibly.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email us at: **security@haggl.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

### What to Expect

1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Assessment**: We'll assess the vulnerability within 7 days
3. **Resolution**: Critical issues will be patched within 30 days
4. **Disclosure**: We'll coordinate disclosure timing with you

### Scope

The following are in scope:
- Authentication/Authorization bypasses
- Data exposure vulnerabilities
- API security issues
- Payment processing vulnerabilities
- Injection attacks (SQL, NoSQL, Command)
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)

### Out of Scope

- Denial of Service attacks
- Social engineering
- Physical security
- Issues in dependencies (report to upstream)

## Security Best Practices

### For Operators

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Rotate keys regularly
3. **MongoDB**: Use authentication and network restrictions
4. **HTTPS**: Always use TLS in production
5. **Updates**: Keep dependencies updated

### For Contributors

1. **Secrets**: Never hardcode secrets
2. **Input Validation**: Validate all user inputs
3. **Dependencies**: Use `pip-audit` and `npm audit`
4. **Logging**: Never log sensitive data

## Security Features

Haggl implements several security measures:

- **Authentication**: JWT-based API authentication
- **Encryption**: TLS for data in transit
- **Secrets Management**: Environment-based configuration
- **Input Validation**: Pydantic models for all inputs
- **Rate Limiting**: API rate limiting (configurable)
- **Audit Logging**: All actions logged to MongoDB

## Acknowledgments

We thank the following researchers for responsible disclosure:

*No reports yet - be the first!*
