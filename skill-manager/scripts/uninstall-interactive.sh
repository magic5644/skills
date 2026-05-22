#!/usr/bin/env bash

#==============================================================================
# Skill Manager - Interactive Uninstaller
# Fuzzy-find and uninstall agent skills with fzf
#==============================================================================

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

#==============================================================================
# Functions
#==============================================================================

print_error() {
    echo -e "${RED}❌ Error:${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

detect_all_skills_directories() {
    local dirs=()
    
    # Check all known locations
    local candidate_dirs=(
        "$HOME/.copilot/skills"    # VS Code / GitHub Copilot
        "$HOME/.claude/skills"      # Claude Code
        "$HOME/.cursor/skills"      # Cursor
        "$HOME/.agents/skills"      # Generic agent framework
        ".agents/skills"            # Project-local skills
    )

    for dir in "${candidate_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            dirs+=("$dir")
        fi
    done

    printf '%s\n' "${dirs[@]}"
}

detect_skills_directory() {
    # Check for custom directory first
    if [[ -n "${SKILLS_DIR:-}" ]] && [[ -d "$SKILLS_DIR" ]]; then
        echo "$SKILLS_DIR"
        return 0
    fi

    # Auto-detect platform
    local candidate_dirs=(
        "$HOME/.copilot/skills"    # VS Code / GitHub Copilot
        "$HOME/.claude/skills"      # Claude Code
        "$HOME/.cursor/skills"      # Cursor
        "$HOME/.agents/skills"      # Generic agent framework
        ".agents/skills"            # Project-local skills
    )

    for dir in "${candidate_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            echo "$dir"
            return 0
        fi
    done

    return 1
}

check_fzf() {
    if ! command -v fzf &> /dev/null; then
        print_error "fzf is not installed"
        echo ""
        echo "Install fzf first:"
        echo ""
        echo "  macOS:          brew install fzf"
        echo "  Ubuntu/Debian:  sudo apt install fzf"
        echo "  Fedora:         sudo dnf install fzf"
        echo ""
        exit 1
    fi
}

list_installed_skills() {
    local skills_dir="$1"
    
    if [[ ! -d "$skills_dir" ]]; then
        print_error "Skills directory not found: $skills_dir"
        exit 1
    fi

    # List directories only, exclude hidden files and common non-skill files
    find "$skills_dir" -mindepth 1 -maxdepth 1 -type d \
        ! -name ".*" \
        -exec basename {} \; | sort
}

list_all_skills_with_locations() {
    local -a all_dirs
    mapfile -t all_dirs < <(detect_all_skills_directories)
    
    if [[ ${#all_dirs[@]} -eq 0 ]]; then
        return 1
    fi
    
    local location_label
    for dir in "${all_dirs[@]}"; do
        # Determine location label
        case "$dir" in
            "$HOME/.copilot/skills")
                location_label="[copilot]"
                ;;
            "$HOME/.claude/skills")
                location_label="[claude]"
                ;;
            "$HOME/.cursor/skills")
                location_label="[cursor]"
                ;;
            "$HOME/.agents/skills")
                location_label="[agents]"
                ;;
            ".agents/skills")
                location_label="[local]"
                ;;
            *)
                location_label="[custom]"
                ;;
        esac
        
        # List skills from this directory with location prefix
        if [[ -d "$dir" ]]; then
            find "$dir" -mindepth 1 -maxdepth 1 -type d \
                ! -name ".*" \
                -exec basename {} \; | while read -r skill; do
                echo "${location_label} ${skill}|${dir}"
            done
        fi
    done | sort
}

select_scope() {
    echo ""
    print_info "Choose skill scope:"
    echo ""
    echo "  1) Global only  (~/.*/{copilot,claude,cursor,agents}/skills)"
    echo "  2) Local only   (.agents/skills in current project)"
    echo "  3) Both         (all locations)"
    echo ""
    
    local choice
    read -p "$(echo -e "${BLUE}Select [1-3]:${NC} ")" -n 1 -r choice
    echo ""
    
    case "$choice" in
        1) echo "global" ;;
        2) echo "local" ;;
        3) echo "both" ;;
        *)
            print_warning "Invalid choice, defaulting to 'both'"
            echo "both"
            ;;
    esac
}

