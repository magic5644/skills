# Obsidian CLI Reference

Obsidian CLI (requires Obsidian 1.12.7+) controls the running Obsidian app from terminal.

## Installation

1. Update Obsidian to 1.12.7+
2. Settings → General → Enable "Command line interface"
3. Restart terminal after registration

**Platform paths:**
- Windows: `Obsidian.com` added to PATH
- macOS: symlink at `/usr/local/bin/obsidian`
- Linux: binary at `~/.local/bin/obsidian`

## Vault Targeting

```bash
# Uses CWD vault by default, or specify:
obsidian vault=Notes daily
obsidian vault="My Vault" search query="test"
```

## File Targeting

```bash
# By name (link resolution, no extension needed):
obsidian read file=Recipe
# By exact path:
obsidian read path="Templates/Recipe.md"
# Active file (default when omitted)
obsidian read
```

## Complete Command Reference

### Files & Folders
| Command | Description |
|---------|-------------|
| `files` | List files (`folder=`, `ext=`, `total`) |
| `folders` | List folders (`folder=`, `total`) |
| `file` | Show file info |
| `folder` | Show folder info (`info=files\|folders\|size`) |
| `open` | Open a file (`newtab`) |
| `create` | Create file (`name=`, `content=`, `template=`, `overwrite`, `open`) |
| `read` | Read file contents |
| `append` | Append to file (`content=`, `inline`) |
| `prepend` | Prepend after frontmatter (`content=`, `inline`) |
| `move` | Move/rename file (`to=` required) |
| `rename` | Rename file (`name=` required) |
| `delete` | Delete file (`permanent` flag) |

### Search
| Command | Description |
|---------|-------------|
| `search` | Search vault (`query=`, `path=`, `limit=`, `total`, `case`) |
| `search:context` | Search with line context (grep-style output) |
| `search:open` | Open search in Obsidian (`query=`) |

### Properties
| Command | Description |
|---------|-------------|
| `properties` | List properties (`file=`, `name=`, `sort=count`, `counts`) |
| `property:set` | Set property (`name=`, `value=`, `type=`) |
| `property:remove` | Remove property (`name=`) |
| `property:read` | Read property value (`name=`) |
| `aliases` | List aliases (`total`, `verbose`) |

### Links
| Command | Description |
|---------|-------------|
| `links` | Outgoing links (`total`) |
| `backlinks` | Incoming links (`counts`, `total`) |
| `unresolved` | Broken links (`total`, `counts`, `verbose`) |
| `orphans` | Notes with no incoming links (`total`) |
| `deadends` | Notes with no outgoing links (`total`) |

### Tags
| Command | Description |
|---------|-------------|
| `tags` | List tags (`sort=count`, `counts`, `total`) |
| `tag` | Tag info (`name=`, `total`, `verbose`) |

### Tasks
| Command | Description |
|---------|-------------|
| `tasks` | List tasks (`todo`, `done`, `daily`, `verbose`) |
| `task` | Show/update task (`ref=path:line`, `toggle`, `done`, `todo`) |

### Daily Notes
| Command | Description |
|---------|-------------|
| `daily` | Open daily note |
| `daily:path` | Get daily note path |
| `daily:read` | Read daily note |
| `daily:append` | Append to daily (`content=`, `inline`, `open`) |
| `daily:prepend` | Prepend to daily (`content=`, `inline`, `open`) |

### Templates
| Command | Description |
|---------|-------------|
| `templates` | List templates (`total`) |
| `template:read` | Read template (`name=`, `resolve`) |
| `template:insert` | Insert into active file (`name=`) |

### Plugins
| Command | Description |
|---------|-------------|
| `plugins` | List plugins (`filter=core\|community`, `versions`) |
| `plugins:enabled` | List enabled plugins |
| `plugin` | Plugin info (`id=`) |
| `plugin:enable` | Enable plugin (`id=`) |
| `plugin:disable` | Disable plugin (`id=`) |
| `plugin:install` | Install plugin (`id=`, `enable`) |
| `plugin:uninstall` | Uninstall plugin (`id=`) |
| `plugin:reload` | Reload plugin (`id=`) |

