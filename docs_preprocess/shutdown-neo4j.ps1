# CONFIG
$port = 7687
$shutdownDelaySeconds = 300

Write-Host "Checking Neo4j process on port $port..."

# Get Neo4j PID
$neo4jPID = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
       Select-Object -ExpandProperty OwningProcess |
       Where-Object { $_ -ne 0 } |
       Select-Object -Unique

if ($neo4jPID) {
    Write-Host "Neo4j PID found: $neo4jPID"
    Write-Host "Stopping Neo4j process..."

    # Try graceful stop first
    try {
        Stop-Process -Id $neo4jPID -ErrorAction Stop
        Write-Host "Neo4j stopped gracefully."
    }
    catch {
        Write-Host "Graceful stop failed, forcing shutdown..."
        Stop-Process -Id $neo4jPID -Force
    }
}
else {
    Write-Host "Neo4j is not running."
}

Write-Host "Scheduling system shutdown in $shutdownDelaySeconds seconds..."

Start-Process "shutdown.exe" -ArgumentList "/s /t $shutdownDelaySeconds /f"