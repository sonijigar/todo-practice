#!/usr/bin/env bash
# Start Grafana with project-local provisioning (no Docker, no login)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROV_DIR="$SCRIPT_DIR/provisioning"
DASH_DIR="$PROV_DIR/dashboards"
GRAFANA_HOME="$(brew --prefix grafana)/share/grafana"

# Patch dashboards.yml with the absolute path to dashboard JSON files
sed -i '' "s|path:.*|path: $DASH_DIR|" "$DASH_DIR/dashboards.yml"

echo "── Grafana home:    $GRAFANA_HOME"
echo "── Provisioning:    $PROV_DIR"
echo "── Dashboards dir:  $DASH_DIR"
echo "── URL:             http://localhost:3000  (no login required)"
echo ""

exec grafana server \
  --homepath="$GRAFANA_HOME" \
  --config="$GRAFANA_HOME/conf/defaults.ini" \
  cfg:paths.provisioning="$PROV_DIR" \
  cfg:paths.data="$SCRIPT_DIR/.grafana-data" \
  cfg:paths.logs="$SCRIPT_DIR/.grafana-data/logs" \
  cfg:server.http_port=3000 \
  cfg:auth.anonymous.enabled=true \
  cfg:auth.anonymous.org_role=Admin
