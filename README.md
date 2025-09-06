# TierlistBot
A Discord bot for managing Minecraft testing queues and tickets — supports per-channel queues, test creation, results tracking, and a ticketing system.

# Requirements
- Python 3.13
- A Discord Developer Bot Token

---
# Installation
1. Clone this repo:
   
   ```
   git clone https://github.com/fwextx/TierlistBot.git
   cd TierlistBot
   
2. Install all imported packages:
   ```
   python -m venv .venv
   source .venv/bin/activate  # (Linux/macOS)
   .venv\Scripts\activate     # (Windows)
   pip install -r requirements.txt

3. Configure bot:
   - Go into the .env file and replace the token with a valid token from the Discord Developer Portal

4. Run the bot
   ```py main.py```

---


# Features

- **Per-Channel Queues**
  - Create independent queues per channel (`/test`)
  - Join/leave queues with buttons or `/leave`
  - Queue updates every 20 seconds
  - Automatic DM to the first user when they’re up

- **Queue Management**
  - `/freeze_queue` → freeze buttons to stop new entries
  - `/remove_first_in_queue` → manually remove the first user
  - `/end_test` → cleanly close a queue

- **Testers & Roles**
  - Assign testers to a queue when launching with `/test`
  - Manage testers dynamically with `/manage_testers`
  - `/set_tester_role` → configure which roles can manage queues

- **Ticket System**
  - Integrates with queues: first-in-line users get prompted to open a ticket
  - Supports per-region or per-channel ticket workflows

- **Test Results**
  - Track and record results from completed sessions
  - Attach outcomes to tickets for easy history/reference

- **Permissions**
  - Role-based control using a simple role database
  - Only authorized roles can launch/manage tests

---

# Commands Overview

### Queue & Test Commands
- `/test <channel> <tester1> [tester2..tester5]` → Start a new queue in the channel
- `/leave` → Leave the queue you’re in
- `/freeze_queue <channel>` → Disable join/leave buttons
- `/remove_first_in_queue <channel>` → Remove first user
- `/end_test <channel>` → End a queue

### Tester Management
- `/manage_testers add/remove <member> <channel>` → Manage testers
- `/set_tester_role <role>` → Allow or disallow a role for testers

---
