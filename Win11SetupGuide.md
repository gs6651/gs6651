# Windows 11 Setup Guide

> - STOP MAKING PERFECT LINUX DISTRO, BECAUSE THERE ISN'T ANY.
> - STOP FALLING FOR FIREFOX, CHROME IS MUCH BETTER BOTH ON WINDOWS AND PIXEL PHONE. GOOGLE ANYWAYS KNOWS EVERYTHING ABOUT EVERYONE, THERE IS NO SUCH WAY TO PROTECT YOUR PRIVACY
> - WINDOWS WORKS ALL THE TIME, YES IT NAGS A BIT TIME TO TIME, BUT USE BELOW GUIDE TO GET THE CONTROL

## 1. Initial System Cleanup
Run this command in an Administrator PowerShell to allow your local sync scripts to run:

`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 2. The Lean Software Stack (via winget)
These commands install only the core engines and ad-free tools, specifically using MinGit instead of the full Git package to avoid Start Menu clutter.

- Google Chrome: `winget install -e --id Google.Chrome`
- PowerShell 7: `winget install -e --id Microsoft.PowerShell`
- MinGit: `winget install -e --id Git.MinGit`
- VS Code: `winget install -e --id Microsoft.VisualStudioCode`
- SumatraPDF: `winget install -e --id SumatraPDF.SumatraPDF`
- TuxGuitar: `winget install -e --id TuxGuitar.TuxGuitar`
- Audacity: `winget install -e --id Muse.Audacity`
- VLC Media Player (Optional): `winget install -e --id VideoLAN.VLC`

## 3. Git Setup

Run these two commands to set your identity for your 5 repositories:
- GitRoot: `C:\Users\Gaurav\Documents\GitLocal`
```shell
git config --global user.name "Gaurav Saini"
git config --global user.email "gauravsaini88@gmail.com"
```

- Repository Management: `New-Item -ItemType Directory -Force -Path "C:\Users\Gaurav\Documents\GitLocal"`
- SSH Authentication: `ssh-keygen -t ed25519 -C "gauravsaini88@gmail.com"`
- Copy Public Key to GitHub: `cat ~/.ssh/id_ed25519.pub`
- GitHub Settings > SSH and GPG keys > New SSH Key, paste your key
- Shallow clone
```shell
cd "C:\Users\Gaurav\Documents\GitLocal"
git clone --depth 1 git@github.com:gs6651/gs6651.git
git clone --depth 1 git@github.com:gs6651/Packet-Foundry.git
git clone --depth 1 git@github.com:gs6651/The-Inkwell.git
git clone --depth 1 git@github.com:gs6651/Six-String-Sanctuary.git
git clone --depth 1 git@github.com:gs6651/Terminal-Center.git
```
### Required Files

1. Microsoft.PowerShell_profile.ps1

- Save it here: `C:\Users\Gaurav\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`
<details>
<summary>Microsoft.PowerShell_profile.ps1</summary>

```shell
# 1. Shorten PowerShell Path
function prompt {
    "PS $($ExecutionContext.SessionState.Path.CurrentLocation.Drive.Name):\$((Get-Item $pwd).Name)> "
}

# 2. Root Path
$script:GitRoot = "C:\Users\Gaurav\Documents\GitLocal"

# 3. Load the separate script file from the PowerShell folder
. "$HOME\Documents\PowerShell\gitsync.ps1"
```
</details>

\
2. gitsync.ps1
- Save it here: `C:\Users\Gaurav\Documents\PowerShell\gitsync.ps1`

<details>
<summary>gitsync.ps1</summary>

```shell

# Root folder to auto-discover repos (edit if needed)
$script:GitRoot = "C:\Users\Gaurav\Documents\GitLocal"

# Optional helper: only define Say if you don't already have one
if (-not (Get-Command Say -ErrorAction SilentlyContinue)) {
  function Say {
    param(
      [Parameter(Mandatory)][string]$Message,
      [ValidateSet('Black','DarkBlue','DarkGreen','DarkCyan','DarkRed','DarkMagenta','DarkYellow','Gray','DarkGray','Blue','Green','Cyan','Red','Magenta','Yellow','White')]
      [string]$Color = 'Gray',
      [switch]$Bold
    )
    $isPwsh7 = ($PSVersionTable.PSVersion.Major -ge 7)
    if ($isPwsh7 -and $Bold) {
      $PSStyle.OutputRendering = 'Ansi'
      Write-Host ($PSStyle.Bold + $Message + $PSStyle.Reset) -ForegroundColor $Color
    } else {
      Write-Host $Message -ForegroundColor $Color
    }
  }
}

