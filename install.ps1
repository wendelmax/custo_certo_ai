# Custo Certo AI - Installer
# Uso: iex (iwr 'https://raw.githubusercontent.com/wendelmax/custo_certo_ai/main/install.ps1').Content

$RepoOwner = "wendelmax"
$RepoName = "custo_certo_ai"
$Branch = "main"
$GithubRaw = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/$Branch"
$GithubZip = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/$Branch.zip"
$PythonVersion = "3.12.3"

$InstallDir = "$env:USERPROFILE\custo_certo"
$RuntimeDir = "$InstallDir\_runtime"
$PythonDir = "$RuntimeDir\python"
$PythonExe = "$PythonDir\python.exe"

function Write-Step {
    param([string]$M, [string]$C = "White")
    Write-Host ">> $M" -ForegroundColor $C
}

function Test-Command {
    param([string]$Cmd)
    return [bool](Get-Command $Cmd -ErrorAction SilentlyContinue)
}

Clear-Host
Write-Host ""
Write-Host "  ╔═══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║    CUSTO CERTO AI - INSTALADOR        ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Baixar o projeto ─────────────────────────────────────────────────────

Write-Step "Baixando projeto do GitHub..." Yellow
try {
    $zipPath = "$env:TEMP\custo_certo.zip"
    if (Test-Command "curl.exe") {
        & curl.exe -sL $GithubZip -o $zipPath
    } else {
        [System.Net.WebClient]::new().DownloadFile($GithubZip, $zipPath)
    }

    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force "$InstallDir\*" -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

    if (Test-Command "tar.exe") {
        & tar.exe -xf $zipPath -C "$env:TEMP" 2>$null
        $extracted = "$env:TEMP\$RepoName-$Branch"
        if (Test-Path $extracted) {
            Get-ChildItem -Path "$extracted\*" | Move-Item -Destination $InstallDir -Force
            Remove-Item -Recurse -Force $extracted
        }
    }
    # Se tar nao funcionou, usa Expand-Archive
    if (-not (Test-Path "$InstallDir\app.py")) {
        Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP" -Force
        Get-ChildItem -Path "$env:TEMP\$RepoName-$Branch\*" | Move-Item -Destination $InstallDir -Force
        Remove-Item -Recurse -Force "$env:TEMP\$RepoName-$Branch"
    }
    Remove-Item $zipPath -Force
} catch {
    Write-Step "Falha ao baixar projeto: $_" Red
    exit 1
}
Write-Step "Projeto baixado para $InstallDir" Green

# ─── 2. Baixar Python portatil ────────────────────────────────────────────────

Write-Step "Baixando Python $PythonVersion (portatil)..." Yellow
New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

$pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
$pythonZip = "$RuntimeDir\python.zip"

try {
    if (Test-Command "curl.exe") {
        & curl.exe -sL $pythonUrl -o $pythonZip
    } else {
        [System.Net.WebClient]::new().DownloadFile($pythonUrl, $pythonZip)
    }
    Expand-Archive -Path $pythonZip -DestinationPath $PythonDir -Force
    Remove-Item $pythonZip -Force
} catch {
    Write-Step "Falha ao baixar Python: $_" Red
    exit 1
}

# Habilita site-packages
$pthFile = "$PythonDir\python._pth"
$content = Get-Content $pthFile -Raw
if ($content -notmatch '(?m)^import site$') {
    $content = $content -replace '(?m)^#import site', 'import site'
    Set-Content -Path $pthFile -Value $content
}
Write-Step "Python $PythonVersion instalado" Green

# ─── 3. Instalar pip ──────────────────────────────────────────────────────────

Write-Step "Instalando pip..." Yellow
$getPip = "$RuntimeDir\get-pip.py"
try {
    if (Test-Command "curl.exe") {
        & curl.exe -sL "https://bootstrap.pypa.io/get-pip.py" -o $getPip
    } else {
        [System.Net.WebClient]::new().DownloadFile("https://bootstrap.pypa.io/get-pip.py", $getPip)
    }
    & $PythonExe $getPip --no-warn-script-location 2>&1 | Out-Null
    Remove-Item $getPip -Force
} catch {
    Write-Step "Falha ao instalar pip: $_" Red
    exit 1
}

$env:Path = "$PythonDir;$PythonDir\Scripts;$env:Path"

# ─── 4. Instalar dependencias ─────────────────────────────────────────────────

Write-Step "Instalando dependencias..." Yellow
& $PythonExe -m pip install -r "$InstallDir\requirements.txt" --quiet 2>&1 | Out-Null
Write-Step "Dependencias instaladas" Green

# ─── 5. Criar atalhos ─────────────────────────────────────────────────────────

# Desktop shortcut
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = "$desktop\Custo Certo AI.lnk"
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($shortcut)
$link.TargetPath = "powershell.exe"
$link.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$InstallDir\run.ps1`""
$link.WorkingDirectory = $InstallDir
$link.Description = "Custo Certo AI - Analise de Custos Industriais"
$link.Save()
Write-Step "Atalho criado na Area de Trabalho" Green

# Start Menu shortcut
$startMenu = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Custo Certo AI"
if (-not (Test-Path $startMenu)) {
    New-Item -ItemType Directory -Force -Path $startMenu | Out-Null
}
$link2 = $shell.CreateShortcut("$startMenu\Custo Certo AI.lnk")
$link2.TargetPath = "powershell.exe"
$link2.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$InstallDir\run.ps1`""
$link2.WorkingDirectory = $InstallDir
$link2.Description = "Custo Certo AI - Analise de Custos Industriais"
$link2.Save()

Write-Host ""
Write-Host "  ╔═══════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║  INSTALACAO CONCLUIDA!                ║" -ForegroundColor Green
Write-Host "  ╚═══════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Projeto:  $InstallDir" -ForegroundColor White
Write-Host "  Atalho:   Area de Trabalho" -ForegroundColor White
Write-Host ""

$choice = Read-Host "  Iniciar o Custo Certo AI agora? (S/N)"
if ($choice -eq "S" -or $choice -eq "s") {
    & powershell.exe -ExecutionPolicy Bypass -NoProfile -File "$InstallDir\run.ps1"
}
