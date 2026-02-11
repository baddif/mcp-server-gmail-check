#!/bin/bash

# Gmail Check MCP Server Update Script
# This script helps existing users update their Gmail Check MCP Server installation
# to the latest version while preserving their configuration.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project information
REPO_URL="https://github.com/baddif/mcp-server-gmail-check.git"
PROJECT_NAME="Gmail Check MCP Server"

echo -e "${BLUE}🔄 $PROJECT_NAME Update Script${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "This doesn't appear to be a Git repository."
        print_info "Please run this script from the mcp-server-gmail-check directory."
        exit 1
    fi
}

# Check if we have the correct remote
check_remote() {
    local remote_url=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$remote_url" != *"mcp-server-gmail-check"* ]]; then
        print_warning "Remote URL doesn't match expected repository."
        print_info "Expected: $REPO_URL"
        print_info "Found: $remote_url"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Backup configuration files
backup_config() {
    print_info "Backing up configuration files..."
    
    # Create backup directory with timestamp
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup important files
    if [ -f "gmail_config_local.json" ]; then
        cp "gmail_config_local.json" "$backup_dir/"
        print_status "Backed up gmail_config_local.json"
    fi
    
    if [ -f "claude_desktop_config.json" ]; then
        cp "claude_desktop_config.json" "$backup_dir/"
        print_status "Backed up claude_desktop_config.json"
    fi
    
    # Backup any custom files
    if [ -f "custom_config.json" ]; then
        cp "custom_config.json" "$backup_dir/"
        print_status "Backed up custom_config.json"
    fi
    
    echo "📁 Backups saved to: $backup_dir"
}

# Check for uncommitted changes
check_uncommitted_changes() {
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes in your repository."
        echo "Uncommitted files:"
        git diff --name-only HEAD
        echo
        read -p "Do you want to stash these changes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Auto-stash before update $(date)"
            print_status "Changes stashed successfully"
        else
            print_error "Please commit or stash your changes before updating."
            exit 1
        fi
    fi
}

# Get current version
get_current_version() {
    if [ -f "version.py" ]; then
        python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from version import __version__
    print(__version__)
except ImportError:
    print('unknown')
"
    else
        echo "unknown"
    fi
}

# Update repository
update_repo() {
    print_info "Fetching latest changes..."
    git fetch origin main
    
    # Check if updates are available
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    
    if [ "$local_commit" = "$remote_commit" ]; then
        print_status "You are already up to date!"
        return 0
    fi
    
    print_info "Updates available. Pulling changes..."
    git pull origin main
    print_status "Repository updated successfully"
    return 1  # Indicates updates were applied
}

# Update Python dependencies
update_dependencies() {
    print_info "Updating Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --upgrade
        print_status "Dependencies updated successfully"
    else
        print_warning "requirements.txt not found, skipping dependency update"
    fi
}

# Validate installation
validate_installation() {
    print_info "Validating installation..."
    
    # Test Python imports
    if python3 -c "from gmail_check_skill import GmailCheckSkill; print('✅ Gmail Check Skill import successful')" 2>/dev/null; then
        print_status "Gmail Check Skill import successful"
    else
        print_error "Gmail Check Skill import failed"
        return 1
    fi
    
    # Test MCP server
    if python3 mcp_server.py --test > /dev/null 2>&1; then
        print_status "MCP Server test successful"
    else
        print_warning "MCP Server test failed - may need configuration"
    fi
    
    # Check version
    local new_version=$(get_current_version)
    print_status "Updated to version: $new_version"
}

# Restore configuration files
restore_config() {
    print_info "Configuration files were preserved during update"
    
    # Check if gmail_config_local.json exists
    if [ ! -f "gmail_config_local.json" ]; then
        print_warning "gmail_config_local.json not found"
        if [ -f "gmail_config_example.json" ]; then
            print_info "Copy gmail_config_example.json to gmail_config_local.json and configure it"
            echo "cp gmail_config_example.json gmail_config_local.json"
        fi
    fi
}

# Show what's new
show_changelog() {
    local old_version="$1"
    local new_version=$(get_current_version)
    
    if [ "$old_version" != "$new_version" ]; then
        echo
        echo -e "${BLUE}📝 What's New in v$new_version:${NC}"
        echo "----------------------------------------"
        
        # Check if CHANGELOG.md exists
        if [ -f "CHANGELOG.md" ]; then
            # Show recent changes (you can customize this)
            head -20 CHANGELOG.md
        else
            # Default changelog info
            echo "• Enhanced time range control with time_range_hours parameter (1-720 hours)"
            echo "• Added cache management with use_cache parameter"  
            echo "• Improved MCP server compatibility and error handling"
            echo "• Updated documentation and examples"
            echo "• Better version control and update mechanisms"
        fi
        
        echo
        print_info "For full details, see: https://github.com/baddif/mcp-server-gmail-check/releases"
    fi
}

# Restart services if needed
restart_services() {
    print_info "Checking if services need restart..."
    
    # Check if Claude Desktop is running (macOS)
    if pgrep -f "Claude" > /dev/null; then
        print_warning "Claude Desktop is running. You may need to restart it to use updated MCP server."
        echo "To restart Claude Desktop:"
        echo "1. Quit Claude Desktop"
        echo "2. Reopen Claude Desktop"
        echo "3. The updated MCP server will be loaded automatically"
    fi
}

# Main update process
main() {
    echo "Starting update process..."
    echo
    
    # Pre-update checks
    check_git_repo
    check_remote
    
    # Get current version before update
    local old_version=$(get_current_version)
    echo "Current version: $old_version"
    echo
    
    # Backup and safety checks
    backup_config
    check_uncommitted_changes
    
    # Perform update
    if update_repo; then
        # No updates available
        echo
        print_info "Use 'python3 version.py --info' to check version details"
        exit 0
    fi
    
    # Post-update tasks
    update_dependencies
    validate_installation
    restore_config
    show_changelog "$old_version"
    restart_services
    
    echo
    print_status "✨ Update completed successfully!"
    echo
    print_info "Next steps:"
    echo "1. Test your configuration: python3 test_gmail_skill.py"
    echo "2. Test MCP server: python3 mcp_server.py --test"
    echo "3. Check new features: python3 version.py --info"
    
    if [ -f "claude_desktop_config.json" ]; then
        echo "4. Restart Claude Desktop to use updated MCP server"
    fi
}

# Command line options
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check        Check for updates without applying them"
        echo "  --force        Force update even with uncommitted changes"
        echo "  --version      Show current version information"
        echo
        echo "Examples:"
        echo "  $0              # Run normal update"
        echo "  $0 --check     # Check for updates"
        echo "  $0 --version   # Show version info"
        ;;
    --check)
        check_git_repo
        git fetch origin main > /dev/null 2>&1
        local_commit=$(git rev-parse HEAD)
        remote_commit=$(git rev-parse origin/main)
        
        if [ "$local_commit" = "$remote_commit" ]; then
            print_status "You are up to date!"
        else
            print_info "Updates are available. Run '$0' to update."
            # Show commit difference
            echo "Changes available:"
            git log --oneline "$local_commit..$remote_commit" | head -5
        fi
        ;;
    --version)
        if command -v python3 > /dev/null && [ -f "version.py" ]; then
            python3 version.py --info
        else
            echo "Version information not available"
        fi
        ;;
    --force)
        # Skip uncommitted changes check
        main
        ;;
    *)
        main
        ;;
esac