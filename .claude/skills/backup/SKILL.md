---
name: backup
description: Copy personal vault data from VPS to local via SSH (daily, thoughts, contacts, finances, attachments, business, projects, sessions, graph). Remote path: brain:/home/agent-second-brain/vault
---

Run the backup script to pull vault data from the remote server:

```bash
bash scripts/backup.sh
```

Report what was copied and what was skipped.
