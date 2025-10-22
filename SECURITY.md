# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in SnapFlux v2, please report it responsibly:

### How to Report

1. **Email**: Send details to [your-email@domain.com]
2. **GitHub Issues**: Create a private issue (if you have access)
3. **Direct Contact**: Contact the maintainer directly

### What to Include

Please include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Your contact information

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution**: Depends on severity (1-4 weeks)

### Security Considerations

This project handles:
- User credentials (encrypted storage)
- Web automation data
- Excel file generation
- Network communications

### Security Best Practices

- Never commit credentials to the repository
- Use environment variables for sensitive configuration
- Keep dependencies updated
- Run the application in secure environments only

### What NOT to Report

- Issues related to the target website's own security
- Problems with outdated dependencies (use GitHub Issues instead)
- Feature requests (use GitHub Issues instead)
