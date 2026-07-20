"""Guidance service — provides step-by-step guidance for each workspace."""
from typing import Any, Dict, Optional


WORKSPACE_GUIDANCE = {
    "home": {
        "step": "Dashboard",
        "purpose": "Overview of your DVA platform and quick access to projects.",
        "instructions": "Select a project to begin, or create a new project from the Projects workspace.",
        "estimated_time": "N/A",
        "required_inputs": [],
        "expected_outputs": ["Platform overview", "Recent projects", "Quick actions"],
        "next_step": "projects",
        "progress": 0,
    },
    "projects": {
        "step": "1. Create Project",
        "purpose": "Create a new project to organize your data processing pipeline.",
        "instructions": "Enter a project name and optional description, then click Create.",
        "estimated_time": "1 minute",
        "required_inputs": ["Project name"],
        "expected_outputs": ["Project created", "Project stored in persistence"],
        "next_step": "connection",
        "progress": 10,
    },
    "connection": {
        "step": "2. Create Connection",
        "purpose": "Connect to your data source (local directory, SSH, or MFT).",
        "instructions": "Choose a connection type, fill in the required fields, and test the connection.",
        "estimated_time": "2 minutes",
        "required_inputs": ["Connection type", "Connection details"],
        "expected_outputs": ["Connection established", "Data source accessible"],
        "next_step": "detection",
        "progress": 20,
    },
    "detection": {
        "step": "3. Run Detection",
        "purpose": "Automatically detect file format, encoding, delimiter, and column layout.",
        "instructions": "Select a file from your connection and run detection to analyze its structure.",
        "estimated_time": "30 seconds",
        "required_inputs": ["Connected data source", "Selected file"],
        "expected_outputs": ["File format detected", "Columns identified", "Confidence scores"],
        "next_step": "canonical",
        "progress": 35,
    },
    "canonical": {
        "step": "4. Business Mapping",
        "purpose": "Map your physical data columns to DVA's business schema.",
        "instructions": "Review suggested mappings, adjust as needed, and accept the mapping configuration.",
        "estimated_time": "3 minutes",
        "required_inputs": ["Detection results", "Physical column list"],
        "expected_outputs": ["Column mappings defined", "Quantity strategy set", "UOM resolved"],
        "next_step": "preview",
        "progress": 50,
    },
    "preview": {
        "step": "5. Business Preview",
        "purpose": "Review the transformed canonical dataset before processing.",
        "instructions": "Verify mappings, check validation status, and approve to proceed.",
        "estimated_time": "2 minutes",
        "required_inputs": ["Canonical mappings", "Detection results"],
        "expected_outputs": ["Canonical dataset preview", "Validation results", "Approval status"],
        "next_step": "requirement",
        "progress": 60,
    },
    "requirement": {
        "step": "6. Analysis Planning",
        "purpose": "Define analysis requirements and generate an execution plan.",
        "instructions": "Select analysis modes, review recommendations, and generate the execution plan.",
        "estimated_time": "3 minutes",
        "required_inputs": ["Canonical dataset", "Business rules"],
        "expected_outputs": ["Execution plan", "Analysis requirements"],
        "next_step": "operation",
        "progress": 70,
    },
    "operation": {
        "step": "7. Execution Planning",
        "purpose": "Configure and review the processing pipeline before execution.",
        "instructions": "Review the pipeline stages, configure parameters, and check readiness.",
        "estimated_time": "2 minutes",
        "required_inputs": ["Execution plan", "Processing configuration"],
        "expected_outputs": ["Pipeline configured", "Readiness confirmed"],
        "next_step": "processing",
        "progress": 80,
    },
    "processing": {
        "step": "8. Execute Processing",
        "purpose": "Run the data processing pipeline and monitor progress.",
        "instructions": "Start processing and monitor progress, logs, and metrics in real time.",
        "estimated_time": "5-15 minutes (depends on data size)",
        "required_inputs": ["Configured pipeline", "Source data"],
        "expected_outputs": ["Processed results", "Execution logs", "Metrics"],
        "next_step": "validation",
        "progress": 85,
    },
    "validation": {
        "step": "9. Validate Results",
        "purpose": "Validate processed data against business rules and quality thresholds.",
        "instructions": "Review validation dashboard, investigate issues, and approve results.",
        "estimated_time": "5 minutes",
        "required_inputs": ["Processed data", "Business rules"],
        "expected_outputs": ["Validation report", "Quality metrics", "Approved results"],
        "next_step": "reports",
        "progress": 92,
    },
    "reports": {
        "step": "10. Reports & Insights",
        "purpose": "Generate and export reports, charts, and insights from processed data.",
        "instructions": "Select report type, configure parameters, and generate or export.",
        "estimated_time": "2 minutes",
        "required_inputs": ["Validated data", "Report configuration"],
        "expected_outputs": ["Generated reports", "Exported data", "Charts and visualizations"],
        "next_step": "administration",
        "progress": 97,
    },
    "administration": {
        "step": "Administration",
        "purpose": "System administration, history, diagnostics, and settings.",
        "instructions": "Review system health, view history, and configure platform settings.",
        "estimated_time": "N/A",
        "required_inputs": [],
        "expected_outputs": ["System health status", "Activity history", "Configuration"],
        "next_step": None,
        "progress": 100,
    },
}


class GuidanceService:
    def __init__(self):
        self._guidance = dict(WORKSPACE_GUIDANCE)

    def get_guidance(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        return self._guidance.get(workspace_id)

    def get_all_guidance(self) -> Dict[str, Any]:
        return dict(self._guidance)

    def update_guidance(self, workspace_id: str, **kwargs) -> bool:
        if workspace_id in self._guidance:
            self._guidance[workspace_id].update(kwargs)
            return True
        return False

    def get_next_step(self, workspace_id: str) -> Optional[str]:
        guidance = self._guidance.get(workspace_id)
        return guidance.get("next_step") if guidance else None