show_usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Interactive skill uninstaller using fzf.

OPTIONS:
    --list              List installed skills and exit
    --dir <path>        Use custom skills directory (bypasses scope selection)
    --scope <scope>     Pre-select scope: global, local, or both (default: interactive)
    -h, --help          Show this help message

ENVIRONMENT:
    SKILLS_DIR          Override skills directory detection

EXAMPLES:
    # Interactive uninstall with scope selection
    ./$(basename "$0")

    # List only
    ./$(basename "$0") --list

    # Uninstall global skills only
    ./$(basename "$0") --scope global

    # Uninstall local skills only
    ./$(basename "$0") --scope local

    # Uninstall from all locations
    ./$(basename "$0") --scope both

    # Custom directory (bypasses scope selection)
    ./$(basename "$0") --dir /path/to/skills

    # Or via environment
    SKILLS_DIR=/path/to/skills ./$(basename "$0")
EOF
}

#==============================================================================
# Main
#==============================================================================

main() {
    local list_only=false
    local custom_dir=""
    local scope=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --list)
                list_only=true
                shift
                ;;
            --dir)
                custom_dir="$2"
                shift 2
                ;;
            --scope)
                scope="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo ""
                show_usage
                exit 1
                ;;
        esac
    done

    # Set custom directory if provided (bypasses scope selection)
    if [[ -n "$custom_dir" ]]; then
        export SKILLS_DIR="$custom_dir"
        
        # Detect skills directory
        print_info "Using custom directory..."
        local skills_dir
        if ! skills_dir=$(detect_skills_directory); then
            print_error "Custom directory not found or invalid"
            exit 1
        fi

        print_success "Found skills directory: $skills_dir"
        echo ""

        # Get list of installed skills
        local skills_list
        skills_list=$(list_installed_skills "$skills_dir")

        if [[ -z "$skills_list" ]]; then
            print_warning "No skills installed in $skills_dir"
            exit 0
        fi

        local skill_count
        skill_count=$(echo "$skills_list" | wc -l | tr -d ' ')
        print_info "Found $skill_count skill(s) installed"
        echo ""

        # If list only, show and exit
        if [[ "$list_only" = true ]]; then
            echo "$skills_list"
            exit 0
        fi

        # Check for fzf
        check_fzf
        
        # Continue with single directory flow
        run_single_directory_uninstall "$skills_dir" "$skills_list"
        return
    fi

    # Multi-directory flow
    local -a all_dirs
    mapfile -t all_dirs < <(detect_all_skills_directories)

    if [[ ${#all_dirs[@]} -eq 0 ]]; then
        print_error "No skills directory found"
        echo ""
        echo "Checked locations:"
        echo "  - ~/.copilot/skills"
        echo "  - ~/.claude/skills"
        echo "  - ~/.cursor/skills"
        echo "  - ~/.agents/skills"
        echo "  - .agents/skills (project-local)"
        echo ""
        echo "Create one with: mkdir -p ~/.copilot/skills"
        exit 1
    fi

    print_success "Found ${#all_dirs[@]} skill location(s):"
    for dir in "${all_dirs[@]}"; do
        echo "  - $dir"
    done
    echo ""

    # Ask for scope if not provided
    if [[ -z "$scope" ]] && [[ "$list_only" = false ]]; then
        scope=$(select_scope)
    else
        scope="${scope:-both}"
    fi

    # Filter directories based on scope
    local -a filtered_dirs=()
    case "$scope" in
        global)
            for dir in "${all_dirs[@]}"; do
                if [[ "$dir" != ".agents/skills" ]]; then
                    filtered_dirs+=("$dir")
                fi
            done
            ;;
        local)
            for dir in "${all_dirs[@]}"; do
                if [[ "$dir" == ".agents/skills" ]]; then
                    filtered_dirs+=("$dir")
                fi
            done
            ;;
        both)
            filtered_dirs=("${all_dirs[@]}")
            ;;
    esac

    if [[ ${#filtered_dirs[@]} -eq 0 ]]; then
        print_warning "No skills found for scope: $scope"
        exit 0
    fi

    print_info "Using scope: $scope (${#filtered_dirs[@]} location(s))"
    echo ""

    # List skills with locations
    local skills_with_locations
    if ! skills_with_locations=$(list_all_skills_with_locations); then
        print_warning "No skills installed"
        exit 0
    fi

    # Filter by scope
    local filtered_skills=""
    case "$scope" in
        global)
            filtered_skills=$(echo "$skills_with_locations" | grep -v '\[local\]')
            ;;
        local)
            filtered_skills=$(echo "$skills_with_locations" | grep '\[local\]')
            ;;
        both)
            filtered_skills="$skills_with_locations"
            ;;
    esac

    if [[ -z "$filtered_skills" ]]; then
        print_warning "No skills found for scope: $scope"
        exit 0
    fi

    local skill_count
    skill_count=$(echo "$filtered_skills" | wc -l | tr -d ' ')
    print_info "Found $skill_count skill(s)"
    echo ""

    # If list only, show and exit
    if [[ "$list_only" = true ]]; then
        echo "$filtered_skills" | sed 's/|.*//'
        exit 0
    fi

    # Check for fzf
    check_fzf

    run_multi_directory_uninstall "$filtered_skills"
}

