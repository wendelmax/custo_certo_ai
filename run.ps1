param(
    [switch]$ResetPython,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$RuntimeDir = Join-Path $ProjectRoot "_runtime"
$PythonDir = Join-Path $RuntimeDir "python"
$PythonExe = Join-Path $PythonDir "python.exe"
$PythonVersion = "3.12.3"

function Write-Step {
    param([string]$Message, [string]$Color = "White")
    Write-Host ">> $Message" -ForegroundColor $Color
}

function Test-CommandAvailable {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

Write-Host ""
Write-Host "  ╔═══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       CUSTO CERTO AI - LAUNCHER       ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─── Step 1: Check / Download Python ──────────────────────────────────────────

$needPython = $ResetPython -or -not (Test-Path $PythonExe)

if ($needPython) {
    if (Test-Path $PythonDir) {
        Remove-Item -Recurse -Force $PythonDir
    }

    $url = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
    $zipPath = Join-Path $RuntimeDir "python.zip"

    Write-Step "Baixando Python $PythonVersion (portatil)..." Yellow
    New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

    try {
        if (Test-CommandAvailable "curl.exe") {
            & curl.exe -sL $url -o $zipPath
        } else {
            [System.Net.WebClient]::new().DownloadFile($url, $zipPath)
        }
    } catch {
        Write-Step "Falha ao baixar Python. Verifique sua conexao." Red
        exit 1
    }

    Write-Step "Extraindo..." Yellow
    if (Test-CommandAvailable "tar.exe") {
        & tar.exe -xf $zipPath -C $PythonDir 2>$null
        if (-not (Test-Path $PythonExe)) {
            Expand-Archive -Path $zipPath -DestinationPath $PythonDir -Force
        }
    } else {
        Expand-Archive -Path $zipPath -DestinationPath $PythonDir -Force
    }
    Remove-Item $zipPath -Force

    Write-Step "Python $PythonVersion pronto" Green
} else {
    Write-Step "Python encontrado em $PythonDir" Green
}

# ─── Step 2: Enable site-packages ─────────────────────────────────────────────

$pthFile = Join-Path $PythonDir "python._pth"
if (Test-Path $pthFile) {
    $content = Get-Content $pthFile -Raw
    if ($content -notmatch '(?m)^import site$') {
        $content = $content -replace '(?m)^#import site', 'import site'
        Set-Content -Path $pthFile -Value $content
        Write-Step "site-packages habilitado" Green
    }
}

# ─── Step 3: Install pip ──────────────────────────────────────────────────────

$pipScript = Join-Path $PythonDir "Scripts\pip.exe"
if (-not (Test-Path $pipScript)) {
    Write-Step "Instalando pip..." Yellow
    $getPip = Join-Path $RuntimeDir "get-pip.py"

    try {
        if (Test-CommandAvailable "curl.exe") {
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
    Write-Step "pip instalado" Green
}

# ─── Step 4: Add Python to PATH (session only) ────────────────────────────────

$pythonScripts = Join-Path $PythonDir "Scripts"
$env:Path = "$PythonDir;$pythonScripts;$env:Path"

# ─── Step 5: Install dependencies ─────────────────────────────────────────────

$reqFile = Join-Path $ProjectRoot "requirements.txt"
Write-Step "Instalando dependencias..." Yellow
try {
    & $PythonExe -m pip install -r $reqFile --quiet 2>&1 | Out-Null
} catch {
    Write-Step "Falha ao instalar dependencias: $_" Red
    exit 1
}
Write-Step "Dependencias instaladas" Green

# ─── Step 6: Verify / Setup .env ─────────────────────────────────────────────

$envFile = Join-Path $ProjectRoot ".env"
$Providers = @(
    @{ Name = "Google Gemini";         Env = "GEMINI_API_KEY" }
    @{ Name = "OpenAI";                Env = "OPENAI_API_KEY" }
    @{ Name = "Anthropic Claude";      Env = "ANTHROPIC_API_KEY" }
    @{ Name = "Groq";                  Env = "GROQ_API_KEY" }
    @{ Name = "OpenRouter";            Env = "OPENROUTER_API_KEY" }
    @{ Name = "Hugging Face";          Env = "HF_TOKEN" }
    @{ Name = "Cerebras";              Env = "CEREBRAS_API_KEY" }
    @{ Name = "Moonshot";              Env = "MOONSHOT_API_KEY" }
    @{ Name = "DeepSeek (Alibaba SG)"; Env = "ALIBABA_SINGAPORE_API_KEY" }
    @{ Name = "DeepSeek (Alibaba US)"; Env = "ALIBABA_US_API_KEY" }
    @{ Name = "Z.ai";                  Env = "ZAI_API_KEY" }
    @{ Name = "MiniMax";               Env = "MINIMAX_API_KEY" }
    @{ Name = "Synthetic";             Env = "SYNTHETIC_API_KEY" }
    @{ Name = "Avian";                 Env = "AVIAN_API_KEY" }
)

$hasCredential = $false
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    foreach ($p in $Providers) {
        if ($envContent -match "$($p.Env)=") {
            $hasCredential = $true
            break
        }
    }
}

if (-not $hasCredential) {
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "  ║    CONFIGURACAO DE CREDENCIAL         ║" -ForegroundColor Yellow
    Write-Host "  ╚═══════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Step "Nenhuma chave de API encontrada no .env" Yellow
    Write-Step "Escolha um provedor:" White
    Write-Host ""

    for ($i = 0; $i -lt $Providers.Count; $i++) {
        Write-Host "  $($i + 1). $($Providers[$i].Name) - $($Providers[$i].Env)" -ForegroundColor White
    }
    Write-Host "  $($Providers.Count + 1). Digitar manual (qualquer env)" -ForegroundColor White
    Write-Host ""

    $choice = $null
    do {
        $input = Read-Host "  Escolha (1..$($Providers.Count + 1))"
        $choice = [int]::TryParse($input, [ref]$choice) ? $choice : $null
    } while ($null -eq $choice -or $choice -lt 1 -or $choice -gt $Providers.Count + 1)

    if ($choice -eq $Providers.Count + 1) {
        $envName = Read-Host "  Nome da variavel (ex: GEMINI_API_KEY)"
        $envValue = Read-Host "  Valor da chave"
    } else {
        $selected = $Providers[$choice - 1]
        $envName = $selected.Env
        $envValue = Read-Host "  Informe sua chave $($selected.Name)"
    }

    Set-Content -Path $envFile -Value "$envName=$envValue" -Encoding ASCII
    Write-Step "Credencial salva em .env" Green
} else {
    Write-Step ".env OK" Green
}

Write-Host ""
Write-Step "Servidor iniciando em http://localhost:5000" Cyan
Write-Step "Pressione Ctrl+C para parar" Gray

# ─── Step 7: Launch ──────────────────────────────────────────────────────────

if (-not $NoBrowser) {
    Start-Process "http://localhost:5000"
}

& $PythonExe (Join-Path $ProjectRoot "app.py")
