$ErrorActionPreference = 'Stop'
$interopPath = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $interopPath
$sourceCode = @"
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class BenchBodyMat {
 public static string Probe() {
  ISldWorks app=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  IModelDoc2 model=(IModelDoc2)app.GetOpenDocumentByName(@"C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\Bench_Prototype\Bench_Rotor\BD_RB_Part1.SLDPRT");
  IPartDoc part=(IPartDoc)model;
  Feature f=(Feature)part.FeatureByName("Bench_Defined_skin");
  object[] faces=(object[])f.GetFaces();
  IBody2 body=(IBody2)((IFace2)faces[0]).GetBody();
  int result=body.SetMaterialProperty("Default","Bench_Blade_Densities.sldmat","BLADE_CFRP_1550_PROVISIONAL");
  string db; string name=body.GetMaterialPropertyName("Default",out db);
  return "Code="+result+" Name="+name+" Database="+db;
 }
}
"@
Add-Type -TypeDefinition $sourceCode -ReferencedAssemblies $interopPath
[BenchBodyMat]::Probe()
