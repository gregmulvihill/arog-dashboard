# Arog Dashboard - Project Roadmap

## Vision
Transform the Arog Dashboard into an intelligent R&D operations center that provides:
- Instant visibility into system health and container states
- Proactive issue detection with visual alerts
- AI-powered automated remediation through interactive wizards
- Comprehensive resource monitoring (containers, services, processes, network)

---

## Phase 1: Enhanced UI & Information Density

### 1.1 Beszel-Style System Info Card
**Status**: Pending
**Priority**: High

Implement Beszel's clean system info card design:
- Large system name header (arog)
- Animated status indicator (green pulse when up, red when issues)
- Key system info in horizontal layout:
  - Hostname
  - Uptime
  - OS/Kernel version
  - CPU model and core count
  - Total memory
- Compact, information-dense design

### 1.2 Enhanced Docker Container Table
**Status**: Pending
**Priority**: High

**Current State**:
- Columns: Status | Arrow Link | Name | Image | Port
- Basic layout, minimal information

**Target State**:
```
Status | Port (Link) | Name | Image | Created | Updated | Network | Volumes | Memory | CPU
```

**Column Details**:
- **Status**: Color-coded indicator (green=running, red=exited, yellow=paused)
- **Port (Link)**: Large clickable button showing port number, opens web UI in new tab
  - Example: `[8080]` as prominent button
  - Only show if web UI detected
  - Multiple ports: show primary port
- **Name**: Container name with truncation if needed
- **Image**: Image name (short form)
- **Created**: Relative time (e.g., "3 days ago")
- **Updated**: Last state change
- **Network**: Network mode/name
- **Volumes**: Size of mounted volumes
- **Memory**: Current memory usage
- **CPU**: Current CPU usage percentage

### 1.3 Advanced Table Features
**Status**: Pending
**Priority**: High

#### Per-Column Regex Filtering
- Text input at top of each column
- Real-time regex-based filtering
- Show/hide filter inputs with toggle button
- Persist filter state in localStorage

#### Sortable Columns
- Click column header to sort
- Toggle ascending/descending
- Multi-column sort (shift+click)
- Visual indicators for sort direction

#### Additional Features
- Row selection (checkbox)
- Bulk actions (restart, stop, remove selected)
- Export filtered data (JSON, CSV)
- Saved filter presets

---

## Phase 2: Intelligent Issue Detection

### 2.1 Health Monitoring System
**Status**: Pending
**Priority**: High

**Container Health Checks**:
- Exit status detection (highlight red)
- Resource threshold alerts:
  - Memory > 90% usage
  - CPU sustained > 80%
  - Disk space < 10%
- Restart loop detection (restarts > 5 in 10min)
- Network connectivity issues
- Failed health checks

**System Health Checks**:
- High system memory/CPU usage
- Disk space warnings
- Service failures
- Network interface issues

**Visual Indicators**:
- Red highlight for critical issues
- Yellow for warnings
- Pulsing animation for active problems
- Issue count badges

### 2.2 Issue Prioritization
**Status**: Pending
**Priority**: Medium

Rank issues by severity:
1. **Critical** (red): Service down, out of disk space
2. **High** (orange): Resource exhaustion, restart loops
3. **Medium** (yellow): Performance degradation
4. **Low** (blue): Informational warnings

Display priority issues at top of dashboard in alert panel.

---

## Phase 3: AI-Powered Remediation

### 3.1 Interactive Fix Wizard
**Status**: Pending
**Priority**: High

**Trigger**: Click on red/yellow issue indicator

**Wizard Flow**:
1. **Issue Analysis** (automatic):
   - Gather container logs (last 100 lines)
   - Check resource usage history
   - Analyze restart patterns
   - Review network connectivity

2. **AI-Powered Diagnosis** (DSPy/Swarms):
   - Classify issue type
   - Identify root cause
   - Generate fix suggestions
   - Rank suggestions by confidence

3. **Action Selection Interface**:
   ```
   What would you like to do?

   [1] Restart container (confidence: 85%)
   [2] Increase memory limit to 2GB (confidence: 70%)
   [3] Clear container logs (confidence: 45%)
   [4] Review container logs
   [5] View resource graphs
   [O] Other (describe custom action)
   ```

4. **Execution**:
   - Show progress spinner
   - Stream execution logs
   - Report success/failure
   - Re-check health status

5. **Follow-up**:
   - Monitor for 5 minutes
   - Report if issue resolved
   - Suggest additional actions if needed

### 3.2 DSPy Integration
**Status**: Pending
**Priority**: High

**Use Cases**:
- Log analysis and error extraction
- Root cause analysis
- Fix suggestion generation
- Natural language command translation

**Implementation**:
- Create DSPy signatures for:
  - `LogAnalyzer`: Extract errors from logs
  - `RootCauseAnalyzer`: Determine issue cause
  - `FixGenerator`: Generate remediation steps
  - `CommandTranslator`: NL → Docker/system commands

### 3.3 Swarms Integration
**Status**: Pending
**Priority**: Medium

**Multi-Agent Orchestration**:
- **Diagnostic Agent**: Gather information, analyze state
- **Planning Agent**: Generate fix strategies
- **Execution Agent**: Execute approved actions
- **Validation Agent**: Verify fixes worked

**Workflow**:
1. User clicks issue → Diagnostic agent activates
2. Planning agent generates options
3. User selects option → Execution agent runs commands
4. Validation agent confirms resolution

---

## Phase 4: Comprehensive Resource Monitoring

### 4.1 Non-Container Resources
**Status**: Pending
**Priority**: Medium

**System Services**:
- Systemd service status
- Service health checks
- Restart counts
- Memory/CPU per service

