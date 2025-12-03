# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of NOF1 Tracker seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Do

1. **Email us directly** at daniel@lagowski.es
2. **Include the following information**:
   - Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
   - Full path of the affected source file(s)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact assessment of the vulnerability

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Initial Assessment**: Within 7 days, we will provide an initial assessment
- **Resolution Timeline**: We aim to resolve critical issues within 30 days
- **Credit**: We will credit reporters in our release notes (unless you prefer anonymity)

## Security Best Practices for Users

### Environment Variables

- **Never commit `.env` files** to version control
- Use strong, unique passwords for database connections
- Rotate credentials regularly
- Use environment-specific configurations

### Database Security

- Use the principle of least privilege for database users
- Enable SSL/TLS for database connections in production
- Regularly backup your database
- Keep PostgreSQL updated to the latest stable version

### Docker Security

- Don't run containers as root in production
- Use official base images and keep them updated
- Scan images for vulnerabilities before deployment
- Limit container resources and capabilities

### Network Security

- Use HTTPS for all external connections
- Implement rate limiting for API endpoints
- Use firewalls to restrict database access
- Consider using a VPN for sensitive operations

## Known Security Considerations

### Data Collection

This application collects publicly available data from nof1.ai. Users should:

- Respect the target website's terms of service
- Implement appropriate rate limiting
- Not use collected data for unauthorized purposes

### Credential Management

- Database credentials should be stored securely
- API keys should never be committed to version control
- Use secret management solutions in production environments

## Security Updates

Security updates will be announced through:

- GitHub Security Advisories
- Release notes
- Direct communication for critical vulnerabilities

## Contact

For security-related inquiries, please contact:

- **Email**: daniel@lagowski.es
- **GitHub**: Open an issue with the "security" label for non-sensitive questions

Thank you for helping keep NOF1 Tracker secure!
