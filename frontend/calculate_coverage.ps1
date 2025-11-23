# Calculate comment coverage for TypeScript files
# Formula: (comment_lines / (total_lines - blank_lines)) * 100

function Get-CommentCoverage {
    param(
        [string]$FilePath
    )

    $content = Get-Content $FilePath
    $totalLines = $content.Count
    $blankLines = 0
    $commentLines = 0
    $inBlockComment = $false

    foreach ($line in $content) {
        $trimmed = $line.Trim()

        # Count blank lines
        if ($trimmed -eq "") {
            $blankLines++
            continue
        }

        # Check for block comment start
        if ($trimmed -match "^/\*" -or $inBlockComment) {
            $commentLines++
            $inBlockComment = $true

            # Check for block comment end
            if ($trimmed -match "\*/$") {
                $inBlockComment = $false
            }
            continue
        }

        # Check for single-line comment
        if ($trimmed -match "^//" -or $trimmed -match "^\*") {
            $commentLines++
            continue
        }
    }

    $nonBlankLines = $totalLines - $blankLines
    $coverage = if ($nonBlankLines -gt 0) {
        [math]::Round(($commentLines / $nonBlankLines) * 100, 2)
    } else {
        0
    }

    return @{
        File = Split-Path $FilePath -Leaf
        TotalLines = $totalLines
        BlankLines = $blankLines
        CommentLines = $commentLines
        NonBlankLines = $nonBlankLines
        Coverage = $coverage
    }
}

# Calculate coverage for all files
$files = @(
    "src\lib\stores\projects.ts",
    "src\lib\stores\conversations.ts",
    "src\lib\stores\messages.ts",
    "src\lib\config.ts",
    "vite.config.ts"
)

Write-Host "`n=== Comment Coverage Report ===" -ForegroundColor Cyan
Write-Host ("Required: >= 40%`n") -ForegroundColor Yellow

foreach ($file in $files) {
    $result = Get-CommentCoverage -FilePath $file

    $status = if ($result.Coverage -ge 40) { "PASS" } else { "FAIL" }
    $color = if ($result.Coverage -ge 40) { "Green" } else { "Red" }

    Write-Host ("`n{0}" -f $result.File) -ForegroundColor White
    Write-Host ("  Total Lines:     {0}" -f $result.TotalLines)
    Write-Host ("  Blank Lines:     {0}" -f $result.BlankLines)
    Write-Host ("  Comment Lines:   {0}" -f $result.CommentLines)
    Write-Host ("  Non-Blank Lines: {0}" -f $result.NonBlankLines)
    Write-Host ("  Coverage:        {0}% [{1}]" -f $result.Coverage, $status) -ForegroundColor $color
}

Write-Host "`n=================================`n" -ForegroundColor Cyan
