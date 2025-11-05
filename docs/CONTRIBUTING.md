Contributing to SnapFlux v2

Terima kasih atas minat Anda untuk berkontribusi pada SnapFlux v2! Kami menyambut kontribusi dari semua orang yang ingin membantu meningkatkan project ini.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

Project ini mengikuti [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Dengan berpartisipasi, Anda setuju untuk mematuhi kode etik ini.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Git
- Chrome/Chromium browser
- Basic knowledge of Python, Selenium, and web automation

### Fork and Clone

1. Fork repository ini
2. Clone fork Anda:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Snapflux-v2.git
   cd Snapflux-v2
   ```

## 🔧 Development Setup

### 1. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
# At minimum, set:
# CHROME_BINARY_PATH=path/to/your/chrome.exe
# CHROMEDRIVER_PATH=path/to/your/chromedriver.exe
```

### 3. Account Setup

```bash
# Copy account template
cp akun/akun.xlsx.example akun/akun.xlsx

# Edit akun.xlsx with test account data
# Note: Use test accounts only, never commit real credentials
```

### 4. Verify Setup

```bash
# Run basic tests
python -m pytest tests/ -v

# Run the application in test mode
python main.py
```

## 🤝 How to Contribute

### Types of Contributions

Kami menyambut berbagai jenis kontribusi:

- **Bug Reports**: Laporkan bug yang Anda temukan
- **Feature Requests**: Usulkan fitur baru
- **Code Contributions**: Perbaikan bug atau implementasi fitur
- **Documentation**: Perbaikan atau penambahan dokumentasi
- **Testing**: Menambah test coverage
- **Performance**: Optimasi performa

### Areas That Need Help

- 🔍 **Enhanced Error Handling**: Perbaikan error handling untuk edge cases
- 🧪 **Test Coverage**: Menambah unit tests dan integration tests
- 📚 **Documentation**: Perbaikan README dan dokumentasi kode
- 🚀 **Performance**: Optimasi kecepatan dan memory usage
- 🔒 **Security**: Peningkatan keamanan dan input validation
- 🌐 **Cross-platform**: Support untuk Linux dan macOS

## 📝 Coding Standards

### Python Style Guide

Project ini mengikuti PEP 8 dengan beberapa pengecualian:

```bash
# Format code dengan black
black src/ tests/ main.py

# Check linting dengan flake8
flake8 src/ tests/ main.py

# Type checking dengan mypy
mypy src/
```

### Code Structure

- **Functions**: Gunakan descriptive names, maksimal 50 karakter
- **Comments**: Gunakan bahasa Indonesia untuk business logic, English untuk technical
- **Docstrings**: Gunakan format Google style
- **Imports**: Group imports: standard library, third-party, local imports

### Example Code Style

```python
def login_direct(username: str, pin: str) -> WebDriver:
    """
    Melakukan login langsung ke portal merchant.

    Args:
        username: Username atau email untuk login
        pin: PIN untuk autentikasi

    Returns:
        WebDriver: Driver instance jika login berhasil, None jika gagal

    Raises:
        AuthenticationError: Jika login gagal setelah retry maksimal
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Login gagal untuk {username}: {str(e)}")
        raise AuthenticationError(f"Login gagal: {str(e)}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_validators.py -v
```

### Writing Tests

- **Unit Tests**: Test individual functions dan methods
- **Integration Tests**: Test interaction antara components
- **Fixtures**: Gunakan fixtures untuk setup test data

### Test Structure

```python
def test_validate_username_valid():
    """Test validasi username dengan input yang valid."""
    # Arrange
    username = "test@example.com"

    # Act
    result = validate_username(username)

    # Assert
    assert result is True

def test_validate_username_invalid():
    """Test validasi username dengan input yang tidak valid."""
    # Arrange
    username = "invalid-username"

    # Act
    result = validate_username(username)

    # Assert
    assert result is False
```

## 📤 Pull Request Process

### Before Submitting

1. **Check Existing Issues**: Pastikan tidak ada issue yang sama
2. **Create Issue**: Buat issue terlebih dahulu untuk diskusi (opsional)
3. **Create Branch**: Buat branch baru untuk feature/fix
   ```bash
   git checkout -b feature/your-feature-name
   # atau
   git checkout -b fix/your-bug-fix
   ```

### Development Workflow

1. **Make Changes**: Implementasi perubahan Anda
2. **Test Changes**: Pastikan semua test pass
3. **Update Documentation**: Update README jika diperlukan
4. **Commit Changes**: Gunakan conventional commits
   ```bash
   git commit -m "feat: add new validation function"
   git commit -m "fix: resolve login timeout issue"
   git commit -m "docs: update installation instructions"
   ```

### Pull Request Guidelines

- **Title**: Gunakan conventional commit format
- **Description**: Jelaskan perubahan yang dibuat dan mengapa
- **Screenshots**: Jika ada perubahan UI, sertakan screenshot
- **Testing**: Jelaskan bagaimana Anda test perubahan ini
- **Breaking Changes**: Jelaskan jika ada breaking changes

### PR Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented if necessary)
```

## 🐛 Issue Reporting

### Before Creating an Issue

1. **Search Existing Issues**: Pastikan issue belum ada
2. **Check Documentation**: Pastikan sudah membaca README dan dokumentasi
3. **Try Latest Version**: Pastikan menggunakan versi terbaru

### Bug Report Template

```markdown
## Bug Description

Clear and concise description of the bug.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9.7]
- Chrome Version: [e.g., 120.0.6099.71]
- Project Version: [e.g., 2.0.1]

## Additional Context

Add any other context about the problem here.
```

### Feature Request Template

```markdown
## Feature Description

Clear and concise description of the feature you'd like to see.

## Use Case

Describe the problem this feature would solve or the benefit it would provide.

## Proposed Solution

Describe your proposed solution or implementation ideas.

## Alternatives Considered

Describe any alternative solutions or features you've considered.

## Additional Context

Add any other context or screenshots about the feature request here.
```

## 📚 Resources

### Documentation

- [README.md](README.md) - Main project documentation
- [API Documentation](docs/api.md) - API reference (if available)
- [Configuration Guide](docs/config.md) - Configuration options

### External Resources

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 🎯 Getting Help

Jika Anda memerlukan bantuan:

1. **GitHub Discussions**: Untuk pertanyaan umum dan diskusi
2. **GitHub Issues**: Untuk bug reports dan feature requests
3. **Email**: [your-email@domain.com] untuk pertanyaan sensitif

## 🙏 Recognition

Kontributor akan diakui dalam:

- README.md contributors section
- Release notes
- GitHub contributors page

Terima kasih telah berkontribusi pada SnapFlux v2! 🚀
