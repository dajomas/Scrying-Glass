$ErrorActionPreference = 'Stop'

# Run from the directory containing this script.
Set-Location -LiteralPath $PSScriptRoot

$VDir = Join-Path $env:USERPROFILE 'dnd'
$VenvPython = Join-Path $VDir 'Scripts\python.exe'
$VenvActivate = Join-Path $VDir 'Scripts\activate.bat'

try {
    if (
        -not (Test-Path -LiteralPath $VenvPython -PathType Leaf) -or
        -not (Test-Path -LiteralPath $VenvActivate -PathType Leaf)
    ) {
        # Prefer the Python launcher; fall back to python on PATH.
        $PythonCommand = $null
        $PythonArguments = @()

        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3.14 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else 1)" 2>$null

            if ($LASTEXITCODE -eq 0) {
                $PythonCommand = 'py'
                $PythonArguments = @('-3.14')
            }
        }

        if (-not $PythonCommand) {
            if (Get-Command python -ErrorAction SilentlyContinue) {
                & python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else 1)" 2>$null

                if ($LASTEXITCODE -eq 0) {
                    $PythonCommand = 'python'
                }
            }
        }

        if (-not $PythonCommand) {
            throw 'Python 3.14 was not found. Make it available through py -3.14 or python on PATH.'
        }

        & $PythonCommand @PythonArguments -m venv $VDir
        if ($LASTEXITCODE -ne 0) {
            throw "Virtual environment creation failed (exit code $LASTEXITCODE)."
        }
    }

    & $VenvPython -c "import sqlite3; print('SQLite:', sqlite3.sqlite_version)"
    if ($LASTEXITCODE -ne 0) {
        throw 'Python lacks working sqlite3 support; repair Python, not pip dependencies.'
    }

    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "pip upgrade failed (exit code $LASTEXITCODE)."
    }

    $Dependencies = @(
        'fastapi>=0.115'
        'uvicorn[standard]>=0.30'
        'PyYAML>=6.0'
        'python-multipart'
    )

    & $VenvPython -m pip install @Dependencies
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed (exit code $LASTEXITCODE)."
    }

    & $VenvPython scrying_glass_server.py --config config.yaml
    exit $LASTEXITCODE
}
catch {
    [Console]::Error.WriteLine("ERROR: $($_.Exception.Message)")
    exit 1
}
