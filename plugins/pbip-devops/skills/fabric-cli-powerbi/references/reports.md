# Reports Reference

Working with Power BI reports via Fabric CLI.

## Item Type

Use `.Report` suffix when referencing reports:

```bash
# Reference format
ws.Workspace/ReportName.Report
```

## List Reports

```bash
# List in current workspace
fab ls . -t Report

# List in specific workspace
fab ls "ws.Workspace" -t Report

# List with details
fab ls "ws.Workspace" -t Report -v
```

## Get Report Details

```bash
# Get report metadata
fab get "ws.Workspace/SalesReport.Report"

# Get specific property
fab get "ws.Workspace/SalesReport.Report" -q "id"

# Get report via API
WS_ID=$(fab get "ws.Workspace" -q "id" | tr -d '"')
REPORT_ID=$(fab get "ws.Workspace/SalesReport.Report" -q "id" | tr -d '"')
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID"
```

## Export Reports

### Export as PBIX

```bash
fab export "ws.Workspace/SalesReport.Report" -d ./exports
```

### Export to File Format

```bash
# Export to PDF
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{
  "format": "PDF"
}' -o report.pdf

# Export to PNG
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{
  "format": "PNG",
  "powerBIReportConfiguration": {
    "pages": [{"pageName": "Page1"}]
  }
}' -o report.png

# Export to PPTX (PowerPoint)
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{
  "format": "PPTX"
}' -o report.pptx
```

### Export Paginated Report

```bash
# Export to PDF with parameters
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{
  "format": "PDF",
  "paginatedReportConfiguration": {
    "parameterValues": [
      {"name": "Year", "value": "2024"},
      {"name": "Region", "value": "West"}
    ]
  }
}'
```

### Async Export (Large Reports)

```bash
# Start export job
EXPORT_RESULT=$(fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{
  "format": "PDF"
}')
EXPORT_ID=$(echo $EXPORT_RESULT | jq -r '.id')

# Poll for completion
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/exports/$EXPORT_ID"

# Download when complete
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/exports/$EXPORT_ID/file" -o report.pdf
```

## Import Reports

### Import PBIX (Contains Report)

```bash
fab import ./report.pbix -d "ws.Workspace"

# Skip creating new dataset (rebind to existing)
fab import ./report.pbix -d "ws.Workspace" -c CreateOrOverwrite
```

## Clone Report

```bash
# Clone within same workspace
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Clone" -X post -i '{
  "name": "SalesReport_Copy"
}'

# Clone to different workspace
TARGET_WS_ID=$(fab get "target.Workspace" -q "id" | tr -d '"')
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Clone" -X post -i '{
  "name": "SalesReport_Copy",
  "targetWorkspaceId": "'"$TARGET_WS_ID"'"
}'

# Clone and rebind to different dataset
TARGET_MODEL_ID=$(fab get "target.Workspace/Model.SemanticModel" -q "id" | tr -d '"')
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Clone" -X post -i '{
  "name": "SalesReport_Copy",
  "targetWorkspaceId": "'"$TARGET_WS_ID"'",
  "targetModelId": "'"$TARGET_MODEL_ID"'"
}'
```

## Rebind Report

Change the semantic model a report connects to:

```bash
# Get current binding
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID"

# Rebind to new dataset in same workspace
NEW_MODEL_ID=$(fab get "ws.Workspace/NewModel.SemanticModel" -q "id" | tr -d '"')
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Rebind" -X post -i '{
  "datasetId": "'"$NEW_MODEL_ID"'"
}'
```

## Report Pages

### Get Pages

```bash
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/pages"
```

### Get Single Page

```bash
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/pages/Page1"
```

## Update Report

### Update Report Content

```bash
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/UpdateReportContent" -X post -i '{
  "sourceReport": {
    "sourceReportId": "'"$SOURCE_REPORT_ID"'",
    "sourceWorkspaceId": "'"$SOURCE_WS_ID"'"
  },
  "sourceType": "ExistingReport"
}'
```

### Update Report Definition (PBIR project files → Fabric)

Deploying the PBIR files of a `.Report` folder is an **item definition update** on the Fabric
API, not a Power BI REST call — approval gate, part encoding, the `byConnection` requirement
and the RegisteredResources caveat live in `pbip-deploy` (reference.md §4, §4.2):

```bash
# parts: definition/** + StaticResources/** + definition.pbir, each InlineBase64
fab api -A fabric "workspaces/$WS_ID/reports/$REPORT_ID/updateDefinition" -X post -i @definition.json
# verify the -A value and the long-running-operation polling in `fab api --help` before relying on it
```

### Navigation smoke test after deploy

Export one PNG per visible page (`ExportTo` above, `"format": "PNG"`, `pages: [{pageName}]`) —
a page that fails to render fails to export. Full checklist → `pbip-deploy` reference.md §4.3.

## Delete Report

```bash
# Delete via fab
fab rm "ws.Workspace/SalesReport.Report"

# Delete via API
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID" -X delete
```

## Report Permissions

### Get Report Users

```bash
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/users"
```

## Subscriptions

### Get Report Subscriptions

```bash
fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/subscriptions"
```

## Quick Reference

| Operation | Command |
|-----------|---------|
| List reports | `fab ls "ws.Workspace" -t Report` |
| Get report | `fab get "ws.Workspace/Report.Report"` |
| Export PBIX | `fab export "ws.Workspace/Report.Report" -d ./` |
| Export PDF | `fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/ExportTo" -X post -i '{"format":"PDF"}'` |
| Clone report | `fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Clone" -X post -i '{...}'` |
| Rebind dataset | `fab api -A powerbi "groups/$WS_ID/reports/$REPORT_ID/Rebind" -X post -i '{...}'` |
| Delete report | `fab rm "ws.Workspace/Report.Report"` |

## See Also

- [Semantic Models](./semantic-models.md) - Manage underlying data
- [Refresh Operations](./refresh.md) - Refresh data
