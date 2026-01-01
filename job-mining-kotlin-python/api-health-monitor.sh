#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║  API Health-Check Monitor - Continuos Monitoring                              ║
# ║  Überwacht Endpoints kontinuierlich und meldet Probleme                       ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH_CHECK_SCRIPT="$SCRIPT_DIR/api-health-check.sh"
MONITOR_LOG="$SCRIPT_DIR/api-health-monitor.log"
ALERT_LOG="$SCRIPT_DIR/api-health-alerts.log"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Konfiguration
CHECK_INTERVAL=${1:-300}  # Standard: 5 Minuten
ALERT_THRESHOLD=${2:-2}   # Alert nach 2 aufeinanderfolgenden Fehlern

init_log() {
    cat >> "$MONITOR_LOG" << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Health Monitor Session: $(date)
Check Interval: ${CHECK_INTERVAL}s
Alert Threshold: ${ALERT_THRESHOLD} errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

log_event() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> "$MONITOR_LOG"
}

send_alert() {
    local subject=$1
    local details=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log alert
    cat >> "$ALERT_LOG" << EOF
[ALERT] $timestamp
Subject: $subject
Details: $details

EOF
    
    # Console notification
    echo ""
    echo -e "${RED}🚨 ALERT 🚨${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Subject: $subject"
    echo "Time:    $timestamp"
    echo "Details: $details"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

run_check() {
    local iteration=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${BLUE}[$iteration] Check @ $timestamp${NC}"
    
    # Führe Health-Check aus
    if bash "$HEALTH_CHECK_SCRIPT" > /tmp/health-check-output.txt 2>&1; then
        # Success
        local up_count=$(grep "✅" /tmp/health-check-output.txt | wc -l || echo "0")
        log_event "INFO" "Health check PASSED - $up_count endpoints OK"
        echo -e "${GREEN}✅ All systems operational${NC}"
        return 0
    else
        # Failed
        local down_count=$(grep "❌" /tmp/health-check-output.txt | wc -l || echo "unknown")
        log_event "ERROR" "Health check FAILED - $down_count endpoints DOWN"
        echo -e "${RED}❌ Issues detected${NC}"
        
        # Parse errors
        grep "LOST ENDPOINTS:" -A 30 /tmp/health-check-output.txt >> "$MONITOR_LOG" || true
        
        return 1
    fi
}

track_consecutive_failures() {
    local failure_count=$1
    
    if [ $failure_count -ge $ALERT_THRESHOLD ]; then
        send_alert \
            "API Health Check Failing" \
            "Health check has failed $failure_count times consecutively. Some endpoints are LOST."
        return 1
    fi
    return 0
}

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║  API Health Monitor                                                            ║"
    echo "║  Überwacht kontinuierlich alle ${BLUE}28 Endpoints${NC}                           ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Monitoring-Einstellungen:"
    echo "   Check-Intervall: ${CHECK_INTERVAL}s"
    echo "   Alert-Schwelle:  ${ALERT_THRESHOLD} Fehler"
    echo "   Monitor-Log:     $MONITOR_LOG"
    echo "   Alert-Log:       $ALERT_LOG"
    echo ""
    echo "Drücke Ctrl+C zum Stoppen"
    echo ""
    
    init_log
    
    local iteration=1
    local consecutive_failures=0
    
    while true; do
        if run_check "$iteration"; then
            # Success
            consecutive_failures=0
        else
            # Failure
            consecutive_failures=$((consecutive_failures + 1))
            track_consecutive_failures "$consecutive_failures"
        fi
        
        echo ""
        sleep "$CHECK_INTERVAL"
        iteration=$((iteration + 1))
    done
}

# Trap für sauberes Beenden
trap 'echo ""; echo -e "${YELLOW}Monitor beendet.${NC}"; echo "Logs verfügbar:"; echo "  • $MONITOR_LOG"; echo "  • $ALERT_LOG"; exit 0' SIGINT SIGTERM

# Hauptprogramm
if [ ! -x "$HEALTH_CHECK_SCRIPT" ]; then
    echo "❌ Health-Check Script nicht gefunden: $HEALTH_CHECK_SCRIPT"
    exit 1
fi

main
