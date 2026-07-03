# Antigravity2RPM

**Antigravity2RPM** is an intelligent, agent-powered automation script that generates RPM packages for the [Google Antigravity IDE](https://antigravity.google) and its associated CLI tools. 

By leveraging the official `agy` (Antigravity CLI) under the hood, this tool avoids the need for standalone API keys or complex SDK configurations, seamlessly inheriting your existing IDE subscription authentication to dynamically fetch the latest release versions and build the packages!

## 🚀 Features

- **Dynamic Download Fetching**: Agent-powered retrieval of the latest IDE and Agent Linux x64 tarballs.
- **Hybrid AI Strategy**:
  - Uses `agy -p` (Antigravity CLI) locally for zero-config authentication inheriting IDE context.
  - Falls back to `google-antigravity` Python SDK (using `GEMINI_API_KEY`) for automated CI/CD runners.
- **Multi-Packaging Support**:
  - Automatically generates `.rpm` using `rpmbuild` (Fedora/RHEL).
  - Automatically generates `.deb` using `dpkg-deb` (Debian/Ubuntu).
- **Desktop Integration**: Installs `.desktop` shortcuts for GNOME/KDE automatically.
- **CI/CD Pipeline**: GitHub Actions workflow to build RPM and DEB packages and publish them as Pre-Releases directly in the GitHub repository.
- **Install Script**: Quick `curl ... | bash` initialization script setting up dependencies and `venv`.

## 🛠️ Requirements

- **Fedora/RHEL**: `rpm-build` and `rpmdevtools`
- **Debian/Ubuntu**: `dpkg-dev`
- `python3` (and optionally `python3-venv`)
- Antigravity IDE CLI (`agy`) installed OR `GEMINI_API_KEY` exported.

## 📚 Documentation

Check out the [Documentation folder](docs/usage.md) for detailed instructions on usage, requirements, and how it works.

---

### Authors
- [RLuf](https://github.com/RLuf)
- **GeGe** (Google DeepMind Antigravity AI) - Co-Author & Logic Architect

### License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
