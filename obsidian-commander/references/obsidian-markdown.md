# Obsidian Markdown & Frontmatter Reference

## Frontmatter (Properties)

YAML block at the very top of a `.md` file, between `---` markers:

```yaml
---
title: My Note Title
tags:
  - project
  - active
aliases:
  - my-note
  - alternate-name
cssclasses:
  - wide-page
created: 2024-01-15
modified: 2024-06-20T10:30:00
status: draft
publish: false
---
```

### Default Properties

| Property | Type | Purpose |
| --- | --- | --- |
| `tags` | list | Categorize notes |
| `aliases` | list | Alternative names for linking |
| `cssclasses` | list | Apply CSS snippets |

### Property Types

| Type | Example |
| --- | --- |
| Text | `title: "A New Hope"` |
| List | `tags: [a, b]` or multiline with `- item` |
| Number | `year: 1977` |
| Checkbox | `favorite: true` |
| Date | `date: 2024-01-15` |
| Date & time | `time: 2024-01-15T10:30:00` |

### Links in Properties

Internal links in properties must be quoted:

```yaml
---
related: "[[Other Note]]"
references:
  - "[[Note A]]"
  - "[[Note B]]"
---
```

## Link Syntax

### Wikilinks (default)

| Syntax | Result |
| --- | --- |
| `[[Note]]` | Link to Note |
| `[[Note\|Display]]` | Link with custom display text |
| `[[Note#Heading]]` | Link to heading |
| `[[Note#^block-id]]` | Link to block |
| `![[Note]]` | Embed note content |
| `![[image.png]]` | Embed image |
| `![[video.mp4]]` | Embed video |

### Markdown Links

| Syntax | Result |
| --- | --- |
| `[text](Note.md)` | Link to Note |
| `[text](Note.md#Heading)` | Link to heading |
| `![alt](image.png)` | Embed image |

### Block References

Add `^block-id` at end of any block:

```markdown
This is a paragraph. ^my-block

- List item ^list-ref
```

Then link: `[[Note#^my-block]]`

## Tags

- Inline: `#tag`, `#nested/tag`
- In frontmatter: `tags: [tag1, tag2]`
- Allowed chars: letters, numbers, `_`, `-`, `/`
- Must contain at least one non-numeric character
- Case-insensitive

## Callouts

```markdown
> [!note] Title
> Content

> [!warning] Attention
> Important info

> [!tip]+ Collapsible (open by default)
> Content

> [!info]- Collapsed by default
> Content
```

Types: `note`, `abstract`, `info`, `tip`, `success`, `question`, `warning`, `failure`, `danger`, `bug`, `example`, `quote`

## Task Syntax

```markdown
- [ ] Incomplete task
- [x] Completed task
- [-] Cancelled task
- [?] Question
- [!] Important
```

## Embed Syntax

```markdown
![[Note]]               # Embed full note
![[Note#Heading]]       # Embed section
![[Note#^block]]        # Embed block
![[image.png]]          # Embed image
![[image.png|300]]      # Embed with width
![[audio.mp3]]          # Embed audio
![[video.mp4]]          # Embed video
![[file.pdf]]           # Embed PDF
```

## Code Blocks

````markdown
```language
code here
```

```query
search term here
```

```dataview
TABLE file.ctime AS Created
FROM #project
SORT file.ctime DESC
```
````

## Math (LaTeX)

```markdown
Inline: $E = mc^2$

Block:
$$
\int_0^1 x^2 dx = \frac{1}{3}
$$
```

## Comments

```markdown
%%
This is a comment that won't render
%%

Inline %%comment%% in text
```
