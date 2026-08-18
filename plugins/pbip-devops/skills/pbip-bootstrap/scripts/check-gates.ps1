<#
.SYNOPSIS
    Автоматична частина гейтів G1/G3 для PBIP-репозиторію — пер-типова матриця.

.DESCRIPTION
    Визначає з git, які типи файлів змінено, і жене лише релевантні гейти:

      завжди          гілка, заборонені файли в індексі, .gitignore
      модель (*.tmdl) TMDL-коментарі + BPA (Tabular Editor 2, scripts/bpa-rules.json)
      звіт (*.Report) валідність JSON, roundtrip і геометрія через pbir.py,
                      нагадування про діагностику закладок при їх зміні
      тема            валідність JSON + нагадування про повне перевідкриття Desktop
      лише docs       важкі перевірки пропускаються (про це сказано явно)

    Чисте дерево = повний аудит (усі гейти).
    Кожен пропуск гейта — гучний (WARN з причиною), ніколи мовчазний.

    Вихідний код: 1 — є провалені перевірки, 0 — ні. Попередження код не змінюють.

.PARAMETER RepoRoot
    Корінь репозиторію. За замовчуванням — поточна тека.

.PARAMETER Quiet
    Показувати лише проблеми, без списку успішних перевірок.

.PARAMETER SkipBpa
    Пропустити BPA-гейт (наприклад, разова правка при відсутньому TE2).
    Пропуск все одно буде показаний як WARN.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/check-gates.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoRoot,
    [switch]$Quiet,
    [switch]$SkipBpa
)

$ErrorActionPreference = 'Continue'
if (-not $RepoRoot) { $RepoRoot = (Get-Location).Path }

$script:Failures = New-Object System.Collections.ArrayList
$script:Warnings = New-Object System.Collections.ArrayList
$script:Passes   = New-Object System.Collections.ArrayList

function Add-Fail { param([string]$m) [void]$script:Failures.Add($m) }
function Add-Warn { param([string]$m) [void]$script:Warnings.Add($m) }
function Add-Pass { param([string]$m) [void]$script:Passes.Add($m) }

# ── 0. Чи це взагалі репозиторій ────────────────────────────────────────────
$null = git -C $RepoRoot rev-parse --is-inside-work-tree
if ($LASTEXITCODE -ne 0) {
    Write-Host "check-gates: '$RepoRoot' не є git-репозиторієм." -ForegroundColor Red
    exit 2
}

$commitCount = 0
$cc = git -C $RepoRoot rev-list --count HEAD 2>$null
if ($LASTEXITCODE -eq 0) { $commitCount = [int]$cc }

# ── 0.1 Що змінено → які типи задач зачеплені ──────────────────────────────
# Об'єднання: незакомічені зміни проти HEAD + нові (untracked) файли.
# core.quotepath=false ОБОВ'ЯЗКОВО: інакше git огортає кириличні шляхи в лапки
# з вісімковим екрануванням ("\320\227...json"), і всі кінець-заякорені регекси
# ($ на розширенні) мовчки перестають матчитись.
$changed = @()
$diffNames = git -C $RepoRoot -c core.quotepath=false diff --name-only HEAD 2>$null
if ($LASTEXITCODE -eq 0 -and $diffNames) { $changed += $diffNames }
$untracked = git -C $RepoRoot -c core.quotepath=false ls-files --others --exclude-standard 2>$null
if ($LASTEXITCODE -eq 0 -and $untracked) { $changed += $untracked }
$changed = @($changed | Where-Object { $_ } | Select-Object -Unique)

$fullAudit = ($changed.Count -eq 0)

$modelTouched  = [bool]($changed | Where-Object { $_ -match '\.tmdl$' -or $_ -match '\.SemanticModel/' })
$reportTouched = [bool]($changed | Where-Object { $_ -match '\.Report/' -or $_ -match 'report\.json$' -or $_ -match '\.pbir$' })
$themeTouched  = [bool]($changed | Where-Object { $_ -match '\.Report/StaticResources/.*\.json$' })
$docsOnly = $false
if (-not $fullAudit) {
    $nonDocs = @($changed | Where-Object { $_ -notmatch '\.(md|txt)$' })
    $docsOnly = ($nonDocs.Count -eq 0)
}

