#!/bin/bash
# ============================================================
# SJKNCS 同步脚本 (Linux/macOS)
# ============================================================
# 用法：
#   ./sync.sh check     - 检查更新
#   ./sync.sh pull      - 拉取更新
#   ./sync.sh status    - 查看本地版本状态
#   ./sync.sh backup    - 备份当前规则
#   ./sync.sh restore   - 从备份恢复
# ============================================================

set -e

REPO_URL="https://github.com/sjkncs/sjkncs.git"
LOCAL_DIR="${HOME}/.codebuddy/sjkncs"
BACKUP_DIR="${HOME}/.codebuddy/backups/sjkncs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       SJKNCS 七维治理体系 同步工具       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

check_update() {
    echo -e "${YELLOW}[检查] 正在查询远程版本...${NC}"

    if [ ! -d "$LOCAL_DIR" ]; then
        echo -e "${RED}[提示] 本地未安装 SJKNCS，请先执行安装。${NC}"
        echo -e "  git clone $REPO_URL \"$LOCAL_DIR\""
        return
    fi

    cd "$LOCAL_DIR"
    local_version=$(python3 -c "import json; print(json.load(open('version.json'))['version'])" 2>/dev/null || \
                    python -c "import json; print(json.load(open('version.json'))['version'])" 2>/dev/null)
    echo -e "${GREEN}[本地] 版本: v${local_version}${NC}"

    git fetch origin 2>/dev/null
    remote_version=$(git show origin/main:version.json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])" 2>/dev/null || echo "")

    if [ -n "$remote_version" ]; then
        echo -e "${BLUE}[远程] 版本: v${remote_version}${NC}"

        if [ "$local_version" != "$remote_version" ]; then
            echo ""
            echo -e "${GREEN}[更新] 有新版本可用！v${local_version} → v${remote_version}${NC}"
            echo -e "${YELLOW}[操作] 运行 ./sync.sh pull 来更新${NC}"
        else
            echo -e "${GREEN}[状态] 已是最新版本 ✓${NC}"
        fi
    else
        echo -e "${RED}[警告] 无法获取远程版本信息${NC}"
    fi
}

pull_update() {
    echo -e "${YELLOW}[更新] 正在拉取最新版本...${NC}"

    if [ ! -d "$LOCAL_DIR" ]; then
        echo -e "${YELLOW}[提示] 本地未安装 SJKNCS，正在克隆...${NC}"
        git clone "$REPO_URL" "$LOCAL_DIR"
        echo -e "${GREEN}[完成] 已安装到 $LOCAL_DIR${NC}"
        return
    fi

    # Backup
    timestamp=$(date +"%Y-%m-%d_%H%M%S")
    backup_path="$BACKUP_DIR/$timestamp"
    mkdir -p "$backup_path"
    cp -r "$LOCAL_DIR/.codebuddy/"* "$backup_path/" 2>/dev/null || true
    echo -e "${GREEN}[备份] 已备份到 $backup_path${NC}"

    # Pull
    cd "$LOCAL_DIR"
    before_version=$(python3 -c "import json; print(json.load(open('version.json'))['version'])" 2>/dev/null || echo "?")
    git stash 2>/dev/null || true
    git pull origin main

    after_version=$(python3 -c "import json; print(json.load(open('version.json'))['version'])" 2>/dev/null || echo "?")
    echo -e "${GREEN}[完成] v${before_version} → v${after_version}${NC}"

    # Show changelog
    echo ""
    echo -e "${CYAN}更新内容：${NC}"
    python3 -c "
import json
data = json.load(open('version.json'))
for entry in data['changelog']:
    print(f\"  v{entry['version']} ({entry['date']}):\")
    for change in entry['changes']:
        print(f'    - {change}')
" 2>/dev/null || true
}

show_status() {
    echo -e "${CYAN}[状态] 当前 SJKNCS 配置状态${NC}"
    echo ""

    if [ ! -d "$LOCAL_DIR" ]; then
        echo -e "${RED}  安装状态: 未安装${NC}"
        echo -e "  安装命令: git clone $REPO_URL \"$LOCAL_DIR\""
        return
    fi

    version=$(python3 -c "import json; print(json.load(open('$LOCAL_DIR/version.json'))['version'])" 2>/dev/null || echo "?")
    echo -e "${GREEN}  安装状态: 已安装${NC}"
    echo -e "${GREEN}  本地版本: v${version}${NC}"
    echo -e "  安装路径: $LOCAL_DIR"
    echo ""

    echo -e "${CYAN}已安装技能：${NC}"
    python3 -c "
import json
data = json.load(open('$LOCAL_DIR/version.json'))
for name, info in data['skills'].items():
    print(f'  ✓ {name} (v{info[\"version\"]})')
" 2>/dev/null || true
}

do_backup() {
    timestamp=$(date +"%Y-%m-%d_%H%M%S")
    backup_path="$BACKUP_DIR/$timestamp"
    mkdir -p "$backup_path"

    if [ ! -d "$LOCAL_DIR" ]; then
        echo -e "${RED}[错误] 本地未安装，无需备份${NC}"
        return
    fi

    cp -r "$LOCAL_DIR/.codebuddy/"* "$backup_path/" 2>/dev/null || true
    echo -e "${GREEN}[备份] 已完成 → $backup_path${NC}"
    echo -e "${YELLOW}[提示] 备份保留 30 天${NC}"
}

do_restore() {
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}[错误] 没有找到备份${NC}"
        return
    fi

    backups=($(ls -d "$BACKUP_DIR"/*/ 2>/dev/null | sort -r))
    if [ ${#backups[@]} -eq 0 ]; then
        echo -e "${RED}[错误] 没有找到备份${NC}"
        return
    fi

    echo -e "${CYAN}可用备份：${NC}"
    for i in "${!backups[@]}"; do
        echo "  [$i] $(basename ${backups[$i]})"
    done

    read -p "选择要恢复的备份编号: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -lt "${#backups[@]}" ]; then
        selected="${backups[$choice]}"
        cp -r "$selected"* "$LOCAL_DIR/.codebuddy/"
        echo -e "${GREEN}[恢复] 已从 $(basename $selected) 恢复${NC}"
    else
        echo -e "${RED}[取消] 无效选择${NC}"
    fi
}

# ---- Main ----
banner

case "${1:-status}" in
    check)  check_update ;;
    pull)   pull_update ;;
    status) show_status ;;
    backup) do_backup ;;
    restore)do_restore ;;
    *)      echo "用法: $0 {check|pull|status|backup|restore}" ;;
esac