run_single_directory_uninstall() {
    local skills_dir="$1"
    local skills_list="$2"

    # Interactive selection with fzf
    print_info "Opening interactive selector..."
    echo ""
    echo "  ⬆️⬇️  Navigate with arrow keys"
    echo "  🔍   Type to filter"
    echo "  ✅   TAB to select/unselect (multi-select)"
    echo "  ✨   ENTER to confirm and uninstall"
    echo "  ❌   ESC to cancel"
    echo ""
    sleep 1

    local selected_skills
    selected_skills=$(echo "$skills_list" | fzf \
        --multi \
        --height=60% \
        --border=rounded \
        --prompt="Select skills to uninstall (TAB=multi-select) > " \
        --header="↑↓ Navigate | TAB Select | ENTER Confirm | ESC Cancel" \
        --preview="ls -lh \"$skills_dir/{}/\" 2>/dev/null || echo 'Directory: {}'" \
        --preview-window=right:40%:wrap \
        --bind='ctrl-a:select-all,ctrl-d:deselect-all' \
        --color='header:italic:underline' \
    ) || {
        print_warning "Selection cancelled"
        exit 0
    }

    # Check if anything was selected
    if [[ -z "$selected_skills" ]]; then
        print_warning "No skills selected"
        exit 0
    fi

    # Show what will be uninstalled
    local selected_count
    selected_count=$(echo "$selected_skills" | wc -l | tr -d ' ')
    echo ""
    print_info "Selected $selected_count skill(s) for uninstallation:"
    echo "$selected_skills" | sed 's/^/  - /'
    echo ""

    # Confirmation
    read -p "$(echo -e "${YELLOW}⚠️  Proceed with uninstallation? [y/N]${NC} ")" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Uninstallation cancelled"
        exit 0
    fi

    # Uninstall each selected skill
    echo ""
    print_info "Uninstalling skills..."
    echo ""

    local success_count=0
    local fail_count=0

    while IFS= read -r skill; do
        local skill_path="$skills_dir/$skill"
        
        if [[ ! -d "$skill_path" ]]; then
            print_error "Not found: $skill"
            ((fail_count++))
            continue
        fi

        echo -n "  Removing $skill... "
        if rm -rf "$skill_path"; then
            echo -e "${GREEN}✓${NC}"
            ((success_count++))
        else
            echo -e "${RED}✗${NC}"
            print_error "Failed to remove $skill"
            ((fail_count++))
        fi
    done <<< "$selected_skills"

    # Summary
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ $fail_count -eq 0 ]]; then
        print_success "Successfully uninstalled $success_count skill(s)"
    else
        print_warning "Uninstalled $success_count skill(s), $fail_count failed"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Show remaining skills
    local remaining_skills
    remaining_skills=$(list_installed_skills "$skills_dir")
    
    if [[ -z "$remaining_skills" ]]; then
        print_info "No skills remaining in $skills_dir"
    else
        local remaining_count
        remaining_count=$(echo "$remaining_skills" | wc -l | tr -d ' ')
        print_info "Remaining skills ($remaining_count):"
        echo "$remaining_skills" | sed 's/^/  - /'
    fi
    
    echo ""
}