# Auto-discover repos under $script:GitRoot (direct children by default; optionally recurse)
function Initialize-GitRepos {
  param(
    [string]$Root = $script:GitRoot,
    [switch]$Recurse
  )
  if (-not (Test-Path -LiteralPath $Root)) {
    Say "❌ Root path not found: $Root" "DarkRed" -Bold
    $script:ReposMap = $null
    return
  }
  $dirs = if ($Recurse) {
    Get-ChildItem -LiteralPath $Root -Directory -Recurse -ErrorAction SilentlyContinue
  } else {
    Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue
  }

  $script:ReposMap = [ordered]@{}
  $dirs | Where-Object { Test-Path (Join-Path $_.FullName ".git") } |
    Sort-Object Name | ForEach-Object {
      # Key = folder name; Value = full path
      $script:ReposMap[$_.Name] = $_.FullName
    }
}

function gitsync {
  [CmdletBinding()]
  param(
    # Pass names to sync a subset (e.g., gitsync Terminal-Center)
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Targets,

    # Conflict handling preference
    [ValidateSet('Manual','Theirs','Ours')]
    [string]$Resolve = 'Manual',

    # Pull with autostash unless disabled
    [switch]$NoAutoStash,

    # Concise output (one-line per repo + errors only)
    [switch]$Quiet,

    # Turn off emojis if needed
    [switch]$NoEmoji,

    # Look for repos in all nested folders
    [switch]$Recurse
  )

  # Discover repos each run so the list is always current
  Initialize-GitRepos -Recurse:$Recurse
  if (-not $script:ReposMap -or $script:ReposMap.Count -eq 0) {
    Say "❌ No Git repositories found under: $script:GitRoot" "DarkRed" -Bold
    return
  }

  $date      = Get-Date -Format 'yyyy-MM-dd'
  $commitMsg = "$date Windows-Personal-Laptop"

  # Emojis and icons (funky + dark-theme friendly)
  $E = @{
    repo="📦"; sync="🔄"; fetch="📥"; pull="🧲"; rebase="🔁"; stage="➕"; commit="📝"; push="🚀";
    ok="✅"; fail="❌"; warn="⚠️"; skip="⏭️"; up="✨"; none=""; dot="•"
  }
  if ($NoEmoji) { $E.Keys | ForEach-Object { $E[$_] = "" } }

  # Styles (bold red on PS 7+; safe fallback on 5.1)
  $IsPwsh7 = ($PSVersionTable.PSVersion.Major -ge 7)
  if ($IsPwsh7) { $PSStyle.OutputRendering = 'Ansi' }
  $S = if ($IsPwsh7) {
    [pscustomobject]@{
      Reset = $PSStyle.Reset
      Repo  = $PSStyle.Foreground.Cyan
      Ok    = $PSStyle.Foreground.Green
      Err   = $PSStyle.Bold + $PSStyle.Foreground.Red
      Dim   = $PSStyle.Foreground.BrightBlack
    }
  } else {
    [pscustomobject]@{ Reset=""; Repo=""; Ok=""; Err=""; Dim="" }
  }

  # Determine targets from auto-discovered map
  $selected = if ($Targets -and $Targets.Count -gt 0) {
    $Targets | ForEach-Object { if ($script:ReposMap.ContainsKey($_)) { $script:ReposMap[$_] } else { $_ } }
  } else { $script:ReposMap.Values }

  foreach ($repo in $selected) {
    if (-not (Test-Path $repo))  { Say "$($E.warn) Skip: $repo (not found)" "Yellow" -Bold; continue }
    if (-not (Test-Path (Join-Path $repo '.git'))) { Say "$($E.warn) Skip: $repo is not a Git repo" "Yellow" -Bold; continue }

    Push-Location $repo
    try {
      git config core.longpaths true   # avoid Windows path-length issues

      $name   = Split-Path -Leaf $repo
      $branch = (git rev-parse --abbrev-ref HEAD).Trim()

      if (-not $Quiet) { Say "$($E.sync) [$name] Syncing '$branch'..." "Cyan" -Bold }

      # -------- Fetch (quiet when -Quiet) --------
      if (-not $Quiet) { Say "  $($E.fetch) Fetching..." "Gray" }
      $fetchOut = if ($Quiet) { git fetch --all --prune --quiet 2>&1 } else { git fetch --all --prune 2>&1 }
      $fetchOk  = ($LASTEXITCODE -eq 0)
      if (-not $fetchOk) {
        if (-not $Quiet) { Say "$($E.fail) [$name] Fetch failed." "DarkRed" -Bold }
        # Quiet summary will reflect failure
      }

      # -------- Pull (rebase) --------
      $before = (git rev-parse HEAD).Trim()
      if (-not $Quiet) { Say "  $($E.pull)$($E.rebase) Pull (rebase)..." "Gray" }
      $pullOut = if (-not $fetchOk) {
        ""  # skip pull if fetch failed
      } else {
        if ($NoAutoStash) {
          if ($Quiet) { git pull --rebase origin $branch --quiet 2>&1 } else { git pull --rebase origin $branch 2>&1 }
        } else {
          if ($Quiet) { git pull --rebase --autostash origin $branch --quiet 2>&1 } else { git pull --rebase --autostash origin $branch 2>&1 }
        }
      }

      if (-not $fetchOk) {
        $pullOk = $false
      } else {
        # Optional conflict auto-resolve
        if ($LASTEXITCODE -ne 0 -and $Resolve -ne 'Manual') {
          if     ($Resolve -eq 'Theirs') { git checkout --theirs -- . }
          elseif ($Resolve -eq 'Ours')   { git checkout --ours  -- . }
          git add -A
          git rebase --continue
        }
        $pullOk = ($LASTEXITCODE -eq 0)
        if (-not $pullOk -and -not $Quiet) { Say "$($E.fail) [$name] Pull/rebase needs attention." "DarkRed" -Bold }
      }

      $after     = (git rev-parse HEAD).Trim()
      $upToDate  = ($before -eq $after)
      $committed = $false
      $pushed    = $false

      if (-not $Quiet -and $pullOk -and $upToDate) {
        Say "  $($E.up) Already up to date." "Blue" -Bold
      }

      # -------- Stage & commit (quiet when -Quiet) --------
      if (-not $Quiet) { Say "  $($E.stage) Staging changes..." "Gray" }
      git add -A
      git diff --cached --quiet
      if ($LASTEXITCODE -ne 0) {
        if (-not $Quiet) { Say "  $($E.commit) Commit..." "Gray" }
        $commitOut = if ($Quiet) { git commit -m $commitMsg --quiet 2>&1 } else { git commit -m $commitMsg 2>&1 }
        if ($LASTEXITCODE -eq 0) {
          $committed = $true
          if (-not $Quiet) { Say "$($E.ok) [$name] Committed: $commitMsg" "Green" -Bold }
        } else {
          if (-not $Quiet) { Say "$($E.fail) [$name] Commit failed." "DarkRed" -Bold }
        }
      } else {
        if (-not $Quiet) { Say "  $($E.dot) No changes to commit." "Gray" }
      }

      # -------- Push (quiet when -Quiet) --------
      if (-not $Quiet) { Say "  $($E.push) Push..." "Gray" }
      if ($pullOk) {
        git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Out-Null
        $pushOut = if ($LASTEXITCODE -ne 0) {
          if ($Quiet) { git push -u origin $branch --quiet 2>&1 } else { git push -u origin $branch 2>&1 }
        } else {
          if ($Quiet) { git push --quiet 2>&1 } else { git push 2>&1 }
        }
        if ($LASTEXITCODE -eq 0) {
          $pushed = $true
          if (-not $Quiet) { Say "$($E.ok) [$name] Push successful." "Green" -Bold }
        } else {
          if (-not $Quiet) { Say "$($E.fail) [$name] Push failed." "DarkRed" -Bold }
        }
      } else {
        $pushOut = ""
        $pushed = $false
      }

      # -------- Compact one-line summary when -Quiet --------
      if ($Quiet) {
        $pullMark  = if ($pullOk) { "$($S.Ok)$($E.ok)$($S.Reset)" } else { "$($S.Err)$($E.fail)$($S.Reset)" }
        $pushMark  = if ($pushed) { "$($S.Ok)$($E.ok)$($S.Reset)" } else { if ($pullOk) { "$($S.Err)$($E.fail)$($S.Reset)" } else { "$($S.Dim)–$($S.Reset)" } }
        $commitTag = if ($committed) { " | $($E.commit) Commit: $($S.Ok)$($E.ok)$($S.Reset)" } else { "" }

        # 📦 Repo | 🧲 Pull: ✅ | 🚀 Push: ✅ (| 📝 Commit: ✅)
        Write-Host ("{0} {1}{2}{3}{4}{5}{6}{7}" -f `
          $E.repo, $S.Repo, $name, $S.Reset,
          " | $($E.pull) Pull: ", $pullMark,
          " | $($E.push) Push: ", $pushMark
        ) -NoNewline
        if ($commitTag) { Write-Host $commitTag -NoNewline }
        Write-Host

        # Only print details if something failed (first line only, bold red)
        if (-not $fetchOk) {
          $first = ($fetchOut | Out-String).Trim().Split("`r`n","`n") | Select-Object -First 1
          if ($first) { Write-Host "$($S.Err)$($E.fail) Fetch error: $first$($S.Reset)" }
        } elseif (-not $pullOk) {
          $first = ($pullOut | Out-String).Trim().Split("`r`n","`n") | Select-Object -First 1
          if ($first) { Write-Host "$($S.Err)$($E.fail) Pull error: $first$($S.Reset)" }
        } elseif (-not $pushed) {
          $first = ($pushOut | Out-String).Trim().Split("`r`n","`n") | Select-Object -First 1
          if ($first) { Write-Host "$($S.Err)$($E.fail) Push error: $first$($S.Reset)" }
        }
      }
    }
    finally { Pop-Location }
  }
}

