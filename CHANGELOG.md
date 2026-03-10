# Changelog

All notable changes to this project will be documented in this file.

## [0.0.4] - 2026-03-11

### Changed
- Simplified config flow for better user experience
- Auto-detection of OpenVPN add-on
- Clearer setup instructions without technical jargon
- Removed confusing API host/port fields for basic users

### Fixed
- Config flow descriptions now render properly
- HACS validation passes all checks
- Translation strings comply with Home Assistant standards
- GitHub Actions updated to Node.js 24

### Added
- Smart auto-setup flow that detects if add-on is running
- Simplified upload instructions
- Comprehensive troubleshooting guide

## [0.0.3] - 2026-03-10

### Added
- Initial release
- OpenVPN client integration for Home Assistant
- Dashboard switch to toggle VPN connection
- Status, IP, and uptime sensors
- File upload support for .ovpn configurations
- REST API for VPN management
- Multi-profile support
- HACS compatibility
