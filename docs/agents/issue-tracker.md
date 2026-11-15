# Issue tracker: Jira

Issues and PRDs for this repo live in Jira.

- Site: https://clogweeny.atlassian.net (cloudId: `clogweeny.atlassian.net`)
- Project key: `KAN`
- Access: the Atlassian MCP server configured in `.mcp.json` (`mcp__atlassian__*` tools).
  Never use the Jira REST API directly or put credentials in the repo.

## Issue types

| Use for | Jira type |
|---|---|
| A PRD (from `to-prd`) | **Epic**. The PRD text is the description. |
| A thin vertical slice (from `to-issues`) | **Story**, with its parent set to the PRD's Epic |
| Technical work with no user-visible behaviour (tooling, CI, refactors) | **Task** |
| A bug (from `triage` / `diagnose`) | **Task**, with summary prefixed `Bug:` (KAN has no Bug type) |
| A breakdown step inside one story | **Subtask**. Use sparingly; prefer smaller stories. |

Stories carry their executable example (PDF in, expected spread out) and
acceptance criteria in the description, per `CLAUDE.md`.

## Conventions

- **Create**: `createJiraIssue` with project `KAN`, the issue type, summary, a Markdown
  description, and `labels`. Set `parent` to the Epic key for stories under a PRD.
- **Read**: `getJiraIssue` for fields and description; `listJiraIssueComments` for comments.
- **List / search**: `searchJiraIssuesUsingJql`, e.g.
  `project = KAN AND labels = "ready-for-agent" AND statusCategory != Done ORDER BY created ASC`.
- **Comment**: `addOrEditJiraIssueComment`.
- **Apply / remove labels**: `editJiraIssue`, updating the `labels` field. Read current labels
  first and write back the full list, because setting labels replaces them.
- **Change status**: `transitionJiraIssue`. The board uses To Do → In Progress → Done.
- **Close**: comment with the reason, then transition to **Done**. For won't-fix, also add
  the `wontfix` label.

Triage roles are labels, not statuses. See `docs/agents/triage-labels.md`.

## When a skill says "publish to the issue tracker"

Create a Jira issue in KAN of the right type (above) and report its key and URL
(`https://clogweeny.atlassian.net/browse/KAN-<n>`).

## When a skill says "fetch the relevant ticket"

Accept a key like `KAN-12` (or a bare number, meaning `KAN-<n>`), then `getJiraIssue`
and `listJiraIssueComments`.