run_multi_directory_uninstall() {
    local skills_with_locations="$1"

    # Interactive selection with fzf
    print_info "Opening interactive selector..."
    echo ""
    echo "  ⬆️⬇️  Navigate with arrow keys"
    echo "  🔍   Type to filter"
    echo "  ✅   TAB to select/unselect (multi-select)"
    echo "  ✨   ENTER to confirm and uninstall"
    echo "  ❌   ESC to cancel"
    echo ""
    sleep 1

    local selected_skills_raw
    selected_skills_raw=$(echo "$skills_with_locations" | fzf \
        --multi \
        --height=60% \
        --border=rounded \
        --prompt="Select skills to uninstall (TAB=multi-select) > " \
        --header="↑↓ Navigate | TAB Select | ENTER Confirm | ESC Cancel" \
        --delimiter='|' \
        --with-nth=1 \
        --preview="echo 'Location: {2}'; ls -lh {2}/{1} 2>/dev/null | tail -n +2" \
        --preview-window=right:40%:wrap \
        --bind='ctrl-a:select-all,ctrl-d:deselect-all' \
        --color='header:italic:underline' \
    ) || {
        print_warning "Selection cancelled"
        exit 0
    }

    # Check if anything was selected
    if [[ -z "$selected_skills_raw" ]]; then
        print_warning "No skills selected"
        exit 0
    fi

    # Parse selections
    local -a skill_entries=()
    while IFS='|' read -r display_name dir; do
        # Extract skill name from "[location] skillname" format
        local skill_name=$(echo "$display_name" | sed 's/^\[[^]]*\] //')
        skill_entries+=("$skill_name|$dir")
    done <<< "$selected_skills_raw"

    # Show what will be uninstalled
    local selected_count=${#skill_entries[@]}
    echo ""
    print_info "Selected $selected_count skill(s) for uninstallation:"
    for entry in "${skill_entries[@]}"; do
        IFS='|' read -r skill_name dir <<< "$entry"
        echo "  - $skill_name ($dir)"
    done
    echo ""

    # Confirmation
    read -p "$(echo -e "${YELLOW}⚠️  Proceed with uninstallation? [y/N]${NC} ")" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Uninstallation cancelled"
        exit 0
    fi

    # Uninstall each selected skill
    echo ""
    print_info "Uninstalling skills..."
    echo ""

    local success_count=0
    local fail_count=0

    for entry in "${skill_entries[@]}"; do
        IFS='|' read -r skill_name dir <<< "$entry"
        local skill_path="$dir/$skill_name"
        
        if [[ ! -d "$skill_path" ]]; then
            print_error "Not found: $skill_name in $dir"
            ((fail_count++))
            continue
        fi

        echo -n "  Removing $skill_name from $dir... "
        if rm -rf "$skill_path"; then
            echo -e "${GREEN}✓${NC}"
            ((success_count++))
        else
            echo -e "${RED}✗${NC}"
            print_error "Failed to remove $skill_name"
            ((fail_count++))
        fi
    done

    # Summary
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ $fail_count -eq 0 ]]; then
        print_success "Successfully uninstalled $success_count skill(s)"
    else
        print_warning "Uninstalled $success_count skill(s), $fail_count failed"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Show remaining skills by location
    print_info "Remaining skills by location:"
    local -a all_dirs
    mapfile -t all_dirs < <(detect_all_skills_directories)
    
    for dir in "${all_dirs[@]}"; do
        local remaining=$(list_installed_skills "$dir" 2>/dev/null)
        if [[ -n "$remaining" ]]; then
            local count=$(echo "$remaining" | wc -l | tr -d ' ')
            echo "  $dir ($count):"
            echo "$remaining" | sed 's/^/    - /'
        else
            echo "  $dir: (empty)"
        fi
    done
    
    echo ""
}

# Run main function
main "$@"
