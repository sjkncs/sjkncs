# ============================================================
# SJKNCS 同步脚本 (Windows PowerShell)
# ============================================================
# 用法：
#   .\sync.ps1 check     - 检查更新
#   .\sync.ps1 pull      - 拉取更新
#   .\sync.ps1 status    - 查看本地版本状态
#   .\sync.ps1 backup    - 备份当前规则
#   .\sync.ps1 restore   - 从备份恢复
# ============================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("check", "pull", "status", "backup", "restore")]
    [string]$Action = "status"
)

$REPO_URL = "https://github.com/sjkncs/sjkncs.git"
$LOCAL_DIR = "$env:USERPROFILE\.codebuddy\sjkncs"
$BACKUP_DIR = "$env:USERPROFILE\.codebuddy\backups\sjkncs"

function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       SJKNCS 七维治理体系 同步工具       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-CheckUpdate {
    Write-Host "[检查] 正在查询远程版本..." -ForegroundColor Yellow

    if (-not (Test-Path $LOCAL_DIR)) {
        Write-Host "[提示] 本地未安装 SJKNCS，请先执行安装。" -ForegroundColor Red
        Write-Host "  git clone $REPO_URL `"$LOCAL_DIR`"" -ForegroundColor White
        return
    }

    Push-Location $LOCAL_DIR
    try {
        $localVersion = (Get-Content "version.json" -Raw | ConvertFrom-Json).version
        Write-Host "[本地] 版本: v$localVersion" -ForegroundColor Green

        git fetch origin 2>&1 | Out-Null
        $remoteVersion = (git show origin/main:version.json 2>$null | ConvertFrom-Json).version

        if ($remoteVersion) {
            Write-Host "[远程] 版本: v$remoteVersion" -ForegroundColor Blue

            if ($localVersion -ne $remoteVersion) {
                Write-Host ""
                Write-Host "[更新] 有新版本可用！v$localVersion → v$remoteVersion" -ForegroundColor Green
                Write-Host "[操作] 运行 .\sync.ps1 pull 来更新" -ForegroundColor Yellow
            } else {
                Write-Host "[状态] 已是最新版本 ✓" -ForegroundColor Green
            }
        } else {
            Write-Host "[警告] 无法获取远程版本信息" -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
}

function Invoke-PullUpdate {
    Write-Host "[更新] 正在拉取最新版本..." -ForegroundColor Yellow

    if (-not (Test-Path $LOCAL_DIR)) {
        Write-Host "[提示] 本地未安装 SJKNCS，正在克隆..." -ForegroundColor Yellow
        git clone $REPO_URL $LOCAL_DIR 2>&1
        Write-Host "[完成] 已安装到 $LOCAL_DIR" -ForegroundColor Green
        return
    }

    # 备份当前版本
    $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $backupPath = "$BACKUP_DIR\$timestamp"
    New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
    Copy-Item -Path "$LOCAL_DIR\.codebuddy\*" -Destination $backupPath -Recurse -Force
    Write-Host "[备份] 已备份到 $backupPath" -ForegroundColor Green

    # 拉取更新
    Push-Location $LOCAL_DIR
    try {
        $beforeVersion = (Get-Content "version.json" -Raw | ConvertFrom-Json).version

        git stash 2>&1 | Out-Null
        git pull origin main 2>&1

        $afterVersion = (Get-Content "version.json" -Raw | ConvertFrom-Json).version
        Write-Host "[完成] v$beforeVersion → v$afterVersion" -ForegroundColor Green

        # 显示 changelog
        $changelog = (Get-Content "version.json" -Raw | ConvertFrom-Json).changelog
        Write-Host ""
        Write-Host "更新内容：" -ForegroundColor Cyan
        foreach ($entry in $changelog) {
            Write-Host "  v$($entry.version) ($($entry.date)):" -ForegroundColor Yellow
            foreach ($change in $entry.changes) {
                Write-Host "    - $change" -ForegroundColor White
            }
        }
    } finally {
        Pop-Location
    }
}

function Invoke-ShowStatus {
    Write-Host "[状态] 当前 SJKNCS 配置状态" -ForegroundColor Cyan
    Write-Host ""

    if (-not (Test-Path $LOCAL_DIR)) {
        Write-Host "  安装状态: 未安装" -ForegroundColor Red
        Write-Host "  安装命令: git clone $REPO_URL `"$LOCAL_DIR`"" -ForegroundColor White
        return
    }

    $version = (Get-Content "$LOCAL_DIR\version.json" -Raw | ConvertFrom-Json).version
    Write-Host "  安装状态: 已安装" -ForegroundColor Green
    Write-Host "  本地版本: v$version" -ForegroundColor Green
    Write-Host "  安装路径: $LOCAL_DIR" -ForegroundColor White
    Write-Host ""

    $skills = (Get-Content "$LOCAL_DIR\version.json" -Raw | ConvertFrom-Json).skills
    Write-Host "已安装技能：" -ForegroundColor Cyan
    foreach ($skill in $skills.PSObject.Properties) {
        $color = if ($skill.Value.version -eq $version) { "Green" } else { "Yellow" }
        Write-Host "  ✓ $($skill.Name) (v$($skill.Value.version))" -ForegroundColor $color
    }
}

function Invoke-Backup {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $backupPath = "$BACKUP_DIR\$timestamp"
    New-Item -ItemType Directory -Force -Path $backupPath | Out-Null

    if (-not (Test-Path $LOCAL_DIR)) {
        Write-Host "[错误] 本地未安装，无需备份" -ForegroundColor Red
        return
    }

    Copy-Item -Path "$LOCAL_DIR\.codebuddy\*" -Destination $backupPath -Recurse -Force
    Write-Host "[备份] 已完成 → $backupPath" -ForegroundColor Green
    Write-Host "[提示] 备份保留 30 天" -ForegroundColor White
}

function Invoke-Restore {
    $backups = Get-ChildItem $BACKUP_DIR -Directory -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending

    if (-not $backups) {
        Write-Host "[错误] 没有找到备份" -ForegroundColor Red
        return
    }

    Write-Host "可用备份：" -ForegroundColor Cyan
    for ($i = 0; $i -lt $backups.Count; $i++) {
        Write-Host "  [$i] $($backups[$i].Name)" -ForegroundColor White
    }

    $choice = Read-Host "选择要恢复的备份编号"
    if ($choice -match '^\d+$' -and [int]$choice -lt $backups.Count) {
        $selected = $backups[[int]$choice]
        Copy-Item -Path $selected.FullName\* -Destination "$LOCAL_DIR\.codebuddy\" -Recurse -Force
        Write-Host "[恢复] 已从 $($selected.Name) 恢复" -ForegroundColor Green
    } else {
        Write-Host "[取消] 无效选择" -ForegroundColor Red
    }
}

# ---- Main ----
Write-Banner

switch ($Action) {
    "check"  { Invoke-CheckUpdate }
    "pull"   { Invoke-PullUpdate }
    "status" { Invoke-ShowStatus }
    "backup" { Invoke-Backup }
    "restore"{ Invoke-Restore }
}
