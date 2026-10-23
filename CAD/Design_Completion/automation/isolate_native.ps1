$ErrorActionPreference = 'Stop'
$interopPath = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $interopPath
$sourceCode = @"
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class CycloPack {
 public static object[] Copy(string destination) {
  ISldWorks app=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  IModelDoc2 model=(IModelDoc2)app.IActiveDoc2;
  if(model.GetPathName()!=@"C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\Assem20_Design_RevB.SLDASM" || model.GetSaveFlag())throw new Exception("Unexpected or dirty active model");
  IModelDocExtension ext=model.Extension;
  IPackAndGo pg=(IPackAndGo)ext.GetPackAndGo();
  pg.IncludeDrawings=false;pg.IncludeSimulationResults=false;pg.IncludeToolboxComponents=true;pg.FlattenToSingleFolder=true;pg.AddPrefix="RB_";
  if(!pg.SetSaveToName(true,destination))throw new Exception("SetSaveToName failed");
  object names;pg.GetDocumentNames(out names);
  object result=ext.SavePackAndGo((PackAndGo)pg);
  return new object[]{names,result};
 }
}
"@
Add-Type -TypeDefinition $sourceCode -ReferencedAssemblies $interopPath
$copyResult = [CycloPack]::Copy('C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\RevB_Isolated')
$copyResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\PACK_AND_GO_RESULT.json' -Encoding UTF8
Write-Output 'PACK_AND_GO_FINISHED'
