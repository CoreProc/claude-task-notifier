# Claude Code Task Notifier — Design

## Overview

A lightweight Python app that runs in the background, listening on a local HTTP endpoint. Claude Code's hook sends a POST request when a task completes, and the app shows a Windows toast notification via `win10toast` with a task summary and timestamp.

## Architecture

```
Claude Code finishes task
  → Hook fires: curl POST localhost:9876 with task summary
    → Python HTTP server receives request
      → Shows Windows toast notification with summary + timestamp
```

## Components

### 1. Python HTTP Server
- Listens on `http://localhost:9876`
- Accepts POST requests with JSON body: `{"summary": "task description"}`
- Runs as a background process

### 2. Toast Notification
- Uses `win10toast` library
- Title: "Claude Code"
- Body: task summary + completion timestamp
- Duration: 10 seconds

### 3. System Tray Icon
- Uses `pystray` + `Pillow`
- Shows app is running
- Right-click menu: "Exit"

### 4. Claude Code Hook
- Configured in Claude Code settings
- Fires on task completion
- Sends: `curl -X POST http://localhost:9876 -H "Content-Type: application/json" -d "{\"summary\": \"...\"}"`

## Dependencies

- `win10toast`
- `pystray`
- `Pillow`

## Project Location

`E:\Dev\Android\Projects\claude-task-notifier\`
