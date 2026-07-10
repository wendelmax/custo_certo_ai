# Custo Certo AI - Installer
# Uso: iex (iwr 'https://raw.githubusercontent.com/wendelmax/custo_certo_ai/main/install.ps1').Content

$RepoOwner = "wendelmax"
$RepoName = "custo_certo_ai"
$Branch = "main"
$GithubRaw = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/$Branch"
$GithubZip = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/$Branch.zip"
$PythonVersion = "3.12.3"

$InstallDir = "$env:USERPROFILE\custo_certo"
$Providers = @(
    @{ Name = "Google Gemini";         Env = "GEMINI_API_KEY";              Tier = "GRATIS";     Url = "https://aistudio.google.com/apikey" }
    @{ Name = "Groq";                  Env = "GROQ_API_KEY";                Tier = "GRATIS";     Url = "https://console.groq.com/keys" }
    @{ Name = "Hugging Face";          Env = "HF_TOKEN";                    Tier = "GRATIS";     Url = "https://huggingface.co/settings/tokens" }
    @{ Name = "Cerebras";              Env = "CEREBRAS_API_KEY";            Tier = "GRATIS";     Url = "https://inference.cerebras.ai/" }
    @{ Name = "DeepSeek (Alibaba US)"; Env = "ALIBABA_US_API_KEY";         Tier = "GRATIS";     Url = "https://www.alibabacloud.com/" }
    @{ Name = "Z.ai";                  Env = "ZAI_API_KEY";                Tier = "GRATIS";     Url = "https://z.ai/" }
    @{ Name = "Synthetic";             Env = "SYNTHETIC_API_KEY";          Tier = "GRATIS";     Url = "https://synthetic.com/" }
    @{ Name = "Avian";                 Env = "AVIAN_API_KEY";              Tier = "GRATIS";     Url = "https://avian.io/" }
    @{ Name = "OpenRouter";            Env = "OPENROUTER_API_KEY";         Tier = "GRATIS+PAGO"; Url = "https://openrouter.ai/keys" }
    @{ Name = "OpenAI";                Env = "OPENAI_API_KEY";             Tier = "PAGO";       Url = "https://platform.openai.com/api-keys" }
    @{ Name = "Anthropic Claude";      Env = "ANTHROPIC_API_KEY";          Tier = "PAGO";       Url = "https://console.anthropic.com/" }
    @{ Name = "Azure OpenAI";          Env = "AZURE_OPENAI_API_KEY";       Tier = "PAGO";       Url = "https://portal.azure.com/" }
    @{ Name = "Amazon Bedrock";        Env = "AWS_ACCESS_KEY_ID";          Tier = "PAGO";       Url = "https://console.aws.amazon.com/bedrock/" }
    @{ Name = "Moonshot";              Env = "MOONSHOT_API_KEY";           Tier = "PAGO";       Url = "https://platform.moonshot.cn/" }
    @{ Name = "DeepSeek (Alibaba SG)"; Env = "ALIBABA_SINGAPORE_API_KEY";  Tier = "PAGO";       Url = "https://www.alibabacloud.com/" }
    @{ Name = "MiniMax";               Env = "MINIMAX_API_KEY";            Tier = "PAGO";       Url = "https://platform.minimaxi.com/" }
    @{ Name = "Hyper (Charm)";         Env = "HYPER_API_KEY";              Tier = "GRATIS+PAGO"; Url = "https://hyper.charm.land/" }
    @{ Name = "Vercel AI Gateway";     Env = "VERCEL_API_KEY";             Tier = "GRATIS+PAGO"; Url = "https://vercel.com/" }
    @{ Name = "io.net";                Env = "IONET_API_KEY";              Tier = "PAGO";       Url = "https://io.net/" }
    @{ Name = "OpenCode Zen & Go";     Env = "OPENCODE_API_KEY";           Tier = "PAGO";       Url = "https://opencode.ai/" }
)
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

# ─── 2. Verificar Python no sistema ou baixar portatil ──────────────────────

$systemPython = $null
foreach ($cmd in @("python.exe", "python3.exe", "python")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) { $systemPython = $found.Source; break }
}

if ($systemPython) {
    $PythonExe = $systemPython
    Write-Step "Python encontrado no sistema: $PythonExe" Green
} else {
    $cachedExe = "$PythonDir\python.exe"
    if (Test-Path $cachedExe) {
        $PythonExe = $cachedExe
        Write-Step "Python em cache: $PythonExe" Green
    } else {
        Write-Step "Baixando Python $PythonVersion portatil..." Yellow
        New-Item -ItemType Directory -Force -Path $PythonDir | Out-Null

        $pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
        $pythonZip = "$RuntimeDir\python.zip"

        try {
            if (Test-Command "curl.exe") {
                & curl.exe -sL $pythonUrl -o $pythonZip
            } else {
                [System.Net.WebClient]::new().DownloadFile($pythonUrl, $pythonZip)
            }

            Expand-Archive -Path $pythonZip -DestinationPath $PythonDir -Force
            $items = Get-ChildItem -Path $PythonDir
            if ($items.Count -eq 1 -and $items[0].PSIsContainer) {
                $sub = $items[0].FullName
                Get-ChildItem -Path $sub | Move-Item -Destination $PythonDir -Force
                Remove-Item -Recurse -Force $sub
            }
            Remove-Item $pythonZip -Force
        } catch {
            Write-Step "Falha ao baixar Python: $_" Red
            exit 1
        }

        $PythonExe = "$PythonDir\python.exe"
        Write-Step "Python $PythonVersion instalado em $PythonDir" Green
    }
}