### Themes & Snippets
| Command | Description |
|---------|-------------|
| `themes` | List themes |
| `theme` | Active theme info |
| `theme:set` | Set theme (`name=`) |
| `theme:install` | Install theme (`name=`, `enable`) |
| `theme:uninstall` | Uninstall theme (`name=`) |
| `snippets` | List CSS snippets |
| `snippet:enable` | Enable snippet (`name=`) |
| `snippet:disable` | Disable snippet (`name=`) |

### Bookmarks
| Command | Description |
|---------|-------------|
| `bookmarks` | List bookmarks (`total`, `verbose`) |
| `bookmark` | Add bookmark (`file=`, `search=`, `url=`, `title=`) |

### Outline
| Command | Description |
|---------|-------------|
| `outline` | Show headings (`format=tree\|md\|json`, `total`) |

### Vault
| Command | Description |
|---------|-------------|
| `vault` | Vault info (`info=name\|path\|files\|folders\|size`) |
| `vaults` | List known vaults (`total`, `verbose`) |

### Workspace
| Command | Description |
|---------|-------------|
| `workspace` | Show layout tree |
| `workspaces` | List saved workspaces |
| `workspace:save` | Save workspace (`name=`) |
| `workspace:load` | Load workspace (`name=`) |
| `tabs` | List open tabs |
| `recents` | Recently opened files |

### Sync
| Command | Description |
|---------|-------------|
| `sync` | Pause/resume (`on`/`off`) |
| `sync:status` | Show sync status |
| `sync:history` | Version history for file |
| `sync:read` | Read sync version (`version=`) |
| `sync:restore` | Restore sync version (`version=`) |
| `sync:deleted` | List deleted files |

### Publish
| Command | Description |
|---------|-------------|
| `publish:site` | Site info |
| `publish:list` | Published files |
| `publish:status` | Publish changes |
| `publish:add` | Publish file (`changed` for all) |
| `publish:remove` | Unpublish file |

### Developer
| Command | Description |
|---------|-------------|
| `eval` | Execute JavaScript (`code=`) |
| `devtools` | Toggle dev tools |
| `dev:screenshot` | Take screenshot (`path=`) |
| `dev:console` | Show console messages |
| `dev:errors` | Show JS errors |
| `plugin:reload` | Reload plugin (`id=`) |

### General
| Command | Description |
|---------|-------------|
| `help` | Show commands |
| `version` | Obsidian version |
| `reload` | Reload app window |
| `restart` | Restart app |
| `random` | Open random note |
| `wordcount` | Word/character count |

## Output Formats

Most list commands support: `format=json|tsv|csv|md|text`
Add `--copy` to any command to copy output to clipboard.

## Search Operators

| Operator | Example | Matches |
|----------|---------|---------|
| `file:` | `file:.jpg` | Filename |
| `path:` | `path:"Daily notes"` | File path |
| `content:` | `content:"hello"` | File content |
| `tag:` | `tag:#work` | Tags (not in code blocks) |
| `line:` | `line:(a b)` | Same line |
| `block:` | `block:(a b)` | Same block |
| `section:` | `section:(a b)` | Same section |
| `task:` | `task:call` | Any task |
| `task-todo:` | `task-todo:buy` | Incomplete tasks |
| `task-done:` | `task-done:call` | Completed tasks |
| `match-case:` | `match-case:API` | Case-sensitive |
| `[prop]` | `[tags]` | Has property |
| `[prop:val]` | `[status:draft]` | Property equals value |

**Boolean:** `a b` (AND), `a OR b` (OR), `-a` (NOT), `(a OR b) c` (grouping)
**Regex:** `/\d{4}-\d{2}-\d{2}/` (JS-flavored)
