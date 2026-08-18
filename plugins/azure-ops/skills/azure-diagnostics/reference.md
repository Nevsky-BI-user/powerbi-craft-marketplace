# Azure Diagnostics — Reference

Overflow from SKILL.md. Per-service depth stays in the existing
[references/](references/) and [troubleshooting/](troubleshooting/) trees —
this file does not duplicate those guides.

## §1. Triggers

Activate this skill when user wants to:
- Debug or troubleshoot production issues
- Diagnose errors in Azure services
- Analyze application logs or metrics
- Fix image pull, cold start, or health probe issues
- Investigate why Azure resources are failing
- Find root cause of application errors
- Troubleshoot App Service issues (high CPU, deployment failures, crashes, slow responses, TLS/custom domains)
- Respond to prompts like "troubleshoot app service", "app service high CPU", or "app service deployment failure"
- Troubleshoot Azure Function Apps (invocation failures, timeouts, binding errors)
- Find the App Insights or Log Analytics workspace linked to a Function App
- Troubleshoot AKS clusters, nodes, pods, ingress, or Kubernetes networking issues
- Troubleshoot Azure Messaging SDK issues (Event Hubs, Service Bus connection failures, AMQP errors, message lock issues)

## §2. AppLens (MCP Tools)

For AI-powered diagnostics, use:
```
mcp_azure_mcp_applens
  intent: "diagnose issues with <resource-name>"
  command: "diagnose"
  parameters:
    resourceId: "<resource-id>"

Provides:
- Automated issue detection
- Root cause analysis
- Remediation recommendations
```

## §3. Azure Monitor (MCP Tools)

For querying logs and metrics:
```
mcp_azure_mcp_monitor
  intent: "query logs for <resource-name>"
  command: "logs_query"
  parameters:
    workspaceId: "<workspace-id>"
    query: "<KQL-query>"
```

See [kql-queries.md](references/kql-queries.md) for common diagnostic queries.

## §4. Check Azure Resource Health

### Using MCP

```
mcp_azure_mcp_resourcehealth
  intent: "check health status of <resource-name>"
  command: "get"
  parameters:
    resourceId: "<resource-id>"
```

### Using CLI

```bash
# Check specific resource health
az resource show --ids RESOURCE_ID

# Check recent activity
az monitor activity-log list -g RG --max-events 20
```