# Se for Python portatil, preparar ambiente (site-packages, pip, PATH)
$isPortable = $PythonExe -like "$PythonDir*"

if ($isPortable) {
    $pthFile = "$PythonDir\python._pth"
    if (Test-Path $pthFile) {
        $content = Get-Content $pthFile -Raw
        if ($content -notmatch '(?m)^import site$') {
            $content = $content -replace '(?m)^#import site', 'import site'
            Set-Content -Path $pthFile -Value $content
        }
    }
    Write-Step "Python $PythonVersion instalado" Green

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
}

# ─── 4. Instalar dependencias ─────────────────────────────────────────────────

Write-Step "Instalando dependencias..." Yellow
& $PythonExe -m pip install -r "$InstallDir\requirements.txt" --quiet 2>&1 | Out-Null
Write-Step "Dependencias instaladas" Green

# ─── 5. Configurar credencial da IA ──────────────────────────────────────────

$envFile = "$InstallDir\.env"
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
    Write-Step "Nenhuma chave de API encontrada." Yellow
    Write-Step "Escolha um provedor para sua chave:" White
    Write-Host ""

    Write-Host "  #  PROVEDOR                       CUSTO             CHAVE EM" -ForegroundColor DarkGray
    Write-Host "  ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――" -ForegroundColor DarkGray
    for ($i = 0; $i -lt $Providers.Count; $i++) {
        $p = $Providers[$i]
        switch ($p.Tier) {
            "GRATIS"      { $tag = " [FREE]"; $color = "Green" }
            "GRATIS+PAGO" { $tag = " [BOTH]"; $color = "Yellow" }
            "PAGO"        { $tag = " [PAID]"; $color = "Red" }
        }
        Write-Host ("  {0,-2} {1,-30} {2,-16} {3}" -f "$($i+1).", $p.Name, $tag, $p.Url) -ForegroundColor $color
    }
    Write-Host ""
    Write-Host "  $($Providers.Count + 1). Digitar chave manual (qualquer env)" -ForegroundColor White
    Write-Host ""

    $choice = $null
    do {
        $raw = Read-Host "  Escolha (1..$($Providers.Count + 1))"
        $parsed = 0
        if ([int]::TryParse($raw, [ref]$parsed)) { $choice = $parsed }
    } while ($null -eq $choice -or $choice -lt 1 -or $choice -gt $Providers.Count + 1)

    if ($choice -eq $Providers.Count + 1) {
        $envName = Read-Host "  Nome da variavel de ambiente (ex: GEMINI_API_KEY)"
        $envValue = Read-Host "  Valor da chave"
    } else {
        $selected = $Providers[$choice - 1]
        $envName = $selected.Env
        if ($envName -eq "AZURE_OPENAI_API_KEY") {
            $envValue = Read-Host "  Informe a chave Azure OpenAI"
            $endpoint = Read-Host "  Informe o endpoint (ex: https://xxx.openai.azure.com)"
            $apiVersion = Read-Host "  Informe a versao da API (ex: 2024-02-15-preview)"
            Add-Content -Path $envFile -Value "AZURE_OPENAI_API_ENDPOINT=$endpoint"
            Add-Content -Path $envFile -Value "AZURE_OPENAI_API_VERSION=$apiVersion"
        } elseif ($envName -eq "AWS_ACCESS_KEY_ID") {
            $envValue = Read-Host "  Informe sua AWS Access Key ID"
            $secret = Read-Host "  Informe sua AWS Secret Access Key"
            $region = Read-Host "  Informe a regiao (ex: us-east-1)"
            Add-Content -Path $envFile -Value "AWS_SECRET_ACCESS_KEY=$secret"
            Add-Content -Path $envFile -Value "AWS_REGION=$region"
        } elseif ($envName -eq "VERTEXAI_PROJECT") {
            $envValue = Read-Host "  Informe o ID do projeto Google Cloud"
            $location = Read-Host "  Informe a localizacao (ex: us-central1)"
            Add-Content -Path $envFile -Value "VERTEXAI_LOCATION=$location"
        } else {
            $envValue = Read-Host "  Informe sua chave $($selected.Name)"
        }
    }

    if ($envName -and $envValue) {
        Set-Content -Path $envFile -Value "$envName=$envValue" -Encoding ASCII
        Write-Step "Credencial salva em .env" Green
    }
} else {
    Write-Step ".env ja configurado" Green
}

# ─── 6. Criar atalhos ─────────────────────────────────────────────────────────

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

# Start Menu shortcut (user-level, sem precisar de admin)
try {
    $startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Custo Certo AI"
    New-Item -ItemType Directory -Force -Path $startMenu | Out-Null
    $link2 = $shell.CreateShortcut("$startMenu\Custo Certo AI.lnk")
    $link2.TargetPath = "powershell.exe"
    $link2.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$InstallDir\run.ps1`""
    $link2.WorkingDirectory = $InstallDir
    $link2.Description = "Custo Certo AI - Analise de Custos Industriais"
    $link2.Save()
    Write-Step "Atalho criado no Menu Iniciar" Green
} catch {
    Write-Step "AVISO: Nao foi possivel criar atalho no Menu Iniciar (sem permissao)" Yellow
}

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
