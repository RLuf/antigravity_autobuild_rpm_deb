# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-03

### Added
- **Dynamic Download Fetching**: Agent-powered retrieval of the latest IDE and Agent Linux x64 tarballs.
- **Hybrid AI Strategy**:
  - Uses `agy -p` (Antigravity CLI) locally for zero-config authentication inheriting IDE context.
  - Falls back to `google-antigravity` Python SDK (using `GEMINI_API_KEY`) for automated CI/CD runners.
- **Multi-Packaging Support**:
  - Automatically generates `.rpm` using `rpmbuild`.
  - Automatically generates `.deb` using `dpkg-deb`.
- **Desktop Integration**: Installs `.desktop` shortcuts for GNOME/KDE automatically.
- **CI/CD Pipeline**: GitHub Actions workflow to build RPM and DEB packages and publish them as Pre-Releases directly in the GitHub repository.
- **Install Script**: Quick `curl ... | bash` initialization script setting up dependencies and `venv`.
