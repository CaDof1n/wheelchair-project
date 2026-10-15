<#
.SYNOPSIS
  Export a .docx or .pptx to PDF with the locally installed Microsoft Office.

.DESCRIPTION
  Render step of the self-check list, section 3 (docs/interfaces). Needs Word
  (for .docx) or PowerPoint (for .pptx) on Windows. The source file is opened
  read-only and never modified. Check the resulting PDF with
  tools/check_render_pdf.py.

  Keep this file ASCII-only: Windows PowerShell 5.1 reads BOM-less scripts in
  the system ANSI code page, so non-ASCII text here can break parsing.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File tools/render_office_pdf.ps1 `
      -InputPath docs/interfaces/<standard>.docx -OutputPdf $env:TEMP/std.pdf
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPdf
)

$ErrorActionPreference = "Stop"

$source = (Resolve-Path -LiteralPath $InputPath).Path
$target = [System.IO.Path]::GetFullPath($OutputPdf)
New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($target)) -Force | Out-Null
$extension = [System.IO.Path]::GetExtension($source).ToLowerInvariant()

$app = $null
$file = $null
try {
    switch ($extension) {
        ".docx" {
            $app = New-Object -ComObject Word.Application
            $app.Visible = $false
            $app.DisplayAlerts = 0                                  # wdAlertsNone
            $file = $app.Documents.Open($source, $false, $true)     # ConfirmConversions, ReadOnly
            $file.ExportAsFixedFormat($target, 17)                  # wdExportFormatPDF
            $file.Close(0)                                          # wdDoNotSaveChanges
        }
        ".pptx" {
            # PowerPoint refuses Visible = false; WithWindow = false keeps it hidden.
            $app = New-Object -ComObject PowerPoint.Application
            $file = $app.Presentations.Open($source, $true, $false, $false)  # ReadOnly, Untitled, WithWindow
            $file.SaveAs($target, 32)                               # ppSaveAsPDF
            $file.Close()
        }
        default {
            throw "Unsupported file type '$extension' (expected .docx or .pptx)"
        }
    }
    $file = $null
    Write-Output $target
}
finally {
    if ($null -ne $file) {
        try {
            if ($extension -eq ".docx") { $file.Close(0) } else { $file.Close() }
        } catch { }
    }
    if ($null -ne $app) {
        $app.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
