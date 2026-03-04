 //% knot 5_2, three-twist knot (KnotServer 5)
 //% process with doknotxzsymm
 //% x-z p-symmetrized by knotxzsymm.f
 //% adjusted with knotadjust.f
 //% shortened with knotshorten.f
// make with infill 80%, support angle 10 deg
r1 = 3;  d1 = 10;
// Path length     27.04*d1
// tube diameter 2*r1, closest approach d1-2*r1
 hull(){
translate(v=[ 0.006*d1,-1.866*d1,-0.581*d1])sphere(r=r1);
translate(v=[ 0.168*d1,-1.944*d1,-0.616*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.168*d1,-1.944*d1,-0.616*d1])sphere(r=r1);
translate(v=[ 0.338*d1,-2.002*d1,-0.626*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.338*d1,-2.002*d1,-0.626*d1])sphere(r=r1);
translate(v=[ 0.509*d1,-2.041*d1,-0.614*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.509*d1,-2.041*d1,-0.614*d1])sphere(r=r1);
translate(v=[ 0.677*d1,-2.057*d1,-0.583*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.677*d1,-2.057*d1,-0.583*d1])sphere(r=r1);
translate(v=[ 0.837*d1,-2.050*d1,-0.539*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.837*d1,-2.050*d1,-0.539*d1])sphere(r=r1);
translate(v=[ 0.984*d1,-2.020*d1,-0.484*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.984*d1,-2.020*d1,-0.484*d1])sphere(r=r1);
translate(v=[ 1.116*d1,-1.969*d1,-0.425*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.116*d1,-1.969*d1,-0.425*d1])sphere(r=r1);
translate(v=[ 1.232*d1,-1.898*d1,-0.365*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.232*d1,-1.898*d1,-0.365*d1])sphere(r=r1);
translate(v=[ 1.362*d1,-1.777*d1,-0.288*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.362*d1,-1.777*d1,-0.288*d1])sphere(r=r1);
translate(v=[ 1.465*d1,-1.631*d1,-0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.465*d1,-1.631*d1,-0.218*d1])sphere(r=r1);
translate(v=[ 1.564*d1,-1.424*d1,-0.137*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.564*d1,-1.424*d1,-0.137*d1])sphere(r=r1);
translate(v=[ 1.646*d1,-1.151*d1,-0.040*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.646*d1,-1.151*d1,-0.040*d1])sphere(r=r1);
translate(v=[ 1.688*d1,-0.913*d1, 0.054*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.688*d1,-0.913*d1, 0.054*d1])sphere(r=r1);
translate(v=[ 1.707*d1,-0.668*d1, 0.168*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.707*d1,-0.668*d1, 0.168*d1])sphere(r=r1);
translate(v=[ 1.696*d1,-0.419*d1, 0.301*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.696*d1,-0.419*d1, 0.301*d1])sphere(r=r1);
translate(v=[ 1.649*d1,-0.172*d1, 0.441*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.649*d1,-0.172*d1, 0.441*d1])sphere(r=r1);
translate(v=[ 1.584*d1, 0.022*d1, 0.546*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.584*d1, 0.022*d1, 0.546*d1])sphere(r=r1);
translate(v=[ 1.493*d1, 0.207*d1, 0.632*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.493*d1, 0.207*d1, 0.632*d1])sphere(r=r1);
translate(v=[ 1.411*d1, 0.338*d1, 0.676*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.411*d1, 0.338*d1, 0.676*d1])sphere(r=r1);
translate(v=[ 1.318*d1, 0.459*d1, 0.699*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.318*d1, 0.459*d1, 0.699*d1])sphere(r=r1);
translate(v=[ 1.218*d1, 0.569*d1, 0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.218*d1, 0.569*d1, 0.696*d1])sphere(r=r1);
translate(v=[ 1.114*d1, 0.668*d1, 0.666*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.114*d1, 0.668*d1, 0.666*d1])sphere(r=r1);
translate(v=[ 1.009*d1, 0.756*d1, 0.609*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.009*d1, 0.756*d1, 0.609*d1])sphere(r=r1);
translate(v=[ 0.908*d1, 0.834*d1, 0.527*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.908*d1, 0.834*d1, 0.527*d1])sphere(r=r1);
translate(v=[ 0.782*d1, 0.925*d1, 0.384*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.782*d1, 0.925*d1, 0.384*d1])sphere(r=r1);
translate(v=[ 0.642*d1, 1.029*d1, 0.172*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.642*d1, 1.029*d1, 0.172*d1])sphere(r=r1);
translate(v=[ 0.479*d1, 1.181*d1,-0.138*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.479*d1, 1.181*d1,-0.138*d1])sphere(r=r1);
translate(v=[ 0.393*d1, 1.284*d1,-0.293*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.393*d1, 1.284*d1,-0.293*d1])sphere(r=r1);
translate(v=[ 0.302*d1, 1.401*d1,-0.417*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.302*d1, 1.401*d1,-0.417*d1])sphere(r=r1);
translate(v=[ 0.226*d1, 1.496*d1,-0.483*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.226*d1, 1.496*d1,-0.483*d1])sphere(r=r1);
translate(v=[ 0.138*d1, 1.596*d1,-0.526*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.138*d1, 1.596*d1,-0.526*d1])sphere(r=r1);
translate(v=[ 0.038*d1, 1.697*d1,-0.545*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.038*d1, 1.697*d1,-0.545*d1])sphere(r=r1);
translate(v=[-0.077*d1, 1.793*d1,-0.540*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.077*d1, 1.793*d1,-0.540*d1])sphere(r=r1);
translate(v=[-0.205*d1, 1.879*d1,-0.514*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.205*d1, 1.879*d1,-0.514*d1])sphere(r=r1);
translate(v=[-0.346*d1, 1.949*d1,-0.469*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.346*d1, 1.949*d1,-0.469*d1])sphere(r=r1);
translate(v=[-0.495*d1, 1.999*d1,-0.409*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.495*d1, 1.999*d1,-0.409*d1])sphere(r=r1);
translate(v=[-0.649*d1, 2.023*d1,-0.337*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.649*d1, 2.023*d1,-0.337*d1])sphere(r=r1);
translate(v=[-0.802*d1, 2.020*d1,-0.257*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.802*d1, 2.020*d1,-0.257*d1])sphere(r=r1);
translate(v=[-0.950*d1, 1.988*d1,-0.172*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.950*d1, 1.988*d1,-0.172*d1])sphere(r=r1);
translate(v=[-1.086*d1, 1.927*d1,-0.084*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.086*d1, 1.927*d1,-0.084*d1])sphere(r=r1);
translate(v=[-1.206*d1, 1.839*d1, 0.004*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.206*d1, 1.839*d1, 0.004*d1])sphere(r=r1);
translate(v=[-1.305*d1, 1.727*d1, 0.089*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.305*d1, 1.727*d1, 0.089*d1])sphere(r=r1);
translate(v=[-1.381*d1, 1.596*d1, 0.169*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.381*d1, 1.596*d1, 0.169*d1])sphere(r=r1);
translate(v=[-1.432*d1, 1.451*d1, 0.243*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.432*d1, 1.451*d1, 0.243*d1])sphere(r=r1);
translate(v=[-1.457*d1, 1.297*d1, 0.309*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.457*d1, 1.297*d1, 0.309*d1])sphere(r=r1);
translate(v=[-1.459*d1, 1.141*d1, 0.363*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.459*d1, 1.141*d1, 0.363*d1])sphere(r=r1);
translate(v=[-1.439*d1, 0.986*d1, 0.404*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.439*d1, 0.986*d1, 0.404*d1])sphere(r=r1);
translate(v=[-1.400*d1, 0.837*d1, 0.430*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.400*d1, 0.837*d1, 0.430*d1])sphere(r=r1);
translate(v=[-1.345*d1, 0.696*d1, 0.439*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.345*d1, 0.696*d1, 0.439*d1])sphere(r=r1);
translate(v=[-1.277*d1, 0.566*d1, 0.428*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.277*d1, 0.566*d1, 0.428*d1])sphere(r=r1);
translate(v=[-1.201*d1, 0.447*d1, 0.397*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.201*d1, 0.447*d1, 0.397*d1])sphere(r=r1);
translate(v=[-1.118*d1, 0.339*d1, 0.346*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.118*d1, 0.339*d1, 0.346*d1])sphere(r=r1);
translate(v=[-0.999*d1, 0.209*d1, 0.248*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.999*d1, 0.209*d1, 0.248*d1])sphere(r=r1);
translate(v=[-0.841*d1, 0.065*d1, 0.085*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.841*d1, 0.065*d1, 0.085*d1])sphere(r=r1);
translate(v=[-0.562*d1,-0.145*d1,-0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.562*d1,-0.145*d1,-0.218*d1])sphere(r=r1);
translate(v=[-0.370*d1,-0.276*d1,-0.388*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.370*d1,-0.276*d1,-0.388*d1])sphere(r=r1);
translate(v=[-0.207*d1,-0.385*d1,-0.489*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.207*d1,-0.385*d1,-0.489*d1])sphere(r=r1);
translate(v=[-0.082*d1,-0.471*d1,-0.536*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.082*d1,-0.471*d1,-0.536*d1])sphere(r=r1);
translate(v=[ 0.042*d1,-0.560*d1,-0.553*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.042*d1,-0.560*d1,-0.553*d1])sphere(r=r1);
translate(v=[ 0.160*d1,-0.655*d1,-0.538*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.160*d1,-0.655*d1,-0.538*d1])sphere(r=r1);
translate(v=[ 0.268*d1,-0.754*d1,-0.492*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.268*d1,-0.754*d1,-0.492*d1])sphere(r=r1);
translate(v=[ 0.361*d1,-0.859*d1,-0.417*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.361*d1,-0.859*d1,-0.417*d1])sphere(r=r1);
translate(v=[ 0.433*d1,-0.968*d1,-0.316*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.433*d1,-0.968*d1,-0.316*d1])sphere(r=r1);
translate(v=[ 0.482*d1,-1.082*d1,-0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.482*d1,-1.082*d1,-0.197*d1])sphere(r=r1);
translate(v=[ 0.501*d1,-1.199*d1,-0.064*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.501*d1,-1.199*d1,-0.064*d1])sphere(r=r1);
translate(v=[ 0.490*d1,-1.319*d1, 0.072*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.490*d1,-1.319*d1, 0.072*d1])sphere(r=r1);
translate(v=[ 0.447*d1,-1.439*d1, 0.206*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.447*d1,-1.439*d1, 0.206*d1])sphere(r=r1);
translate(v=[ 0.373*d1,-1.557*d1, 0.329*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.373*d1,-1.557*d1, 0.329*d1])sphere(r=r1);
translate(v=[ 0.270*d1,-1.670*d1, 0.436*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.270*d1,-1.670*d1, 0.436*d1])sphere(r=r1);
translate(v=[ 0.142*d1,-1.774*d1, 0.521*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.142*d1,-1.774*d1, 0.521*d1])sphere(r=r1);
translate(v=[-0.006*d1,-1.866*d1, 0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.006*d1,-1.866*d1, 0.581*d1])sphere(r=r1);
translate(v=[-0.168*d1,-1.944*d1, 0.616*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.168*d1,-1.944*d1, 0.616*d1])sphere(r=r1);
translate(v=[-0.338*d1,-2.002*d1, 0.626*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.338*d1,-2.002*d1, 0.626*d1])sphere(r=r1);
translate(v=[-0.509*d1,-2.041*d1, 0.614*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.509*d1,-2.041*d1, 0.614*d1])sphere(r=r1);
translate(v=[-0.677*d1,-2.057*d1, 0.583*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.677*d1,-2.057*d1, 0.583*d1])sphere(r=r1);
translate(v=[-0.837*d1,-2.050*d1, 0.539*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.837*d1,-2.050*d1, 0.539*d1])sphere(r=r1);
translate(v=[-0.984*d1,-2.020*d1, 0.484*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.984*d1,-2.020*d1, 0.484*d1])sphere(r=r1);
translate(v=[-1.116*d1,-1.969*d1, 0.425*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.116*d1,-1.969*d1, 0.425*d1])sphere(r=r1);
translate(v=[-1.232*d1,-1.898*d1, 0.365*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.232*d1,-1.898*d1, 0.365*d1])sphere(r=r1);
translate(v=[-1.362*d1,-1.777*d1, 0.288*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.362*d1,-1.777*d1, 0.288*d1])sphere(r=r1);
translate(v=[-1.465*d1,-1.631*d1, 0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.465*d1,-1.631*d1, 0.218*d1])sphere(r=r1);
translate(v=[-1.564*d1,-1.424*d1, 0.137*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.564*d1,-1.424*d1, 0.137*d1])sphere(r=r1);
translate(v=[-1.646*d1,-1.151*d1, 0.040*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.646*d1,-1.151*d1, 0.040*d1])sphere(r=r1);
translate(v=[-1.688*d1,-0.913*d1,-0.054*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.688*d1,-0.913*d1,-0.054*d1])sphere(r=r1);
translate(v=[-1.707*d1,-0.668*d1,-0.168*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.707*d1,-0.668*d1,-0.168*d1])sphere(r=r1);
translate(v=[-1.696*d1,-0.419*d1,-0.301*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.696*d1,-0.419*d1,-0.301*d1])sphere(r=r1);
translate(v=[-1.649*d1,-0.172*d1,-0.441*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.649*d1,-0.172*d1,-0.441*d1])sphere(r=r1);
translate(v=[-1.584*d1, 0.022*d1,-0.546*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.584*d1, 0.022*d1,-0.546*d1])sphere(r=r1);
translate(v=[-1.493*d1, 0.207*d1,-0.632*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.493*d1, 0.207*d1,-0.632*d1])sphere(r=r1);
translate(v=[-1.411*d1, 0.338*d1,-0.676*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.411*d1, 0.338*d1,-0.676*d1])sphere(r=r1);
translate(v=[-1.318*d1, 0.459*d1,-0.699*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.318*d1, 0.459*d1,-0.699*d1])sphere(r=r1);
translate(v=[-1.218*d1, 0.569*d1,-0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.218*d1, 0.569*d1,-0.696*d1])sphere(r=r1);
translate(v=[-1.114*d1, 0.668*d1,-0.666*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.114*d1, 0.668*d1,-0.666*d1])sphere(r=r1);
translate(v=[-1.009*d1, 0.756*d1,-0.609*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.009*d1, 0.756*d1,-0.609*d1])sphere(r=r1);
translate(v=[-0.908*d1, 0.834*d1,-0.527*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.908*d1, 0.834*d1,-0.527*d1])sphere(r=r1);
translate(v=[-0.782*d1, 0.925*d1,-0.384*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.782*d1, 0.925*d1,-0.384*d1])sphere(r=r1);
translate(v=[-0.642*d1, 1.029*d1,-0.172*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.642*d1, 1.029*d1,-0.172*d1])sphere(r=r1);
translate(v=[-0.479*d1, 1.181*d1, 0.138*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.479*d1, 1.181*d1, 0.138*d1])sphere(r=r1);
translate(v=[-0.393*d1, 1.284*d1, 0.293*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.393*d1, 1.284*d1, 0.293*d1])sphere(r=r1);
translate(v=[-0.302*d1, 1.401*d1, 0.417*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.302*d1, 1.401*d1, 0.417*d1])sphere(r=r1);
translate(v=[-0.226*d1, 1.496*d1, 0.483*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.226*d1, 1.496*d1, 0.483*d1])sphere(r=r1);
translate(v=[-0.138*d1, 1.596*d1, 0.526*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.138*d1, 1.596*d1, 0.526*d1])sphere(r=r1);
translate(v=[-0.038*d1, 1.697*d1, 0.545*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.038*d1, 1.697*d1, 0.545*d1])sphere(r=r1);
translate(v=[ 0.077*d1, 1.793*d1, 0.540*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.077*d1, 1.793*d1, 0.540*d1])sphere(r=r1);
translate(v=[ 0.205*d1, 1.879*d1, 0.514*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.205*d1, 1.879*d1, 0.514*d1])sphere(r=r1);
translate(v=[ 0.346*d1, 1.949*d1, 0.469*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.346*d1, 1.949*d1, 0.469*d1])sphere(r=r1);
translate(v=[ 0.495*d1, 1.999*d1, 0.409*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.495*d1, 1.999*d1, 0.409*d1])sphere(r=r1);
translate(v=[ 0.649*d1, 2.023*d1, 0.337*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.649*d1, 2.023*d1, 0.337*d1])sphere(r=r1);
translate(v=[ 0.802*d1, 2.020*d1, 0.257*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.802*d1, 2.020*d1, 0.257*d1])sphere(r=r1);
translate(v=[ 0.950*d1, 1.988*d1, 0.172*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.950*d1, 1.988*d1, 0.172*d1])sphere(r=r1);
translate(v=[ 1.086*d1, 1.927*d1, 0.084*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.086*d1, 1.927*d1, 0.084*d1])sphere(r=r1);
translate(v=[ 1.206*d1, 1.839*d1,-0.004*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.206*d1, 1.839*d1,-0.004*d1])sphere(r=r1);
translate(v=[ 1.305*d1, 1.727*d1,-0.089*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.305*d1, 1.727*d1,-0.089*d1])sphere(r=r1);
translate(v=[ 1.381*d1, 1.596*d1,-0.169*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.381*d1, 1.596*d1,-0.169*d1])sphere(r=r1);
translate(v=[ 1.432*d1, 1.451*d1,-0.243*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.432*d1, 1.451*d1,-0.243*d1])sphere(r=r1);
translate(v=[ 1.457*d1, 1.297*d1,-0.309*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.457*d1, 1.297*d1,-0.309*d1])sphere(r=r1);
translate(v=[ 1.459*d1, 1.141*d1,-0.363*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.459*d1, 1.141*d1,-0.363*d1])sphere(r=r1);
translate(v=[ 1.439*d1, 0.986*d1,-0.404*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.439*d1, 0.986*d1,-0.404*d1])sphere(r=r1);
translate(v=[ 1.400*d1, 0.837*d1,-0.430*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.400*d1, 0.837*d1,-0.430*d1])sphere(r=r1);
translate(v=[ 1.345*d1, 0.696*d1,-0.439*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.345*d1, 0.696*d1,-0.439*d1])sphere(r=r1);
translate(v=[ 1.277*d1, 0.566*d1,-0.428*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.277*d1, 0.566*d1,-0.428*d1])sphere(r=r1);
translate(v=[ 1.201*d1, 0.447*d1,-0.397*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.201*d1, 0.447*d1,-0.397*d1])sphere(r=r1);
translate(v=[ 1.118*d1, 0.339*d1,-0.346*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.118*d1, 0.339*d1,-0.346*d1])sphere(r=r1);
translate(v=[ 0.999*d1, 0.209*d1,-0.248*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.999*d1, 0.209*d1,-0.248*d1])sphere(r=r1);
translate(v=[ 0.841*d1, 0.065*d1,-0.085*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.841*d1, 0.065*d1,-0.085*d1])sphere(r=r1);
translate(v=[ 0.562*d1,-0.145*d1, 0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.562*d1,-0.145*d1, 0.218*d1])sphere(r=r1);
translate(v=[ 0.370*d1,-0.276*d1, 0.388*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.370*d1,-0.276*d1, 0.388*d1])sphere(r=r1);
translate(v=[ 0.207*d1,-0.385*d1, 0.489*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.207*d1,-0.385*d1, 0.489*d1])sphere(r=r1);
translate(v=[ 0.082*d1,-0.471*d1, 0.536*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.082*d1,-0.471*d1, 0.536*d1])sphere(r=r1);
translate(v=[-0.042*d1,-0.560*d1, 0.553*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.042*d1,-0.560*d1, 0.553*d1])sphere(r=r1);
translate(v=[-0.160*d1,-0.655*d1, 0.538*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.160*d1,-0.655*d1, 0.538*d1])sphere(r=r1);
translate(v=[-0.268*d1,-0.754*d1, 0.492*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.268*d1,-0.754*d1, 0.492*d1])sphere(r=r1);
translate(v=[-0.361*d1,-0.859*d1, 0.417*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.361*d1,-0.859*d1, 0.417*d1])sphere(r=r1);
translate(v=[-0.433*d1,-0.968*d1, 0.316*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.433*d1,-0.968*d1, 0.316*d1])sphere(r=r1);
translate(v=[-0.482*d1,-1.082*d1, 0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.482*d1,-1.082*d1, 0.197*d1])sphere(r=r1);
translate(v=[-0.501*d1,-1.199*d1, 0.064*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.501*d1,-1.199*d1, 0.064*d1])sphere(r=r1);
translate(v=[-0.490*d1,-1.319*d1,-0.072*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.490*d1,-1.319*d1,-0.072*d1])sphere(r=r1);
translate(v=[-0.447*d1,-1.439*d1,-0.206*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.447*d1,-1.439*d1,-0.206*d1])sphere(r=r1);
translate(v=[-0.373*d1,-1.557*d1,-0.329*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.373*d1,-1.557*d1,-0.329*d1])sphere(r=r1);
translate(v=[-0.270*d1,-1.670*d1,-0.436*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.270*d1,-1.670*d1,-0.436*d1])sphere(r=r1);
translate(v=[-0.142*d1,-1.774*d1,-0.521*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.142*d1,-1.774*d1,-0.521*d1])sphere(r=r1);
translate(v=[-0.046*d1,-1.837*d1,-0.564*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.046*d1,-1.837*d1,-0.564*d1])sphere(r=r1);
translate(v=[ 0.006*d1,-1.866*d1,-0.581*d1])sphere(r=r1);}