if ($fullAudit) {
    Add-Pass "Дерево чисте — повний аудит (усі гейти)."
    $modelTouched = $true; $reportTouched = $true; $themeTouched = $true
}
elseif ($docsOnly) {
    Add-Pass ("Змінено лише документацію (" + $changed.Count + " файл(ів)) — гейти моделі/звіту не застосовні.")
}
else {
    $kinds = @()
    if ($modelTouched)  { $kinds += 'модель' }
    if ($reportTouched) { $kinds += 'звіт' }
    if ($themeTouched)  { $kinds += 'тема' }
    if ($kinds.Count -eq 0) { $kinds += 'інфраструктура' }
    Add-Pass ("Змінено файлів: " + $changed.Count + "; типи задач: " + ($kinds -join ', ') + ".")
}

# ── 1. ЗАВЖДИ: гілка не інтеграційна ────────────────────────────────────────
# Назву інтеграційної гілки беремо з таблиці §0 у CLAUDE.md, щоб скрипт не
# треба було правити під кожен проєкт.
$integration = 'main'
$claudePath = Join-Path $RepoRoot 'CLAUDE.md'
if (Test-Path $claudePath) {
    $claudeText = Get-Content -Path $claudePath -Raw -Encoding UTF8
    $m = [regex]::Match($claudeText, '(?m)^\|\s*Інтеграційна гілка\s*\|\s*`([^`]+)`')
    if ($m.Success) { $integration = $m.Groups[1].Value.Trim() }
}

$branch = (git -C $RepoRoot branch --show-current)
if ([string]::IsNullOrWhiteSpace($branch)) {
    Add-Warn "Гілку визначити не вдалось (detached HEAD?)."
}
elseif ($branch -eq $integration -or $branch -eq 'prod') {
    if ($commitCount -le 1) {
        Add-Warn "Гілка '$branch' — інтеграційна, але репозиторій ще на bootstrap ($commitCount коміт). Далі — фіча-гілка."
    }
    else {
        Add-Fail "Гілка '$branch' — інтеграційна. Відгалузитись: git checkout -b feature/<опис>"
    }
}
else {
    Add-Pass "Гілка '$branch' — не інтеграційна."
}

# ── 2. ЗАВЖДИ: заборонені файли під версійним контролем ────────────────────
$tracked = git -C $RepoRoot -c core.quotepath=false ls-files
$forbidden = @($tracked | Where-Object {
    $_ -match '\.pbi/localSettings\.json$' -or $_ -match '\.abf$' -or
    $_ -match '\.pbix$' -or $_ -match '\.pbit$'
})
if ($forbidden.Count -gt 0) {
    Add-Fail ("Локальні/бінарні файли потрапили під git: " + ($forbidden -join ', '))
}
else {
    Add-Pass "Локальний стан Desktop і бінарні артефакти не відстежуються."
}

# ── 3. ЗАВЖДИ: .gitignore без інлайн-коментарів ────────────────────────────
# git читає '#' лише на початку рядка; в інших позиціях він стає частиною
# патерну, і правило мовчки перестає діяти.
$giPath = Join-Path $RepoRoot '.gitignore'
if (Test-Path $giPath) {
    $badLines = New-Object System.Collections.ArrayList
    $lineNo = 0
    foreach ($line in (Get-Content -Path $giPath -Encoding UTF8)) {
        $lineNo++
        $t = $line.Trim()
        if ($t.Length -eq 0) { continue }
        if ($t.StartsWith('#')) { continue }
        if ($t -match '\s#') { [void]$badLines.Add("рядок ${lineNo}: $t") }
    }
    if ($badLines.Count -gt 0) {
        Add-Fail (".gitignore має інлайн-коментарі — правила не діють: " + ($badLines -join '; '))
    }
    else {
        Add-Pass ".gitignore без інлайн-коментарів."
    }
}
else {
    Add-Warn ".gitignore відсутній."
}

