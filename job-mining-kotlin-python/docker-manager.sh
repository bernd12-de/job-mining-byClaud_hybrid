#!/bin/bash
# ========================================
# 🛠️ DOCKER MANAGEMENT QUICK COMMANDS
# ========================================
# Interaktives Menü für Docker-Management
# ========================================

set -e
cd "$(dirname "$0")"

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_menu() {
    clear
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🐳 DOCKER MANAGEMENT MENU${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "1) 📊 Container Status anzeigen"
    echo "2) 📜 Live-Logs (alle Services)"
    echo "3) 📜 Live-Logs (nur Python Backend)"
    echo "4) 📜 Live-Logs (nur Kotlin API)"
    echo "5) 🔄 Python Backend neustarten"
    echo "6) 🔄 Kotlin API neustarten"
    echo "7) 🔄 Alle Container neustarten"
    echo "8) 🛑 Alle Container stoppen"
    echo "9) 🚀 Alle Container starten"
    echo "10) 🏗️  Alle Container neu bauen und starten"
    echo "11) 🧹 Logs löschen und Container neu starten"
    echo "0) ❌ Beenden"
    echo ""
    echo -n "Auswahl: "
}

while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            echo -e "\n${BLUE}📊 Container Status:${NC}"
            docker compose ps
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        2)
            echo -e "\n${YELLOW}📜 Starte Live-Logs (alle Services)...${NC}"
            echo "Strg+C zum Beenden"
            docker compose logs -f --tail=50
            ;;
        3)
            echo -e "\n${YELLOW}📜 Starte Live-Logs (Python Backend)...${NC}"
            echo "Strg+C zum Beenden"
            docker compose logs -f --tail=100 python-backend
            ;;
        4)
            echo -e "\n${YELLOW}📜 Starte Live-Logs (Kotlin API)...${NC}"
            echo "Strg+C zum Beenden"
            docker compose logs -f --tail=100 kotlin-api
            ;;
        5)
            echo -e "\n${BLUE}🔄 Starte Python Backend neu...${NC}"
            docker compose restart python-backend
            echo -e "${GREEN}✅ Python Backend neugestartet!${NC}"
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        6)
            echo -e "\n${BLUE}🔄 Starte Kotlin API neu...${NC}"
            docker compose restart kotlin-api
            echo -e "${GREEN}✅ Kotlin API neugestartet!${NC}"
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        7)
            echo -e "\n${BLUE}🔄 Starte alle Container neu...${NC}"
            docker compose restart
            echo -e "${GREEN}✅ Alle Container neugestartet!${NC}"
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        8)
            echo -e "\n${RED}🛑 Stoppe alle Container...${NC}"
            docker compose down
            echo -e "${GREEN}✅ Alle Container gestoppt!${NC}"
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        9)
            echo -e "\n${BLUE}🚀 Starte alle Container...${NC}"
            docker compose up -d
            echo -e "${GREEN}✅ Alle Container gestartet!${NC}"
            sleep 3
            docker compose ps
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        10)
            echo -e "\n${YELLOW}🏗️  Baue Container neu und starte sie...${NC}"
            docker compose down
            docker compose up -d --build
            echo -e "${GREEN}✅ Container neu gebaut und gestartet!${NC}"
            sleep 3
            docker compose ps
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        11)
            echo -e "\n${YELLOW}🧹 Lösche Logs und starte Container neu...${NC}"
            docker compose down -v
            docker compose up -d --build
            echo -e "${GREEN}✅ Container bereinigt und neugestartet!${NC}"
            sleep 3
            docker compose ps
            read -p "Drücke Enter zum Fortfahren..."
            ;;
        0)
            echo -e "\n${GREEN}👋 Auf Wiedersehen!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}❌ Ungültige Auswahl!${NC}"
            read -p "Drücke Enter zum Fortfahren..."
            ;;
    esac
done