# Wrapper: always-minimal view (use this as your default command)
function gs {
  [CmdletBinding()]
  param([Parameter(ValueFromRemainingArguments = $true)][object[]]$Args)
  Update-BookCount
  gitsync -Quiet @Args
}


# Short alias
Set-Alias gs gitsync

```
</details>

## Encrypted DNS

1. Enable Encrypted DNS
- Open Settings (Win + I).
- Go to Network & internet > Wi-Fi (or Ethernet).
- Click on Hardware properties.
- Find DNS server assignment and click Edit.
- Change the dropdown from "Automatic (DHCP)" to Manual.
- Turn ON the IPv4 toggle.
- Enter a trusted DNS provider (I recommend Cloudflare for speed or Quad9 for security):
- Preferred DNS: `1.1.1.1` (Cloudflare) or `9.9.9.9` (Quad9)
- Preferred DNS encryption: Select Encrypted only (DNS over HTTPS).
- Do the same for Alternate DNS (e.g., `1.0.0.1` for Cloudflare).
- Click Save.

2. Verify it's working

`Resolve-DnsName -Type txt proto.on.quad9.net`

- Result should be `doh`
- or go to [website](https://one.one.one.one/help/) and check "Using DNS over HTTPS (DoH)" should be `YES`

## Other Essential Tweaks

**1. Disable the "Advertising ID" and Tracking**

- Go to Settings > Privacy & security > General.
- Turn OFF all 4 toggles (Personalized ads, local content, app launch tracking, and suggested content in Settings).

**2. Kill the "Tailored Experiences"**

- Go to Settings > Privacy & security > Diagnostics & feedback.
- Expand Tailored experiences and turn it OFF.
- Change Feedback frequency to Never.

**3. Clean up the Start Menu "Recommendations"**

- Go to Settings > Personalization > Start.
- Turn OFF: "Show recently added apps," "Show recently opened items," and "Show recommendations for tips, shortcuts, etc."

**4. Silence Taskbar "Widgets" (News & Weather)**

- Go to Settings > Personalization > Taskbar.
- Toggle OFF: Widgets and Search (if you prefer just the icon or hidden).

**5. Background Apps Permission**

- Go to Settings > Apps > Installed apps.
- For any app you don't use often (like Mail, Weather, or Calculator), click the three dots (...) > Advanced options.
- Change Background apps permissions to Never

**6. Start Menu "All Apps" Clean-up (Run as admin)**

- To Disable:
`reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoStartMenuMorePrograms /t REG_DWORD /d 1 /f && taskkill /f /im explorer.exe && start explorer.exe`
- To Enable:
`reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoStartMenuMorePrograms /t REG_DWORD /d 0 /f && taskkill /f /im explorer.exe && start explorer.exe`

## Guitar Journey
**Phase1**
- Pixel8
- Audacity

**Phase2**
- Scarlett 2i2 (4th Gen)
- Lewitt LCT 140 Air
- Pro Tools
- 3m XLR Cable & Boom Mic Stand

**Phase3**
- Yamaha Pacifica Standard Plus
- Pro Tools
- *Amp Sims*
  - Neural Amp Modeler (NAM) – The "Holy Grail" of Free Gear
  - AmpliTube 5 Custom Shop – The All-in-One Studio
  - Guitar Rig 7 Player – The Best for Creative Rock
  - Blue Cat's Free Amp – The "Leanest" Choice

**Phase4**
- Sky is the limit

