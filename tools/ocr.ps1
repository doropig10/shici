param([string]$InputDir, [string]$OutputDir, [int]$Limit = 0)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($Operation, $Type) {
  $task = $asTask.MakeGenericMethod($Type).Invoke($null, @($Operation))
  $task.Wait()
  $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('zh-Hans-CN'))
[IO.Directory]::CreateDirectory($OutputDir) | Out-Null
$files = @(Get-ChildItem -LiteralPath $InputDir -File | Where-Object Extension -Match '\.(png|jpg)$' | Sort-Object Name)
if ($Limit -gt 0) { $files = @($files | Select-Object -First $Limit) }
foreach ($item in $files) {
  $dest = Join-Path $OutputDir ($item.BaseName + '.json')
  if (Test-Path -LiteralPath $dest) { continue }
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($item.FullName)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  $lines = @($result.Lines | ForEach-Object {
    @{text=$_.Text; words=@($_.Words | ForEach-Object { @{text=$_.Text;x=$_.BoundingRect.X;y=$_.BoundingRect.Y;w=$_.BoundingRect.Width;h=$_.BoundingRect.Height} })}
  })
  @{width=$bitmap.PixelWidth;height=$bitmap.PixelHeight;lines=$lines} | ConvertTo-Json -Depth 8 -Compress | Set-Content -LiteralPath $dest -Encoding UTF8
  $bitmap.Dispose()
  $stream.Dispose()
  Write-Output $item.Name
}
