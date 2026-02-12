# Changelog

All notable changes to the Gmail Check MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-02-12

### 🔧 Improved
- **Error Handling Consistency**: All error scenarios now return success=True with empty matched_emails list instead of error structures
- **Connection Failure Handling**: Connection failures return consistent success structure with empty results rather than throwing exceptions
- **Empty Filter Handling**: Empty email_filters parameter now returns success structure instead of validation error
- **Missing Credentials Handling**: Missing authentication parameters return consistent success structure

### 🐛 Fixed
- **Structure Consistency**: Fixed inconsistent return structures between success and error cases
- **Resource Cleanup**: Improved IMAP connection cleanup on errors to prevent resource leaks
- **Exception Propagation**: Prevented exceptions from breaking the consistent response format

### 📈 User Experience  
- **Predictable Responses**: All function calls now return the same structure regardless of success/failure
- **Empty Lists vs Errors**: Programs can now handle empty results more easily than error messages
- **Better Debugging**: Enhanced logging and error status information in statistics

## [1.1.1] - 2026-02-12

### 🐛 Fixed
- **Background Monitoring Immediate Execution**: Fixed critical issue where background monitoring mode did not perform immediate check on startup
- **Monitoring Loop Logic**: Restructured wait logic to check stop event properly and perform initial check immediately
- **Thread Management**: Improved monitoring thread lifecycle and proper shutdown handling

### 🔧 Improved
- **Background Mode Testing**: Enhanced test scripts with comprehensive background mode verification
- **Configuration Examples**: Updated configuration examples with proper cache settings for testing
- **Debugging Tools**: Added detailed MCP inspector and validation tools

### 📚 Documentation  
- Added comprehensive test scripts for background mode functionality
- Enhanced troubleshooting guides for background monitoring
- Updated validation and testing procedures

## [1.1.0] - 2026-02-12

### 🆕 Added
- **Enhanced Time Range Control**: New `time_range_hours` parameter (1-720 hours) for precise time-based email filtering
- **Cache Management**: New `use_cache` parameter to control cache behavior and enable full rescans
- **Version Control System**: Complete version management with automatic update capabilities
- **Update Script**: Automated update script (`update.sh`) with configuration backup
- **Enhanced Documentation**: Comprehensive parameter examples and troubleshooting guides

### 🔧 Improved
- **Parameter Validation**: Enhanced JSON Schema with proper validation rules for all parameters
- **MCP Compatibility**: Better error handling and protocol compliance
- **Configuration Management**: Improved example configurations with all new parameters
- **Test Coverage**: Updated test files with new parameter examples

### 📚 Documentation
- Updated README.md with comprehensive parameter documentation
- Enhanced MCP_DEPLOYMENT.md with new parameter descriptions
- Added version management and update instructions
- Improved troubleshooting guides

### 🔧 Technical Changes
- Enhanced execution logic to handle time_range_hours override of days_back
- Improved cache logic with optional bypass capability
- Better logging and debug information for new parameters
- Updated MCP server schema definitions

## [1.0.0] - 2024-12-12

### 🆕 Initial Release
- **Gmail IMAP Integration**: Complete Gmail email checking with app password authentication
- **Smart Email Filtering**: Filter by sender, subject patterns, and date ranges
- **Intelligent Caching**: 30-minute cache with hash-based deduplication to avoid duplicates
- **MCP Protocol Support**: Full Model Context Protocol compatibility for AI agents
- **Background Monitoring**: Continuous email monitoring with configurable intervals
- **Multi-Language Support**: Chinese and English interface support
- **Secure Configuration**: Git-ignored local configuration with template examples

### 🔧 Core Features
- High-performance IMAP operations with connection reuse
- Comprehensive error handling and validation
- Framework-agnostic design for maximum compatibility
- OpenAI Function Calling JSON Schema support
- Claude Desktop integration support

### 📚 Documentation
- Comprehensive README with installation and usage guides
- MCP deployment documentation
- Skill generation rules and development standards
- Configuration templates and security guidelines

---

## Version Naming Convention

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR version** (X.y.z): Incompatible API changes
- **MINOR version** (x.Y.z): New functionality in backward compatible manner  
- **PATCH version** (x.y.Z): Backward compatible bug fixes

## Compatibility Matrix

| Version | MCP Protocol | Python | Key Features |
|---------|-------------|--------|--------------|
| 1.1.0   | 2024-11-05  | 3.7+   | Time range control, Cache management |
| 1.0.0   | 2024-11-05  | 3.7+   | Basic Gmail integration, MCP support |

## Upgrade Notes

### From 1.0.0 to 1.1.0

**New Parameters Available:**
- `time_range_hours`: Provides hour-level precision (1-720 hours), overrides `days_back`
- `use_cache`: Controls cache behavior, set to `false` for full rescans

**Breaking Changes:**
- None - fully backward compatible

**Migration Steps:**
1. Run update script: `./update.sh`
2. Update your configuration to use new parameters if needed
3. Test with: `python3 mcp_server.py --test`

**Configuration Updates:**
```json
{
  "time_range_hours": 24,  // New: replaces days_back for precise control
  "use_cache": true        // New: control cache behavior
}
```

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/baddif/mcp-server-gmail-check/issues)
- 📖 **Documentation**: [README.md](README.md) and [MCP_DEPLOYMENT.md](MCP_DEPLOYMENT.md)
- 🔄 **Updates**: Use `./update.sh` for automatic updates