**Network Resources**:
- Open ports listing
- Active connections
- Network throughput per interface
- Firewall rules

**Storage**:
- Disk usage by directory
- Volume mounts
- NFS/CIFS shares status
- RAID status (if applicable)

**Processes**:
- Top processes by CPU/memory
- Long-running processes
- Process tree view
- Kill/restart controls

### 4.2 Resource Views
**Status**: Pending
**Priority**: Medium

Add tabs/sections for:
- **Containers** (current view, enhanced)
- **Services** (systemd services)
- **Network** (ports, connections, interfaces)
- **Storage** (disks, volumes, mounts)
- **Processes** (process list with controls)

---

## Phase 5: Advanced Features

### 5.1 Action History
**Status**: Pending
**Priority**: Low

Track all actions taken:
- Timestamp
- Action type (restart, stop, etc.)
- Target (container/service)
- Result (success/failure)
- User (if multi-user future)

### 5.2 Automated Remediation
**Status**: Pending
**Priority**: Low

Allow auto-fixing common issues:
- Auto-restart on exit
- Auto-clear logs when > 100MB
- Auto-prune unused images/volumes
- Configurable rules engine

### 5.3 Notifications
**Status**: Pending
**Priority**: Low

Alert mechanisms:
- Browser notifications
- Webhook to Discord/Slack
- Email alerts
- SMS (via Twilio)

### 5.4 Multi-System Support
**Status**: Pending
**Priority**: Low

Extend to monitor multiple hosts:
- Add remote systems
- Unified dashboard
- Cross-system actions

---

## Technical Architecture

### Backend Components

#### New Modules Needed:
```
app/
├── health_monitor.py      # Issue detection engine
├── ai_diagnostics.py      # DSPy integration
├── action_executor.py     # Execute remediation actions
├── swarms_orchestrator.py # Multi-agent coordination
├── resource_monitor.py    # Non-container resources
└── wizard_api.py          # Wizard endpoints
```

#### API Endpoints:
```
POST   /api/issues/detect          # Run health checks
GET    /api/issues                 # List current issues
POST   /api/issues/{id}/diagnose   # AI diagnosis
POST   /api/issues/{id}/fix        # Execute fix
GET    /api/actions/history        # Action history
POST   /api/containers/{id}/logs   # Get container logs
GET    /api/services               # System services
GET    /api/network                # Network resources
GET    /api/storage                # Storage resources
GET    /api/processes              # Process list
```

### Frontend Components

#### New UI Components:
```
templates/
├── fragments/
│   ├── system_info_card.html    # Beszel-style card
│   ├── issue_list.html          # Issue alerts
│   └── wizard.html              # Fix wizard modal
└── components/
    ├── sortable_table.js         # Enhanced table
    ├── column_filters.js         # Regex filters
    └── wizard_controller.js      # Wizard state machine
```

### Database Schema (SQLite)

```sql
-- Issue tracking
CREATE TABLE issues (
    id TEXT PRIMARY KEY,
    target_type TEXT,      -- 'container', 'service', 'system'
    target_id TEXT,
    severity TEXT,         -- 'critical', 'high', 'medium', 'low'
    issue_type TEXT,
    description TEXT,
    detected_at TIMESTAMP,
    resolved_at TIMESTAMP,
    auto_resolved BOOLEAN
);

-- Action history
CREATE TABLE action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    action_type TEXT,
    target_type TEXT,
    target_id TEXT,
    parameters JSON,
    result TEXT,
    error TEXT,
    duration_ms INTEGER
);

-- Health check results
CREATE TABLE health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    target_type TEXT,
    target_id TEXT,
    check_type TEXT,
    status TEXT,
    metrics JSON
);
```

---

## Implementation Priority

### Sprint 1: Enhanced UI Foundation (Week 1)
1. ✅ Beszel-style system info card
2. ✅ Enhanced container table columns
3. ✅ Large clickable port buttons
4. ✅ Per-column filtering
5. ✅ Sortable columns

### Sprint 2: Health Monitoring (Week 2)
1. Issue detection engine
2. Visual indicators (red/yellow highlights)
3. Issue list panel
4. Basic alerting

### Sprint 3: AI Wizard Foundation (Week 3)
1. Wizard UI/UX
2. Basic DSPy integration
3. Action selection interface
4. Command execution

### Sprint 4: Advanced AI Features (Week 4)
1. Swarms multi-agent orchestration
2. Advanced diagnostics
3. Action history
4. Validation agents

### Sprint 5: Resource Monitoring (Week 5+)
1. System services
2. Network monitoring
3. Storage monitoring
4. Process management

---

## Dependencies

### Python Packages:
```
fastapi
docker-py
psutil
dspy-ai
swarms
sqlalchemy
aiosqlite
jinja2
```

### Frontend Libraries:
```
htmx (already included)
alpinejs (already included)
sortablejs (for drag-drop)
```

---

## Success Metrics

### Performance:
- Page load < 500ms
- Issue detection latency < 2s
- AI diagnosis < 5s
- Action execution feedback in real-time

### Usability:
- < 3 clicks to fix common issues
- Intuitive wizard flow
- Clear visual indicators
- Accessible on mobile

### Reliability:
- 99.9% uptime
- No false positive alerts
- Accurate AI suggestions > 80%
- All actions logged and reversible

---

## Notes

- Keep terminal aesthetic (dense, monospace, dark theme)
- Maintain zero-wasted-space philosophy
- Smooth animations, no jarring transitions
- Mobile-responsive design
- Keyboard shortcuts for power users

---

**Last Updated**: 2025-10-16
**Status**: Planning Phase
**Next Milestone**: Sprint 1 - Enhanced UI Foundation
