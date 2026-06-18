# Atalho Windows para os comandos do Makefile (use: .\mm.ps1 lint)
param(
    [Parameter(Position = 0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Invoke-Compose {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Cmd)
    & docker compose @Cmd
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Target) {
    "build" { Invoke-Compose build }
    "up" { Invoke-Compose up }
    "upd" { Invoke-Compose up -d }
    "down" { Invoke-Compose down }
    "shell" { Invoke-Compose exec -T web python manage.py shell }
    "migrate" { Invoke-Compose exec -T web python manage.py migrate }
    "migrations" { Invoke-Compose exec -T web python manage.py makemigrations }
    "createsuperuser" { Invoke-Compose exec -T web python manage.py createsuperuser }
    "test" { Invoke-Compose exec -T web python manage.py test }
    "pytest" { Invoke-Compose exec -T web pytest }
    "lint" {
        Invoke-Compose exec -T web ruff check .
        Invoke-Compose exec -T web black --check .
    }
    "format" {
        Invoke-Compose exec -T web ruff check . --fix
        Invoke-Compose exec -T web black .
    }
    "cov" {
        Invoke-Compose exec -T web pytest --cov=apps --cov=core --cov-report=term-missing
    }
    "logs" { Invoke-Compose logs -f web }
    "logs-celery" { Invoke-Compose logs -f celery }
    default {
        Write-Host @"

MarryMe Backend — comandos (Windows)

  .\mm.ps1 upd          sobe containers
  .\mm.ps1 migrate      aplica migrations
  .\mm.ps1 lint         ruff + black --check
  .\mm.ps1 format       ruff --fix + black
  .\mm.ps1 test         testes Django
  .\mm.ps1 pytest       testes pytest
  .\mm.ps1 cov          cobertura
  .\mm.ps1 down         para containers

No Linux/Mac use: make lint (Makefile)

"@
    }
}
