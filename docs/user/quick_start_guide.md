# Quick Start Guide — DVA Platform v2

## Overview

DVA Platform v2 is a retail data processing platform that transforms raw retail data files into standardized, validated business insights. This guide gets you from installation to your first data transformation in under 10 minutes.

## Prerequisites

- **Python 3.12+** installed on your system
- **pip** package manager
- **4GB RAM** minimum (8GB recommended)
- **500MB** free disk space

## Installation

### 1. Verify Python

```bash
python3 --version
# Must show Python 3.12 or later
```

### 2. Clone or Download the Project

```bash
git clone <repository-url> dva-platform
cd dva-platform
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
python3 scripts/dependency_checker.py
```

All dependencies should show check marks.

## Launch the Application

```bash
python3 -m ui.app
```

Open your browser to **http://localhost:8080**

## First-Run Wizard

On first launch, the Welcome Wizard guides you through:

1. **Theme Selection** — Choose light, dark, high-contrast, or system theme
2. **Project Setup** — Create your first project
3. **Connection Setup** — Add a data source (local folder or network path)
4. **Demo Data** — Load sample data to explore features

Complete the wizard to access the full workspace.

## Your First Workflow

### Step 1: Upload Data

1. Navigate to **Connection** workspace
2. Browse to a folder containing retail data files
3. Select files and click **Load**

### Step 2: Detect Structure

1. Go to **Detection** workspace
2. Review the detected file type, delimiter, encoding, and columns
3. Confirm or adjust detection results

### Step 3: Map to Canonical

1. Go to **Canonical** workspace
2. Review the suggested column mappings
3. Accept mappings or adjust manually
4. Apply transformations

### Step 4: Preview Results

1. Go to **Preview** workspace
2. Inspect the standardized data
3. Verify column names and data types

### Step 5: Define Requirements

1. Go to **Requirements** workspace
2. Select your business goal (Aggregation, Validation, Reporting, etc.)
3. Configure parameters

### Step 6: Execute

1. Go to **Operation** → **Processing** workspaces
2. Review the execution plan
3. Run the workflow
4. View results in **Validation** and **Reports** workspaces

### Step 7: Export

1. Go to **Reports** workspace
2. Choose export format (Excel, CSV, JSON)
3. Download your results

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` through `Ctrl+9` | Switch workspaces |
| `Ctrl+S` | Save current session |
| `Ctrl+E` | Export results |
| `Ctrl+D` | Toggle dark mode |
| `Ctrl+H` | Show help |

## Next Steps

- Read the [User Guide](user_guide.md) for detailed feature descriptions
- See the [Installation Guide](installation_guide.md) for production setup
- Visit the [FAQ](faq.md) for common questions
- Check the [Troubleshooting Guide](troubleshooting_guide.md) if you encounter issues

## Getting Help

- Built-in help workspace: Click **Help** in the sidebar
- Developer documentation: See [Developer Guide](../developer/developer_guide.md)
- Report issues: Contact your system administrator
