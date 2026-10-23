$ErrorActionPreference = 'Stop'
$interopPath = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $interopPath
$sourceCode = @"
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class BenchPack {
 public static object[] Copy() {
  ISldWorks app=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  string source=@"C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\Bench_Prototype\Starting_Live\Bench_Development_Source.SLDASM";
  IModelDoc2 model=(IModelDoc2)app.GetOpenDocumentByName(source);
  if(model==null || model.GetPathName()!=source)throw new Exception("Expected preserved comparison copy is not open");
  IModelDocExtension ext=model.Extension;
  IPackAndGo pg=(IPackAndGo)ext.GetPackAndGo();
  pg.IncludeDrawings=false;pg.IncludeSimulationResults=false;pg.IncludeToolboxComponents=true;
  pg.FlattenToSingleFolder=true;pg.AddPrefix="BD_";
  if(!pg.SetSaveToName(true,@"C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\Bench_Prototype\Bench_Rotor"))throw new Exception("SetSaveToName failed");
  object names;pg.GetDocumentNames(out names);
  object result=ext.SavePackAndGo((PackAndGo)pg);
  return new object[]{names,result};
 }
}
"@
Add-Type -TypeDefinition $sourceCode -ReferencedAssemblies $interopPath
$benchCopyResult = [BenchPack]::Copy()
$benchCopyResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\Bench_Prototype\BENCH_PACK_RESULT.json' -Encoding UTF8
Write-Output 'BENCH_PACK_FINISHED'