# ── 4. ЗВІТ: валідність JSON ────────────────────────────────────────────────
# ConvertFrom-Json у PowerShell 5.1 має ліміт ~2 МБ і падає на великому
# report.json, тому валідуємо через python — він однаково потрібен для pbir.py.
$pythonOk = $true
$null = python --version
if ($LASTEXITCODE -ne 0) { $pythonOk = $false }

$reportDirs = @(Get-ChildItem -Path $RepoRoot -Directory -Filter '*.Report' -ErrorAction SilentlyContinue)
if ($reportTouched -and $reportDirs.Count -gt 1) {
    Add-Warn ("У репозиторії кілька тек *.Report — перевірки звіту підуть лише по першій: " + $reportDirs[0].Name)
}
$reportJson = $null
if ($reportDirs.Count -gt 0) {
    $candidate = Join-Path $reportDirs[0].FullName 'report.json'
    if (Test-Path $candidate) { $reportJson = $candidate }
}

if (-not $reportTouched) {
    Add-Pass "Звіт не змінювався — гейти звіту (JSON, roundtrip, геометрія) не застосовні."
}
elseif (-not $pythonOk) {
    Add-Warn "python недоступний — перевірки JSON і геометрії пропущено."
}
elseif ($reportDirs.Count -eq 0) {
    Add-Warn "Теки *.Report немає — перевірки звіту пропущено (проєкт ще не збережено з Desktop?)."
}
else {
    $jsonFiles = @(Get-ChildItem -Path $reportDirs[0].FullName -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { ($_.Extension -in '.json', '.pbir') -and ($_.FullName -notmatch '\\\.pbi\\') })

    $badJson = New-Object System.Collections.ArrayList
    foreach ($f in $jsonFiles) {
        $null = python -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8-sig'))" $f.FullName
        if ($LASTEXITCODE -ne 0) { [void]$badJson.Add($f.Name) }
    }
    if ($badJson.Count -gt 0) {
        Add-Fail ("Невалідний JSON: " + ($badJson -join ', '))
    }
    else {
        Add-Pass ("JSON валідний (" + $jsonFiles.Count + " файлів).")
    }
}

# ── 5. МОДЕЛЬ: блокові коментарі TMDL ──────────────────────────────────────
# TMDL не приймає /* */ — Desktop відмовляється відкрити проєкт. Але всередині
# партицій живе M-код, де /* */ легальні, тому це попередження, а не провал:
# перевірити треба очима, чи знахідка поза partition-блоком.
if ($modelTouched) {
    $tmdlFiles = @(Get-ChildItem -Path $RepoRoot -Recurse -File -Filter '*.tmdl' -ErrorAction SilentlyContinue)
    if ($tmdlFiles.Count -gt 0) {
        $withBlockComment = @($tmdlFiles | Where-Object {
            (Get-Content -Path $_.FullName -Raw -Encoding UTF8) -match '/\*'
        })
        if ($withBlockComment.Count -gt 0) {
            Add-Warn ("Знайдено '/*' у TMDL — легально лише всередині M-партицій, перевірити: " +
                      (($withBlockComment | ForEach-Object { $_.Name }) -join ', '))
        }
        else {
            Add-Pass ("TMDL без блокових коментарів (" + $tmdlFiles.Count + " файлів).")
        }
    }
}

# ── 6. МОДЕЛЬ: BPA через Tabular Editor 2 ──────────────────────────────────
# Правила: спершу scripts/bpa-rules.json репозиторію (проєктний тюнінг),
# інакше глобальний %LocalAppData%\TabularEditor\BPARules.json.
# Exit code TE2: 1 лише при порушеннях Severity >= 3 (або фатальній помилці);
# -G дає розмітку ::error:: (Sev3) / ::warning:: (Sev2) для підрахунку.
if (-not $modelTouched) {
    Add-Pass "Модель не змінювалась — BPA не застосовний."
}
elseif ($SkipBpa) {
    Add-Warn "BPA пропущено на вимогу (-SkipBpa)."
}
else {
    $te = $env:TE_PATH
    if (-not $te -or -not (Test-Path $te)) { $te = 'C:\Program Files (x86)\Tabular Editor\TabularEditor.exe' }
    if (-not (Test-Path $te)) { $te = 'C:\Program Files\Tabular Editor\TabularEditor.exe' }

    $rules = Join-Path $RepoRoot 'scripts\bpa-rules.json'
    if (-not (Test-Path $rules)) { $rules = Join-Path $env:LOCALAPPDATA 'TabularEditor\BPARules.json' }

    $modelDirs = @(Get-ChildItem -Path $RepoRoot -Directory -Filter '*.SemanticModel' -ErrorAction SilentlyContinue)
    if ($modelDirs.Count -gt 1) {
        Add-Warn ("У репозиторії кілька тек *.SemanticModel — BPA піде лише по першій: " + $modelDirs[0].Name)
    }
    $modelDef = $null
    if ($modelDirs.Count -gt 0) {
        $candidate = Join-Path $modelDirs[0].FullName 'definition'
        if (Test-Path (Join-Path $candidate 'database.tmdl')) { $modelDef = $candidate }
        elseif (Test-Path (Join-Path $modelDirs[0].FullName 'model.bim')) { $modelDef = Join-Path $modelDirs[0].FullName 'model.bim' }
    }

    # Зіпсований rules-файл TE2 мовчки трактує як «0 правил» і повертає exit 0 —
    # зелений гейт при непрацюючих правилах. Тому JSON правил валідуємо самі.
    $rulesValid = $true
    if ((Test-Path $rules) -and $pythonOk) {
        $null = python -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8-sig'))" $rules 2>$null
        if ($LASTEXITCODE -ne 0) { $rulesValid = $false }
    }

    if (-not (Test-Path $te)) {
        Add-Warn "BPA пропущено: TabularEditor.exe не знайдено (встанови Tabular Editor 2 або задай `$env:TE_PATH)."
    }
    elseif (-not (Test-Path $rules)) {
        Add-Warn "BPA пропущено: файл правил не знайдено (очікується scripts/bpa-rules.json або %LocalAppData%\TabularEditor\BPARules.json)."
    }
    elseif (-not $rulesValid) {
        Add-Fail ("BPA: файл правил '" + $rules + "' — невалідний JSON. TE2 мовчки проігнорує його і дасть хибно-зелений результат; полагодити файл до коміта.")
    }
    elseif (-not $modelDef) {
        Add-Warn "BPA пропущено: теки *.SemanticModel\definition (чи model.bim) немає — модель ще не збережена з Desktop?"
    }
    else {
        $bpaOut = Join-Path $env:TEMP 'check-gates-bpa.txt'
        # TabularEditor.exe — WinForms: без cmd-редиректу керування повертається одразу,
        # і $LASTEXITCODE стає недостовірним. cmd /c з '>' чекає завершення.
        cmd /c "`"$te`" `"$modelDef`" -A `"$rules`" -G > `"$bpaOut`" 2>&1"
        $bpaExit = $LASTEXITCODE
        $bpaLines = @()
        if (Test-Path $bpaOut) { $bpaLines = @(Get-Content -Path $bpaOut -Encoding UTF8) }

        $loadError = [bool]($bpaLines | Where-Object { $_ -match 'Error loading file|File not found' })
        $sev3 = @($bpaLines | Where-Object { $_ -match '^::error::' })
        $sev2 = @($bpaLines | Where-Object { $_ -match '^::warning::' })

        if ($loadError) {
            Add-Fail ("BPA: TE2 не зміг завантажити модель '" + $modelDef + "' — див. " + $bpaOut)
        }
        elseif ($bpaExit -ne 0 -and $sev3.Count -eq 0) {
            Add-Fail ("BPA: TE2 завершився з кодом " + $bpaExit + " без розпізнаних анотацій порушень — ймовірно збій самого TE2, див. " + $bpaOut)
        }
        elseif ($bpaExit -ne 0) {
            $top = ($sev3 | Select-Object -First 5 | ForEach-Object { $_ -replace '^::error::\s*', '' }) -join '; '
            Add-Fail ("BPA: " + $sev3.Count + " порушень Severity 3 (блокують коміт). Перші: " + $top +
                      " | Повний лог: " + $bpaOut)
        }
        else {
            if ($sev2.Count -gt 0) {
                Add-Warn ("BPA: Severity 3 — чисто; попереджень Severity 2: " + $sev2.Count + " (див. " + $bpaOut + ").")
            }
            else {
                Add-Pass "BPA: жодного порушення Severity 2–3."
            }
        }
    }
}

# ── 6.1 МОДЕЛЬ: биті посилання на таблиці в DAX ────────────────────────────
# Клас дефектів, який пропускають і BPA, і JSON-валідність: міра посилається
# на таблицю, якої немає в моделі (реальні прецеденти: 'Автотести витрати',
# 'AccessControl'). TOM це терпить, візуал падає лише в рантаймі.
if ($modelTouched -and $pythonOk) {
    $refsScript = Join-Path $PSScriptRoot 'check-model-refs.py'
    $modelDirs2 = @(Get-ChildItem -Path $RepoRoot -Directory -Filter '*.SemanticModel' -ErrorAction SilentlyContinue)
    if ((Test-Path $refsScript) -and $modelDirs2.Count -gt 0) {
        $defDir = Join-Path $modelDirs2[0].FullName 'definition'
        if (Test-Path (Join-Path $defDir 'tables')) {
            $refsOut = python $refsScript $defDir 2>$null
            $refsExit = $LASTEXITCODE
            if ($refsExit -eq 0) {
                Add-Pass "Посилання DAX→таблиці: усі квотовані посилання валідні."
            }
            elseif ($refsExit -eq 1) {
                $lines = @($refsOut | Where-Object { $_ -match ':\d+' } | Select-Object -First 5)
                Add-Fail ("Биті посилання на неіснуючі таблиці в DAX: " + ($lines -join '; '))
            }
            else {
                Add-Warn "check-model-refs.py не зміг проаналізувати модель (код $refsExit)."
            }
        }
    }
    elseif (-not (Test-Path $refsScript)) {
        Add-Warn "check-model-refs.py не знайдено поруч зі скриптом гейтів — перевірку посилань пропущено."
    }
}

# ── 7. ЗВІТ: pbir.py — roundtrip і геометрія (лише PBIR-Legacy) ────────────
$pbir = Join-Path $env:USERPROFILE '.claude\skills\powerbi-bookmarks\pbir.py'
if (-not $reportTouched) {
    # Гейт уже позначений «не застосовний» у секції 4 — тут мовчимо, щоб не дублювати.
}
elseif ($pythonOk -and $reportJson -and (Test-Path $pbir)) {
    $out = python $pbir $reportJson
    $text = ($out -join "`n")

    $rt = [regex]::Match($text, 'roundtrip:\s*(\w+)')
    if ($rt.Success -and $rt.Groups[1].Value -eq 'True') {
        Add-Pass "report.json: byte-identical roundtrip."
    }
    else {
        Add-Fail "report.json: roundtrip не byte-identical — правки зроблені не через pbir.py."
    }

    $gm = [regex]::Match($text, 'geometry mismatches[^:]*:\s*(\d+)')
    if ($gm.Success) {
        if ([int]$gm.Groups[1].Value -eq 0) {
            Add-Pass "Геометрія: дзеркало і layouts[0].position збігаються."
        }
        else {
            Add-Fail ("Геометрія: " + $gm.Groups[1].Value +
                      " розбіжностей між vc['x'] і config.layouts[0].position — Desktop рендерить з config.")
        }
    }
}
elseif ($reportJson -and -not (Test-Path $pbir)) {
    Add-Warn "pbir.py не знайдено — перевірку roundtrip і геометрії пропущено."
}
elseif ($reportDirs.Count -gt 0 -and -not $reportJson) {
    # Пропуск має бути гучним: інакше кількість пройдених перевірок мовчки падає,
    # і це читається як «усе гаразд», хоча дві перевірки просто не виконались.
    Add-Pass "PBIR enhanced (немає report.json) — roundtrip і подвійна геометрія не застосовні; позиція живе в visual.json у єдиному екземплярі."
}

# ── 8. ЗВІТ: закладки зачеплені → нагадування про діагностику ──────────────
# Грепати сирий дифф не можна: у Legacy report.json увесь config — один рядок
# ~1.8 млн символів, де зміна самого лише activeSectionIndex (перезаписується
# майже кожним Desktop-save) переписує ту саму лінію, що містить "bookmarks".
# Тому порівнюємо КОНКРЕТНО масив bookmarks: HEAD vs робоча копія.
if ($reportTouched -and $reportJson -and -not $fullAudit -and $pythonOk) {
    # git-pathspec приймаємо лише з прямими слешами: зворотні на Windows git
    # трактує як екранування, і 'git show' мовчки не знаходить файл.
    $reportRel = $reportJson.Substring($RepoRoot.Length).TrimStart('\','/').Replace('\','/')
    $bmPy = Join-Path $env:TEMP 'check-gates-bookmarks.py'
    @'
import json, subprocess, sys
rel, root, path = sys.argv[1], sys.argv[2], sys.argv[3]
def bookmarks(txt):
    cfg = json.loads(json.loads(txt)["config"])
    return json.dumps(cfg.get("bookmarks"), sort_keys=True, ensure_ascii=False)
try:
    old_raw = subprocess.run(["git", "-C", root, "show", "HEAD:" + rel],
                             capture_output=True, check=True).stdout.decode("utf-8-sig", errors="replace")
    with open(path, encoding="utf-8-sig") as f:
        new_raw = f.read()
    print("CHANGED" if bookmarks(old_raw) != bookmarks(new_raw) else "SAME")
except Exception:
    print("UNKNOWN")
'@ | Out-File -FilePath $bmPy -Encoding utf8
    $bmResult = (python $bmPy $reportRel $RepoRoot $reportJson | Select-Object -Last 1)
    if ($bmResult -eq 'CHANGED') {
        Add-Warn "Масив bookmarks у report.json змінився проти HEAD — прогнати діагностику powerbi-bookmarks по всіх зачеплених id (симетрія сестринських закладок, скоуп targetVisualNames, G1)."
    }
    elseif ($bmResult -eq 'UNKNOWN') {
        Add-Warn "Не вдалося порівняти закладки report.json (HEAD vs робоча копія — новий файл або нечитабельний config) — якщо правили закладки/видимість, діагностика powerbi-bookmarks вручну."
    }
}

# ── 9. ТЕМА: повне перевідкриття Desktop ───────────────────────────────────
if ($themeTouched -and -not $fullAudit) {
    Add-Warn "Змінено файли теми (StaticResources) — зміна теми потребує ПОВНОГО перевідкриття Desktop; bridge-reload її не підхопить."
}

# ── Підсумок ────────────────────────────────────────────────────────────────
Write-Host ""
if (-not $Quiet) {
    foreach ($p in $script:Passes) { Write-Host "  OK   $p" -ForegroundColor Green }
}
foreach ($w in $script:Warnings) { Write-Host "  WARN $w" -ForegroundColor Yellow }
foreach ($f in $script:Failures) { Write-Host "  FAIL $f" -ForegroundColor Red }

Write-Host ""
$summary = "Гейти: {0} пройдено, {1} попереджень, {2} провалено." -f `
    $script:Passes.Count, $script:Warnings.Count, $script:Failures.Count

if ($script:Failures.Count -gt 0) {
    Write-Host $summary -ForegroundColor Red
    exit 1
}
Write-Host $summary -ForegroundColor Green
exit 0
