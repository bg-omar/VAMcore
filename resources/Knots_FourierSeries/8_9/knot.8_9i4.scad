 //% Knot 8_9
 //%mns=200
 //%+I4
 //%process with  doknotscad.i4
 //%path length 137.33
 //% adjusted with knotadjust.ri.f
 //%0.57  -.18  .12
 //%.68  -.02  .18
 //% shortened with knotshorten.f
// make with infill 80%, support angle 10 deg
r1 = 3;  d1 = 10;
// Path length    130.66*d1
// tube diameter 2*r1, closest approach d1-2*r1
 hull(){
translate(v=[ 0.034*d1,-0.009*d1, 6.244*d1])sphere(r=r1);
translate(v=[ 0.381*d1,-0.107*d1, 6.163*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.381*d1,-0.107*d1, 6.163*d1])sphere(r=r1);
translate(v=[ 0.703*d1,-0.199*d1, 6.052*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.703*d1,-0.199*d1, 6.052*d1])sphere(r=r1);
translate(v=[ 1.027*d1,-0.294*d1, 5.902*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.027*d1,-0.294*d1, 5.902*d1])sphere(r=r1);
translate(v=[ 1.345*d1,-0.387*d1, 5.713*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.345*d1,-0.387*d1, 5.713*d1])sphere(r=r1);
translate(v=[ 1.647*d1,-0.478*d1, 5.489*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.647*d1,-0.478*d1, 5.489*d1])sphere(r=r1);
translate(v=[ 1.928*d1,-0.564*d1, 5.235*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.928*d1,-0.564*d1, 5.235*d1])sphere(r=r1);
translate(v=[ 2.181*d1,-0.642*d1, 4.959*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.181*d1,-0.642*d1, 4.959*d1])sphere(r=r1);
translate(v=[ 2.429*d1,-0.719*d1, 4.635*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.429*d1,-0.719*d1, 4.635*d1])sphere(r=r1);
translate(v=[ 2.659*d1,-0.791*d1, 4.269*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.659*d1,-0.791*d1, 4.269*d1])sphere(r=r1);
translate(v=[ 2.864*d1,-0.856*d1, 3.871*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.864*d1,-0.856*d1, 3.871*d1])sphere(r=r1);
translate(v=[ 3.051*d1,-0.915*d1, 3.421*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.051*d1,-0.915*d1, 3.421*d1])sphere(r=r1);
translate(v=[ 3.221*d1,-0.968*d1, 2.908*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.221*d1,-0.968*d1, 2.908*d1])sphere(r=r1);
translate(v=[ 3.387*d1,-1.018*d1, 2.276*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.387*d1,-1.018*d1, 2.276*d1])sphere(r=r1);
translate(v=[ 3.586*d1,-1.069*d1, 1.344*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.586*d1,-1.069*d1, 1.344*d1])sphere(r=r1);
translate(v=[ 3.625*d1,-1.077*d1, 1.151*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.625*d1,-1.077*d1, 1.151*d1])sphere(r=r1);
translate(v=[ 3.644*d1,-1.073*d1, 1.135*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.644*d1,-1.073*d1, 1.135*d1])sphere(r=r1);
translate(v=[ 3.811*d1,-0.944*d1, 1.083*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.811*d1,-0.944*d1, 1.083*d1])sphere(r=r1);
translate(v=[ 3.941*d1,-0.824*d1, 1.071*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.941*d1,-0.824*d1, 1.071*d1])sphere(r=r1);
translate(v=[ 4.148*d1,-0.609*d1, 1.103*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.148*d1,-0.609*d1, 1.103*d1])sphere(r=r1);
translate(v=[ 4.293*d1,-0.433*d1, 1.146*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.293*d1,-0.433*d1, 1.146*d1])sphere(r=r1);
translate(v=[ 4.386*d1,-0.264*d1, 1.198*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.386*d1,-0.264*d1, 1.198*d1])sphere(r=r1);
translate(v=[ 4.430*d1,-0.107*d1, 1.240*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.430*d1,-0.107*d1, 1.240*d1])sphere(r=r1);
translate(v=[ 4.483*d1, 0.185*d1, 1.300*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.483*d1, 0.185*d1, 1.300*d1])sphere(r=r1);
translate(v=[ 4.482*d1, 0.339*d1, 1.152*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.482*d1, 0.339*d1, 1.152*d1])sphere(r=r1);
translate(v=[ 4.516*d1, 0.478*d1, 0.989*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.516*d1, 0.478*d1, 0.989*d1])sphere(r=r1);
translate(v=[ 4.584*d1, 0.603*d1, 0.809*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.584*d1, 0.603*d1, 0.809*d1])sphere(r=r1);
translate(v=[ 4.758*d1, 0.791*d1, 0.469*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.758*d1, 0.791*d1, 0.469*d1])sphere(r=r1);
translate(v=[ 4.838*d1, 0.966*d1, 0.245*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.838*d1, 0.966*d1, 0.245*d1])sphere(r=r1);
translate(v=[ 4.854*d1, 0.966*d1, 0.077*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.854*d1, 0.966*d1, 0.077*d1])sphere(r=r1);
translate(v=[ 4.877*d1, 0.939*d1,-0.082*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.877*d1, 0.939*d1,-0.082*d1])sphere(r=r1);
translate(v=[ 4.925*d1, 0.785*d1,-0.238*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.925*d1, 0.785*d1,-0.238*d1])sphere(r=r1);
translate(v=[ 4.994*d1, 0.655*d1,-0.358*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.994*d1, 0.655*d1,-0.358*d1])sphere(r=r1);
translate(v=[ 5.188*d1, 0.406*d1,-0.589*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.188*d1, 0.406*d1,-0.589*d1])sphere(r=r1);
translate(v=[ 5.321*d1, 0.248*d1,-0.788*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.321*d1, 0.248*d1,-0.788*d1])sphere(r=r1);
translate(v=[ 5.402*d1, 0.134*d1,-0.933*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.402*d1, 0.134*d1,-0.933*d1])sphere(r=r1);
translate(v=[ 5.462*d1,-0.008*d1,-0.973*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.462*d1,-0.008*d1,-0.973*d1])sphere(r=r1);
translate(v=[ 5.506*d1,-0.148*d1,-0.979*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.506*d1,-0.148*d1,-0.979*d1])sphere(r=r1);
translate(v=[ 5.597*d1,-0.327*d1,-0.792*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.597*d1,-0.327*d1,-0.792*d1])sphere(r=r1);
translate(v=[ 5.753*d1,-0.547*d1,-0.566*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.753*d1,-0.547*d1,-0.566*d1])sphere(r=r1);
translate(v=[ 5.853*d1,-0.743*d1,-0.407*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.853*d1,-0.743*d1,-0.407*d1])sphere(r=r1);
translate(v=[ 5.926*d1,-0.954*d1,-0.227*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.926*d1,-0.954*d1,-0.227*d1])sphere(r=r1);
translate(v=[ 5.953*d1,-1.082*d1,-0.095*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.953*d1,-1.082*d1,-0.095*d1])sphere(r=r1);
translate(v=[ 5.990*d1,-1.097*d1, 0.214*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.990*d1,-1.097*d1, 0.214*d1])sphere(r=r1);
translate(v=[ 6.056*d1,-0.934*d1, 0.407*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.056*d1,-0.934*d1, 0.407*d1])sphere(r=r1);
translate(v=[ 6.156*d1,-0.773*d1, 0.589*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.156*d1,-0.773*d1, 0.589*d1])sphere(r=r1);
translate(v=[ 6.310*d1,-0.568*d1, 0.805*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.310*d1,-0.568*d1, 0.805*d1])sphere(r=r1);
translate(v=[ 6.434*d1,-0.375*d1, 0.954*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.434*d1,-0.375*d1, 0.954*d1])sphere(r=r1);
translate(v=[ 6.525*d1,-0.177*d1, 1.080*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.525*d1,-0.177*d1, 1.080*d1])sphere(r=r1);
translate(v=[ 6.548*d1,-0.104*d1, 1.123*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.548*d1,-0.104*d1, 1.123*d1])sphere(r=r1);
translate(v=[ 6.630*d1, 0.165*d1, 1.095*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.630*d1, 0.165*d1, 1.095*d1])sphere(r=r1);
translate(v=[ 6.740*d1, 0.356*d1, 0.896*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.740*d1, 0.356*d1, 0.896*d1])sphere(r=r1);
translate(v=[ 6.889*d1, 0.581*d1, 0.602*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.889*d1, 0.581*d1, 0.602*d1])sphere(r=r1);
translate(v=[ 7.105*d1, 0.841*d1, 0.274*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.105*d1, 0.841*d1, 0.274*d1])sphere(r=r1);
translate(v=[ 7.174*d1, 0.916*d1, 0.142*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.174*d1, 0.916*d1, 0.142*d1])sphere(r=r1);
translate(v=[ 7.256*d1, 0.883*d1,-0.040*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.256*d1, 0.883*d1,-0.040*d1])sphere(r=r1);
translate(v=[ 7.315*d1, 0.874*d1,-0.148*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.315*d1, 0.874*d1,-0.148*d1])sphere(r=r1);
translate(v=[ 7.365*d1, 0.842*d1,-0.215*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.365*d1, 0.842*d1,-0.215*d1])sphere(r=r1);
translate(v=[ 7.564*d1, 0.775*d1,-0.459*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.564*d1, 0.775*d1,-0.459*d1])sphere(r=r1);
translate(v=[ 7.739*d1, 0.698*d1,-0.637*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.739*d1, 0.698*d1,-0.637*d1])sphere(r=r1);
translate(v=[ 7.904*d1, 0.595*d1,-0.787*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.904*d1, 0.595*d1,-0.787*d1])sphere(r=r1);
translate(v=[ 8.056*d1, 0.467*d1,-0.907*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.056*d1, 0.467*d1,-0.907*d1])sphere(r=r1);
translate(v=[ 8.172*d1, 0.330*d1,-0.994*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.172*d1, 0.330*d1,-0.994*d1])sphere(r=r1);
translate(v=[ 8.240*d1, 0.205*d1,-1.060*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.240*d1, 0.205*d1,-1.060*d1])sphere(r=r1);
translate(v=[ 8.254*d1, 0.165*d1,-1.078*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.254*d1, 0.165*d1,-1.078*d1])sphere(r=r1);
translate(v=[ 8.295*d1, 0.032*d1,-1.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.295*d1, 0.032*d1,-1.096*d1])sphere(r=r1);
translate(v=[ 8.295*d1,-0.116*d1,-1.142*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.295*d1,-0.116*d1,-1.142*d1])sphere(r=r1);
translate(v=[ 8.292*d1,-0.164*d1,-1.155*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.292*d1,-0.164*d1,-1.155*d1])sphere(r=r1);
translate(v=[ 8.522*d1,-0.578*d1,-1.104*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.522*d1,-0.578*d1,-1.104*d1])sphere(r=r1);
translate(v=[ 8.625*d1,-0.817*d1,-1.048*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.625*d1,-0.817*d1,-1.048*d1])sphere(r=r1);
translate(v=[ 8.694*d1,-1.051*d1,-0.970*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.694*d1,-1.051*d1,-0.970*d1])sphere(r=r1);
translate(v=[ 8.735*d1,-1.279*d1,-0.867*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.735*d1,-1.279*d1,-0.867*d1])sphere(r=r1);
translate(v=[ 8.747*d1,-1.492*d1,-0.744*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.747*d1,-1.492*d1,-0.744*d1])sphere(r=r1);
translate(v=[ 8.734*d1,-1.651*d1,-0.638*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.734*d1,-1.651*d1,-0.638*d1])sphere(r=r1);
translate(v=[ 8.657*d1,-1.869*d1,-0.522*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.657*d1,-1.869*d1,-0.522*d1])sphere(r=r1);
translate(v=[ 8.557*d1,-2.052*d1,-0.405*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.557*d1,-2.052*d1,-0.405*d1])sphere(r=r1);
translate(v=[ 8.417*d1,-2.225*d1,-0.282*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.417*d1,-2.225*d1,-0.282*d1])sphere(r=r1);
translate(v=[ 8.304*d1,-2.321*d1,-0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.304*d1,-2.321*d1,-0.218*d1])sphere(r=r1);
translate(v=[ 8.116*d1,-2.438*d1,-0.148*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.116*d1,-2.438*d1,-0.148*d1])sphere(r=r1);
translate(v=[ 7.887*d1,-2.542*d1,-0.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.887*d1,-2.542*d1,-0.096*d1])sphere(r=r1);
translate(v=[ 7.591*d1,-2.630*d1,-0.058*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.591*d1,-2.630*d1,-0.058*d1])sphere(r=r1);
translate(v=[ 7.484*d1,-2.667*d1,-0.049*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.484*d1,-2.667*d1,-0.049*d1])sphere(r=r1);
translate(v=[ 7.461*d1,-2.682*d1,-0.048*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.461*d1,-2.682*d1,-0.048*d1])sphere(r=r1);
translate(v=[ 7.208*d1,-3.160*d1,-0.042*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.208*d1,-3.160*d1,-0.042*d1])sphere(r=r1);
translate(v=[ 6.979*d1,-3.522*d1,-0.039*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.979*d1,-3.522*d1,-0.039*d1])sphere(r=r1);
translate(v=[ 6.710*d1,-3.878*d1,-0.035*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.710*d1,-3.878*d1,-0.035*d1])sphere(r=r1);
translate(v=[ 6.442*d1,-4.179*d1,-0.032*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.442*d1,-4.179*d1,-0.032*d1])sphere(r=r1);
translate(v=[ 6.147*d1,-4.463*d1,-0.030*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.147*d1,-4.463*d1,-0.030*d1])sphere(r=r1);
translate(v=[ 5.828*d1,-4.726*d1,-0.027*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.828*d1,-4.726*d1,-0.027*d1])sphere(r=r1);
translate(v=[ 5.443*d1,-4.996*d1,-0.025*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.443*d1,-4.996*d1,-0.025*d1])sphere(r=r1);
translate(v=[ 5.042*d1,-5.231*d1,-0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.042*d1,-5.231*d1,-0.022*d1])sphere(r=r1);
translate(v=[ 4.633*d1,-5.430*d1,-0.020*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.633*d1,-5.430*d1,-0.020*d1])sphere(r=r1);
translate(v=[ 4.173*d1,-5.613*d1,-0.018*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.173*d1,-5.613*d1,-0.018*d1])sphere(r=r1);
translate(v=[ 3.671*d1,-5.772*d1,-0.016*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.671*d1,-5.772*d1,-0.016*d1])sphere(r=r1);
translate(v=[ 3.136*d1,-5.902*d1,-0.014*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.136*d1,-5.902*d1,-0.014*d1])sphere(r=r1);
translate(v=[ 2.527*d1,-6.008*d1,-0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.527*d1,-6.008*d1,-0.011*d1])sphere(r=r1);
translate(v=[ 1.772*d1,-6.096*d1,-0.008*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.772*d1,-6.096*d1,-0.008*d1])sphere(r=r1);
translate(v=[ 0.772*d1,-6.173*d1,-0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.772*d1,-6.173*d1,-0.003*d1])sphere(r=r1);
translate(v=[ 0.021*d1,-6.224*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.021*d1,-6.224*d1, 0.000*d1])sphere(r=r1);
translate(v=[-0.021*d1,-6.241*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.021*d1,-6.241*d1, 0.000*d1])sphere(r=r1);
translate(v=[-0.375*d1,-6.242*d1, 0.001*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.375*d1,-6.242*d1, 0.001*d1])sphere(r=r1);
translate(v=[-0.695*d1,-6.209*d1, 0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.695*d1,-6.209*d1, 0.003*d1])sphere(r=r1);
translate(v=[-1.014*d1,-6.143*d1, 0.004*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.014*d1,-6.143*d1, 0.004*d1])sphere(r=r1);
translate(v=[-1.328*d1,-6.044*d1, 0.006*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.328*d1,-6.044*d1, 0.006*d1])sphere(r=r1);
translate(v=[-1.671*d1,-5.895*d1, 0.007*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.671*d1,-5.895*d1, 0.007*d1])sphere(r=r1);
translate(v=[-1.999*d1,-5.710*d1, 0.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.999*d1,-5.710*d1, 0.009*d1])sphere(r=r1);
translate(v=[-2.310*d1,-5.493*d1, 0.010*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.310*d1,-5.493*d1, 0.010*d1])sphere(r=r1);
translate(v=[-2.634*d1,-5.220*d1, 0.012*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.634*d1,-5.220*d1, 0.012*d1])sphere(r=r1);
translate(v=[-2.934*d1,-4.919*d1, 0.013*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.934*d1,-4.919*d1, 0.013*d1])sphere(r=r1);
translate(v=[-3.236*d1,-4.559*d1, 0.014*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.236*d1,-4.559*d1, 0.014*d1])sphere(r=r1);
translate(v=[-3.509*d1,-4.175*d1, 0.015*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.509*d1,-4.175*d1, 0.015*d1])sphere(r=r1);
translate(v=[-3.773*d1,-3.739*d1, 0.017*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.773*d1,-3.739*d1, 0.017*d1])sphere(r=r1);
translate(v=[-4.021*d1,-3.260*d1, 0.019*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.021*d1,-3.260*d1, 0.019*d1])sphere(r=r1);
translate(v=[-4.258*d1,-2.718*d1, 0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.258*d1,-2.718*d1, 0.022*d1])sphere(r=r1);
translate(v=[-4.469*d1,-2.140*d1, 0.025*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.469*d1,-2.140*d1, 0.025*d1])sphere(r=r1);
translate(v=[-4.607*d1,-1.681*d1, 0.029*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.607*d1,-1.681*d1, 0.029*d1])sphere(r=r1);
translate(v=[-4.605*d1,-1.641*d1, 0.030*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.605*d1,-1.641*d1, 0.030*d1])sphere(r=r1);
translate(v=[-4.432*d1,-1.392*d1, 0.063*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.432*d1,-1.392*d1, 0.063*d1])sphere(r=r1);
translate(v=[-4.348*d1,-1.239*d1, 0.104*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.348*d1,-1.239*d1, 0.104*d1])sphere(r=r1);
translate(v=[-4.303*d1,-1.118*d1, 0.155*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.303*d1,-1.118*d1, 0.155*d1])sphere(r=r1);
translate(v=[-4.273*d1,-0.930*d1, 0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.273*d1,-0.930*d1, 0.254*d1])sphere(r=r1);
translate(v=[-4.275*d1,-0.784*d1, 0.327*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.275*d1,-0.784*d1, 0.327*d1])sphere(r=r1);
translate(v=[-4.319*d1,-0.611*d1, 0.440*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.319*d1,-0.611*d1, 0.440*d1])sphere(r=r1);
translate(v=[-4.393*d1,-0.430*d1, 0.529*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.393*d1,-0.430*d1, 0.529*d1])sphere(r=r1);
translate(v=[-4.503*d1,-0.239*d1, 0.598*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.503*d1,-0.239*d1, 0.598*d1])sphere(r=r1);
translate(v=[-4.595*d1,-0.081*d1, 0.639*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.595*d1,-0.081*d1, 0.639*d1])sphere(r=r1);
translate(v=[-4.606*d1, 0.032*d1, 0.606*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.606*d1, 0.032*d1, 0.606*d1])sphere(r=r1);
translate(v=[-4.633*d1, 0.111*d1, 0.599*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.633*d1, 0.111*d1, 0.599*d1])sphere(r=r1);
translate(v=[-4.707*d1, 0.230*d1, 0.553*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.707*d1, 0.230*d1, 0.553*d1])sphere(r=r1);
translate(v=[-4.830*d1, 0.356*d1, 0.488*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.830*d1, 0.356*d1, 0.488*d1])sphere(r=r1);
translate(v=[-4.968*d1, 0.462*d1, 0.389*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.968*d1, 0.462*d1, 0.389*d1])sphere(r=r1);
translate(v=[-5.115*d1, 0.546*d1, 0.256*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.115*d1, 0.546*d1, 0.256*d1])sphere(r=r1);
translate(v=[-5.226*d1, 0.616*d1, 0.117*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.226*d1, 0.616*d1, 0.117*d1])sphere(r=r1);
translate(v=[-5.242*d1, 0.630*d1, 0.091*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.242*d1, 0.630*d1, 0.091*d1])sphere(r=r1);
translate(v=[-5.314*d1, 0.668*d1,-0.065*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.314*d1, 0.668*d1,-0.065*d1])sphere(r=r1);
translate(v=[-5.329*d1, 0.679*d1,-0.115*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.329*d1, 0.679*d1,-0.115*d1])sphere(r=r1);
translate(v=[-5.434*d1, 0.595*d1,-0.284*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.434*d1, 0.595*d1,-0.284*d1])sphere(r=r1);
translate(v=[-5.552*d1, 0.474*d1,-0.477*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.552*d1, 0.474*d1,-0.477*d1])sphere(r=r1);
translate(v=[-5.626*d1, 0.354*d1,-0.671*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.626*d1, 0.354*d1,-0.671*d1])sphere(r=r1);
translate(v=[-5.693*d1, 0.169*d1,-0.913*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.693*d1, 0.169*d1,-0.913*d1])sphere(r=r1);
translate(v=[-5.703*d1, 0.133*d1,-0.944*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.703*d1, 0.133*d1,-0.944*d1])sphere(r=r1);
translate(v=[-5.757*d1,-0.072*d1,-0.986*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.757*d1,-0.072*d1,-0.986*d1])sphere(r=r1);
translate(v=[-5.765*d1,-0.105*d1,-0.986*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.765*d1,-0.105*d1,-0.986*d1])sphere(r=r1);
translate(v=[-5.907*d1,-0.376*d1,-0.857*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.907*d1,-0.376*d1,-0.857*d1])sphere(r=r1);
translate(v=[-6.037*d1,-0.583*d1,-0.739*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.037*d1,-0.583*d1,-0.739*d1])sphere(r=r1);
translate(v=[-6.165*d1,-0.789*d1,-0.576*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.165*d1,-0.789*d1,-0.576*d1])sphere(r=r1);
translate(v=[-6.231*d1,-0.939*d1,-0.441*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.231*d1,-0.939*d1,-0.441*d1])sphere(r=r1);
translate(v=[-6.264*d1,-1.098*d1,-0.282*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.264*d1,-1.098*d1,-0.282*d1])sphere(r=r1);
translate(v=[-6.268*d1,-1.148*d1,-0.217*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.268*d1,-1.148*d1,-0.217*d1])sphere(r=r1);
translate(v=[-6.309*d1,-1.151*d1, 0.053*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.309*d1,-1.151*d1, 0.053*d1])sphere(r=r1);
translate(v=[-6.317*d1,-1.145*d1, 0.110*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.317*d1,-1.145*d1, 0.110*d1])sphere(r=r1);
translate(v=[-6.431*d1,-0.939*d1, 0.337*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.431*d1,-0.939*d1, 0.337*d1])sphere(r=r1);
translate(v=[-6.640*d1,-0.614*d1, 0.671*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.640*d1,-0.614*d1, 0.671*d1])sphere(r=r1);
translate(v=[-6.757*d1,-0.442*d1, 0.897*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.757*d1,-0.442*d1, 0.897*d1])sphere(r=r1);
translate(v=[-6.812*d1,-0.306*d1, 1.075*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.812*d1,-0.306*d1, 1.075*d1])sphere(r=r1);
translate(v=[-6.836*d1,-0.178*d1, 1.217*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.836*d1,-0.178*d1, 1.217*d1])sphere(r=r1);
translate(v=[-6.892*d1,-0.010*d1, 1.228*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.892*d1,-0.010*d1, 1.228*d1])sphere(r=r1);
translate(v=[-6.973*d1, 0.163*d1, 1.207*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.973*d1, 0.163*d1, 1.207*d1])sphere(r=r1);
translate(v=[-6.994*d1, 0.194*d1, 1.193*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.994*d1, 0.194*d1, 1.193*d1])sphere(r=r1);
translate(v=[-7.298*d1, 0.516*d1, 0.882*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.298*d1, 0.516*d1, 0.882*d1])sphere(r=r1);
translate(v=[-7.460*d1, 0.733*d1, 0.721*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.460*d1, 0.733*d1, 0.721*d1])sphere(r=r1);
translate(v=[-7.584*d1, 0.946*d1, 0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.584*d1, 0.946*d1, 0.581*d1])sphere(r=r1);
translate(v=[-7.650*d1, 1.114*d1, 0.462*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.650*d1, 1.114*d1, 0.462*d1])sphere(r=r1);
translate(v=[-7.683*d1, 1.294*d1, 0.309*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.683*d1, 1.294*d1, 0.309*d1])sphere(r=r1);
translate(v=[-7.681*d1, 1.457*d1, 0.151*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.681*d1, 1.457*d1, 0.151*d1])sphere(r=r1);
translate(v=[-7.679*d1, 1.485*d1, 0.111*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.679*d1, 1.485*d1, 0.111*d1])sphere(r=r1);
translate(v=[-7.696*d1, 1.530*d1,-0.108*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.696*d1, 1.530*d1,-0.108*d1])sphere(r=r1);
translate(v=[-7.699*d1, 1.541*d1,-0.320*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.699*d1, 1.541*d1,-0.320*d1])sphere(r=r1);
translate(v=[-7.703*d1, 1.535*d1,-0.394*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.703*d1, 1.535*d1,-0.394*d1])sphere(r=r1);
translate(v=[-7.880*d1, 1.296*d1,-0.800*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.880*d1, 1.296*d1,-0.800*d1])sphere(r=r1);
translate(v=[-7.976*d1, 1.208*d1,-1.043*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.976*d1, 1.208*d1,-1.043*d1])sphere(r=r1);
translate(v=[-8.059*d1, 1.107*d1,-1.324*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.059*d1, 1.107*d1,-1.324*d1])sphere(r=r1);
translate(v=[-8.104*d1, 0.997*d1,-1.557*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.104*d1, 0.997*d1,-1.557*d1])sphere(r=r1);
translate(v=[-8.121*d1, 0.869*d1,-1.765*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.121*d1, 0.869*d1,-1.765*d1])sphere(r=r1);
translate(v=[-8.110*d1, 0.722*d1,-1.957*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.110*d1, 0.722*d1,-1.957*d1])sphere(r=r1);
translate(v=[-8.071*d1, 0.560*d1,-2.128*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.071*d1, 0.560*d1,-2.128*d1])sphere(r=r1);
translate(v=[-8.003*d1, 0.382*d1,-2.278*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.003*d1, 0.382*d1,-2.278*d1])sphere(r=r1);
translate(v=[-7.980*d1, 0.330*d1,-2.315*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.980*d1, 0.330*d1,-2.315*d1])sphere(r=r1);
translate(v=[-8.062*d1, 0.073*d1,-2.307*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.062*d1, 0.073*d1,-2.307*d1])sphere(r=r1);
translate(v=[-8.180*d1,-0.399*d1,-2.251*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.180*d1,-0.399*d1,-2.251*d1])sphere(r=r1);
translate(v=[-8.289*d1,-0.674*d1,-2.234*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.289*d1,-0.674*d1,-2.234*d1])sphere(r=r1);
translate(v=[-8.430*d1,-0.974*d1,-2.242*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.430*d1,-0.974*d1,-2.242*d1])sphere(r=r1);
translate(v=[-8.645*d1,-1.414*d1,-2.305*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.645*d1,-1.414*d1,-2.305*d1])sphere(r=r1);
translate(v=[-8.790*d1,-1.764*d1,-2.376*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.790*d1,-1.764*d1,-2.376*d1])sphere(r=r1);
translate(v=[-8.870*d1,-2.004*d1,-2.447*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.870*d1,-2.004*d1,-2.447*d1])sphere(r=r1);
translate(v=[-8.931*d1,-2.241*d1,-2.551*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.931*d1,-2.241*d1,-2.551*d1])sphere(r=r1);
translate(v=[-8.983*d1,-2.509*d1,-2.707*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.983*d1,-2.509*d1,-2.707*d1])sphere(r=r1);
translate(v=[-9.009*d1,-2.668*d1,-2.817*d1])sphere(r=r1);}
 hull(){
translate(v=[-9.009*d1,-2.668*d1,-2.817*d1])sphere(r=r1);
translate(v=[-9.011*d1,-2.676*d1,-2.862*d1])sphere(r=r1);}
 hull(){
translate(v=[-9.011*d1,-2.676*d1,-2.862*d1])sphere(r=r1);
translate(v=[-8.836*d1,-2.632*d1,-3.253*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.836*d1,-2.632*d1,-3.253*d1])sphere(r=r1);
translate(v=[-8.623*d1,-2.575*d1,-3.637*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.623*d1,-2.575*d1,-3.637*d1])sphere(r=r1);
translate(v=[-8.375*d1,-2.506*d1,-4.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.375*d1,-2.506*d1,-4.009*d1])sphere(r=r1);
translate(v=[-8.093*d1,-2.426*d1,-4.362*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.093*d1,-2.426*d1,-4.362*d1])sphere(r=r1);
translate(v=[-7.779*d1,-2.335*d1,-4.693*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.779*d1,-2.335*d1,-4.693*d1])sphere(r=r1);
translate(v=[-7.438*d1,-2.235*d1,-4.998*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.438*d1,-2.235*d1,-4.998*d1])sphere(r=r1);
translate(v=[-7.072*d1,-2.126*d1,-5.275*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.072*d1,-2.126*d1,-5.275*d1])sphere(r=r1);
translate(v=[-6.684*d1,-2.010*d1,-5.522*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.684*d1,-2.010*d1,-5.522*d1])sphere(r=r1);
translate(v=[-6.278*d1,-1.887*d1,-5.738*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.278*d1,-1.887*d1,-5.738*d1])sphere(r=r1);
translate(v=[-5.857*d1,-1.759*d1,-5.925*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.857*d1,-1.759*d1,-5.925*d1])sphere(r=r1);
translate(v=[-5.369*d1,-1.611*d1,-6.099*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.369*d1,-1.611*d1,-6.099*d1])sphere(r=r1);
translate(v=[-4.873*d1,-1.459*d1,-6.237*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.873*d1,-1.459*d1,-6.237*d1])sphere(r=r1);
translate(v=[-4.373*d1,-1.305*d1,-6.340*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.373*d1,-1.305*d1,-6.340*d1])sphere(r=r1);
translate(v=[-3.819*d1,-1.135*d1,-6.417*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.819*d1,-1.135*d1,-6.417*d1])sphere(r=r1);
translate(v=[-3.220*d1,-0.952*d1,-6.462*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.220*d1,-0.952*d1,-6.462*d1])sphere(r=r1);
translate(v=[-2.586*d1,-0.758*d1,-6.472*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.586*d1,-0.758*d1,-6.472*d1])sphere(r=r1);
translate(v=[-1.887*d1,-0.547*d1,-6.445*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.887*d1,-0.547*d1,-6.445*d1])sphere(r=r1);
translate(v=[-1.110*d1,-0.317*d1,-6.373*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.110*d1,-0.317*d1,-6.373*d1])sphere(r=r1);
translate(v=[-0.207*d1,-0.058*d1,-6.249*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.207*d1,-0.058*d1,-6.249*d1])sphere(r=r1);
translate(v=[-0.034*d1,-0.009*d1,-6.221*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.034*d1,-0.009*d1,-6.221*d1])sphere(r=r1);
translate(v=[ 0.034*d1, 0.009*d1,-6.244*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.034*d1, 0.009*d1,-6.244*d1])sphere(r=r1);
translate(v=[ 0.381*d1, 0.107*d1,-6.163*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.381*d1, 0.107*d1,-6.163*d1])sphere(r=r1);
translate(v=[ 0.703*d1, 0.199*d1,-6.052*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.703*d1, 0.199*d1,-6.052*d1])sphere(r=r1);
translate(v=[ 1.027*d1, 0.294*d1,-5.902*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.027*d1, 0.294*d1,-5.902*d1])sphere(r=r1);
translate(v=[ 1.345*d1, 0.387*d1,-5.713*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.345*d1, 0.387*d1,-5.713*d1])sphere(r=r1);
translate(v=[ 1.647*d1, 0.478*d1,-5.489*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.647*d1, 0.478*d1,-5.489*d1])sphere(r=r1);
translate(v=[ 1.928*d1, 0.564*d1,-5.235*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.928*d1, 0.564*d1,-5.235*d1])sphere(r=r1);
translate(v=[ 2.181*d1, 0.642*d1,-4.959*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.181*d1, 0.642*d1,-4.959*d1])sphere(r=r1);
translate(v=[ 2.429*d1, 0.719*d1,-4.635*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.429*d1, 0.719*d1,-4.635*d1])sphere(r=r1);
translate(v=[ 2.659*d1, 0.791*d1,-4.269*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.659*d1, 0.791*d1,-4.269*d1])sphere(r=r1);
translate(v=[ 2.864*d1, 0.856*d1,-3.871*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.864*d1, 0.856*d1,-3.871*d1])sphere(r=r1);
translate(v=[ 3.051*d1, 0.915*d1,-3.421*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.051*d1, 0.915*d1,-3.421*d1])sphere(r=r1);
translate(v=[ 3.221*d1, 0.968*d1,-2.908*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.221*d1, 0.968*d1,-2.908*d1])sphere(r=r1);
translate(v=[ 3.387*d1, 1.018*d1,-2.276*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.387*d1, 1.018*d1,-2.276*d1])sphere(r=r1);
translate(v=[ 3.586*d1, 1.069*d1,-1.344*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.586*d1, 1.069*d1,-1.344*d1])sphere(r=r1);
translate(v=[ 3.625*d1, 1.077*d1,-1.151*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.625*d1, 1.077*d1,-1.151*d1])sphere(r=r1);
translate(v=[ 3.644*d1, 1.073*d1,-1.135*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.644*d1, 1.073*d1,-1.135*d1])sphere(r=r1);
translate(v=[ 3.811*d1, 0.944*d1,-1.083*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.811*d1, 0.944*d1,-1.083*d1])sphere(r=r1);
translate(v=[ 3.941*d1, 0.824*d1,-1.071*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.941*d1, 0.824*d1,-1.071*d1])sphere(r=r1);
translate(v=[ 4.148*d1, 0.609*d1,-1.103*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.148*d1, 0.609*d1,-1.103*d1])sphere(r=r1);
translate(v=[ 4.293*d1, 0.433*d1,-1.146*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.293*d1, 0.433*d1,-1.146*d1])sphere(r=r1);
translate(v=[ 4.386*d1, 0.264*d1,-1.198*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.386*d1, 0.264*d1,-1.198*d1])sphere(r=r1);
translate(v=[ 4.430*d1, 0.107*d1,-1.240*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.430*d1, 0.107*d1,-1.240*d1])sphere(r=r1);
translate(v=[ 4.483*d1,-0.185*d1,-1.300*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.483*d1,-0.185*d1,-1.300*d1])sphere(r=r1);
translate(v=[ 4.482*d1,-0.339*d1,-1.152*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.482*d1,-0.339*d1,-1.152*d1])sphere(r=r1);
translate(v=[ 4.516*d1,-0.478*d1,-0.989*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.516*d1,-0.478*d1,-0.989*d1])sphere(r=r1);
translate(v=[ 4.584*d1,-0.603*d1,-0.809*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.584*d1,-0.603*d1,-0.809*d1])sphere(r=r1);
translate(v=[ 4.758*d1,-0.791*d1,-0.469*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.758*d1,-0.791*d1,-0.469*d1])sphere(r=r1);
translate(v=[ 4.838*d1,-0.966*d1,-0.245*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.838*d1,-0.966*d1,-0.245*d1])sphere(r=r1);
translate(v=[ 4.854*d1,-0.966*d1,-0.077*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.854*d1,-0.966*d1,-0.077*d1])sphere(r=r1);
translate(v=[ 4.877*d1,-0.939*d1, 0.082*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.877*d1,-0.939*d1, 0.082*d1])sphere(r=r1);
translate(v=[ 4.925*d1,-0.785*d1, 0.238*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.925*d1,-0.785*d1, 0.238*d1])sphere(r=r1);
translate(v=[ 4.994*d1,-0.655*d1, 0.358*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.994*d1,-0.655*d1, 0.358*d1])sphere(r=r1);
translate(v=[ 5.188*d1,-0.406*d1, 0.589*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.188*d1,-0.406*d1, 0.589*d1])sphere(r=r1);
translate(v=[ 5.321*d1,-0.248*d1, 0.788*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.321*d1,-0.248*d1, 0.788*d1])sphere(r=r1);
translate(v=[ 5.402*d1,-0.134*d1, 0.933*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.402*d1,-0.134*d1, 0.933*d1])sphere(r=r1);
translate(v=[ 5.462*d1, 0.008*d1, 0.973*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.462*d1, 0.008*d1, 0.973*d1])sphere(r=r1);
translate(v=[ 5.506*d1, 0.148*d1, 0.979*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.506*d1, 0.148*d1, 0.979*d1])sphere(r=r1);
translate(v=[ 5.597*d1, 0.327*d1, 0.792*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.597*d1, 0.327*d1, 0.792*d1])sphere(r=r1);
translate(v=[ 5.753*d1, 0.547*d1, 0.566*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.753*d1, 0.547*d1, 0.566*d1])sphere(r=r1);
translate(v=[ 5.853*d1, 0.743*d1, 0.407*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.853*d1, 0.743*d1, 0.407*d1])sphere(r=r1);
translate(v=[ 5.926*d1, 0.954*d1, 0.227*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.926*d1, 0.954*d1, 0.227*d1])sphere(r=r1);
translate(v=[ 5.953*d1, 1.082*d1, 0.095*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.953*d1, 1.082*d1, 0.095*d1])sphere(r=r1);
translate(v=[ 5.990*d1, 1.097*d1,-0.214*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.990*d1, 1.097*d1,-0.214*d1])sphere(r=r1);
translate(v=[ 6.056*d1, 0.934*d1,-0.407*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.056*d1, 0.934*d1,-0.407*d1])sphere(r=r1);
translate(v=[ 6.156*d1, 0.773*d1,-0.589*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.156*d1, 0.773*d1,-0.589*d1])sphere(r=r1);
translate(v=[ 6.310*d1, 0.568*d1,-0.805*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.310*d1, 0.568*d1,-0.805*d1])sphere(r=r1);
translate(v=[ 6.434*d1, 0.375*d1,-0.954*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.434*d1, 0.375*d1,-0.954*d1])sphere(r=r1);
translate(v=[ 6.525*d1, 0.177*d1,-1.080*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.525*d1, 0.177*d1,-1.080*d1])sphere(r=r1);
translate(v=[ 6.548*d1, 0.104*d1,-1.123*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.548*d1, 0.104*d1,-1.123*d1])sphere(r=r1);
translate(v=[ 6.630*d1,-0.165*d1,-1.095*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.630*d1,-0.165*d1,-1.095*d1])sphere(r=r1);
translate(v=[ 6.740*d1,-0.356*d1,-0.896*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.740*d1,-0.356*d1,-0.896*d1])sphere(r=r1);
translate(v=[ 6.889*d1,-0.581*d1,-0.602*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.889*d1,-0.581*d1,-0.602*d1])sphere(r=r1);
translate(v=[ 7.105*d1,-0.841*d1,-0.274*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.105*d1,-0.841*d1,-0.274*d1])sphere(r=r1);
translate(v=[ 7.174*d1,-0.916*d1,-0.142*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.174*d1,-0.916*d1,-0.142*d1])sphere(r=r1);
translate(v=[ 7.256*d1,-0.883*d1, 0.040*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.256*d1,-0.883*d1, 0.040*d1])sphere(r=r1);
translate(v=[ 7.315*d1,-0.874*d1, 0.148*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.315*d1,-0.874*d1, 0.148*d1])sphere(r=r1);
translate(v=[ 7.365*d1,-0.842*d1, 0.215*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.365*d1,-0.842*d1, 0.215*d1])sphere(r=r1);
translate(v=[ 7.564*d1,-0.775*d1, 0.459*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.564*d1,-0.775*d1, 0.459*d1])sphere(r=r1);
translate(v=[ 7.739*d1,-0.698*d1, 0.637*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.739*d1,-0.698*d1, 0.637*d1])sphere(r=r1);
translate(v=[ 7.904*d1,-0.595*d1, 0.787*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.904*d1,-0.595*d1, 0.787*d1])sphere(r=r1);
translate(v=[ 8.056*d1,-0.467*d1, 0.907*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.056*d1,-0.467*d1, 0.907*d1])sphere(r=r1);
translate(v=[ 8.172*d1,-0.330*d1, 0.994*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.172*d1,-0.330*d1, 0.994*d1])sphere(r=r1);
translate(v=[ 8.240*d1,-0.205*d1, 1.060*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.240*d1,-0.205*d1, 1.060*d1])sphere(r=r1);
translate(v=[ 8.254*d1,-0.165*d1, 1.078*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.254*d1,-0.165*d1, 1.078*d1])sphere(r=r1);
translate(v=[ 8.295*d1,-0.032*d1, 1.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.295*d1,-0.032*d1, 1.096*d1])sphere(r=r1);
translate(v=[ 8.295*d1, 0.116*d1, 1.142*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.295*d1, 0.116*d1, 1.142*d1])sphere(r=r1);
translate(v=[ 8.292*d1, 0.164*d1, 1.155*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.292*d1, 0.164*d1, 1.155*d1])sphere(r=r1);
translate(v=[ 8.522*d1, 0.578*d1, 1.104*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.522*d1, 0.578*d1, 1.104*d1])sphere(r=r1);
translate(v=[ 8.625*d1, 0.817*d1, 1.048*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.625*d1, 0.817*d1, 1.048*d1])sphere(r=r1);
translate(v=[ 8.694*d1, 1.051*d1, 0.970*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.694*d1, 1.051*d1, 0.970*d1])sphere(r=r1);
translate(v=[ 8.735*d1, 1.279*d1, 0.867*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.735*d1, 1.279*d1, 0.867*d1])sphere(r=r1);
translate(v=[ 8.747*d1, 1.492*d1, 0.744*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.747*d1, 1.492*d1, 0.744*d1])sphere(r=r1);
translate(v=[ 8.734*d1, 1.651*d1, 0.638*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.734*d1, 1.651*d1, 0.638*d1])sphere(r=r1);
translate(v=[ 8.657*d1, 1.869*d1, 0.522*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.657*d1, 1.869*d1, 0.522*d1])sphere(r=r1);
translate(v=[ 8.557*d1, 2.052*d1, 0.405*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.557*d1, 2.052*d1, 0.405*d1])sphere(r=r1);
translate(v=[ 8.417*d1, 2.225*d1, 0.282*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.417*d1, 2.225*d1, 0.282*d1])sphere(r=r1);
translate(v=[ 8.304*d1, 2.321*d1, 0.218*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.304*d1, 2.321*d1, 0.218*d1])sphere(r=r1);
translate(v=[ 8.116*d1, 2.438*d1, 0.148*d1])sphere(r=r1);}
 hull(){
translate(v=[ 8.116*d1, 2.438*d1, 0.148*d1])sphere(r=r1);
translate(v=[ 7.887*d1, 2.542*d1, 0.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.887*d1, 2.542*d1, 0.096*d1])sphere(r=r1);
translate(v=[ 7.591*d1, 2.630*d1, 0.058*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.591*d1, 2.630*d1, 0.058*d1])sphere(r=r1);
translate(v=[ 7.484*d1, 2.667*d1, 0.049*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.484*d1, 2.667*d1, 0.049*d1])sphere(r=r1);
translate(v=[ 7.461*d1, 2.682*d1, 0.048*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.461*d1, 2.682*d1, 0.048*d1])sphere(r=r1);
translate(v=[ 7.208*d1, 3.160*d1, 0.042*d1])sphere(r=r1);}
 hull(){
translate(v=[ 7.208*d1, 3.160*d1, 0.042*d1])sphere(r=r1);
translate(v=[ 6.979*d1, 3.522*d1, 0.039*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.979*d1, 3.522*d1, 0.039*d1])sphere(r=r1);
translate(v=[ 6.710*d1, 3.878*d1, 0.035*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.710*d1, 3.878*d1, 0.035*d1])sphere(r=r1);
translate(v=[ 6.442*d1, 4.179*d1, 0.032*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.442*d1, 4.179*d1, 0.032*d1])sphere(r=r1);
translate(v=[ 6.147*d1, 4.463*d1, 0.030*d1])sphere(r=r1);}
 hull(){
translate(v=[ 6.147*d1, 4.463*d1, 0.030*d1])sphere(r=r1);
translate(v=[ 5.828*d1, 4.726*d1, 0.027*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.828*d1, 4.726*d1, 0.027*d1])sphere(r=r1);
translate(v=[ 5.443*d1, 4.996*d1, 0.025*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.443*d1, 4.996*d1, 0.025*d1])sphere(r=r1);
translate(v=[ 5.042*d1, 5.231*d1, 0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[ 5.042*d1, 5.231*d1, 0.022*d1])sphere(r=r1);
translate(v=[ 4.633*d1, 5.430*d1, 0.020*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.633*d1, 5.430*d1, 0.020*d1])sphere(r=r1);
translate(v=[ 4.173*d1, 5.613*d1, 0.018*d1])sphere(r=r1);}
 hull(){
translate(v=[ 4.173*d1, 5.613*d1, 0.018*d1])sphere(r=r1);
translate(v=[ 3.671*d1, 5.772*d1, 0.016*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.671*d1, 5.772*d1, 0.016*d1])sphere(r=r1);
translate(v=[ 3.136*d1, 5.902*d1, 0.014*d1])sphere(r=r1);}
 hull(){
translate(v=[ 3.136*d1, 5.902*d1, 0.014*d1])sphere(r=r1);
translate(v=[ 2.527*d1, 6.008*d1, 0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[ 2.527*d1, 6.008*d1, 0.011*d1])sphere(r=r1);
translate(v=[ 1.772*d1, 6.096*d1, 0.008*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.772*d1, 6.096*d1, 0.008*d1])sphere(r=r1);
translate(v=[ 0.772*d1, 6.173*d1, 0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.772*d1, 6.173*d1, 0.003*d1])sphere(r=r1);
translate(v=[ 0.021*d1, 6.224*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.021*d1, 6.224*d1, 0.000*d1])sphere(r=r1);
translate(v=[-0.021*d1, 6.241*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.021*d1, 6.241*d1, 0.000*d1])sphere(r=r1);
translate(v=[-0.375*d1, 6.242*d1,-0.001*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.375*d1, 6.242*d1,-0.001*d1])sphere(r=r1);
translate(v=[-0.695*d1, 6.209*d1,-0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.695*d1, 6.209*d1,-0.003*d1])sphere(r=r1);
translate(v=[-1.014*d1, 6.143*d1,-0.004*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.014*d1, 6.143*d1,-0.004*d1])sphere(r=r1);
translate(v=[-1.328*d1, 6.044*d1,-0.006*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.328*d1, 6.044*d1,-0.006*d1])sphere(r=r1);
translate(v=[-1.671*d1, 5.895*d1,-0.007*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.671*d1, 5.895*d1,-0.007*d1])sphere(r=r1);
translate(v=[-1.999*d1, 5.710*d1,-0.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.999*d1, 5.710*d1,-0.009*d1])sphere(r=r1);
translate(v=[-2.310*d1, 5.493*d1,-0.010*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.310*d1, 5.493*d1,-0.010*d1])sphere(r=r1);
translate(v=[-2.634*d1, 5.220*d1,-0.012*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.634*d1, 5.220*d1,-0.012*d1])sphere(r=r1);
translate(v=[-2.934*d1, 4.919*d1,-0.013*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.934*d1, 4.919*d1,-0.013*d1])sphere(r=r1);
translate(v=[-3.236*d1, 4.559*d1,-0.014*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.236*d1, 4.559*d1,-0.014*d1])sphere(r=r1);
translate(v=[-3.509*d1, 4.175*d1,-0.015*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.509*d1, 4.175*d1,-0.015*d1])sphere(r=r1);
translate(v=[-3.773*d1, 3.739*d1,-0.017*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.773*d1, 3.739*d1,-0.017*d1])sphere(r=r1);
translate(v=[-4.021*d1, 3.260*d1,-0.019*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.021*d1, 3.260*d1,-0.019*d1])sphere(r=r1);
translate(v=[-4.258*d1, 2.718*d1,-0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.258*d1, 2.718*d1,-0.022*d1])sphere(r=r1);
translate(v=[-4.469*d1, 2.140*d1,-0.025*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.469*d1, 2.140*d1,-0.025*d1])sphere(r=r1);
translate(v=[-4.607*d1, 1.681*d1,-0.029*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.607*d1, 1.681*d1,-0.029*d1])sphere(r=r1);
translate(v=[-4.605*d1, 1.641*d1,-0.030*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.605*d1, 1.641*d1,-0.030*d1])sphere(r=r1);
translate(v=[-4.432*d1, 1.392*d1,-0.063*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.432*d1, 1.392*d1,-0.063*d1])sphere(r=r1);
translate(v=[-4.348*d1, 1.239*d1,-0.104*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.348*d1, 1.239*d1,-0.104*d1])sphere(r=r1);
translate(v=[-4.303*d1, 1.118*d1,-0.155*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.303*d1, 1.118*d1,-0.155*d1])sphere(r=r1);
translate(v=[-4.273*d1, 0.930*d1,-0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.273*d1, 0.930*d1,-0.254*d1])sphere(r=r1);
translate(v=[-4.275*d1, 0.784*d1,-0.327*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.275*d1, 0.784*d1,-0.327*d1])sphere(r=r1);
translate(v=[-4.319*d1, 0.611*d1,-0.440*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.319*d1, 0.611*d1,-0.440*d1])sphere(r=r1);
translate(v=[-4.393*d1, 0.430*d1,-0.529*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.393*d1, 0.430*d1,-0.529*d1])sphere(r=r1);
translate(v=[-4.503*d1, 0.239*d1,-0.598*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.503*d1, 0.239*d1,-0.598*d1])sphere(r=r1);
translate(v=[-4.595*d1, 0.081*d1,-0.639*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.595*d1, 0.081*d1,-0.639*d1])sphere(r=r1);
translate(v=[-4.606*d1,-0.032*d1,-0.606*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.606*d1,-0.032*d1,-0.606*d1])sphere(r=r1);
translate(v=[-4.633*d1,-0.111*d1,-0.599*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.633*d1,-0.111*d1,-0.599*d1])sphere(r=r1);
translate(v=[-4.707*d1,-0.230*d1,-0.553*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.707*d1,-0.230*d1,-0.553*d1])sphere(r=r1);
translate(v=[-4.830*d1,-0.356*d1,-0.488*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.830*d1,-0.356*d1,-0.488*d1])sphere(r=r1);
translate(v=[-4.968*d1,-0.462*d1,-0.389*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.968*d1,-0.462*d1,-0.389*d1])sphere(r=r1);
translate(v=[-5.115*d1,-0.546*d1,-0.256*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.115*d1,-0.546*d1,-0.256*d1])sphere(r=r1);
translate(v=[-5.226*d1,-0.616*d1,-0.117*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.226*d1,-0.616*d1,-0.117*d1])sphere(r=r1);
translate(v=[-5.242*d1,-0.630*d1,-0.091*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.242*d1,-0.630*d1,-0.091*d1])sphere(r=r1);
translate(v=[-5.314*d1,-0.668*d1, 0.065*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.314*d1,-0.668*d1, 0.065*d1])sphere(r=r1);
translate(v=[-5.329*d1,-0.679*d1, 0.115*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.329*d1,-0.679*d1, 0.115*d1])sphere(r=r1);
translate(v=[-5.434*d1,-0.595*d1, 0.284*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.434*d1,-0.595*d1, 0.284*d1])sphere(r=r1);
translate(v=[-5.552*d1,-0.474*d1, 0.477*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.552*d1,-0.474*d1, 0.477*d1])sphere(r=r1);
translate(v=[-5.626*d1,-0.354*d1, 0.671*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.626*d1,-0.354*d1, 0.671*d1])sphere(r=r1);
translate(v=[-5.693*d1,-0.169*d1, 0.913*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.693*d1,-0.169*d1, 0.913*d1])sphere(r=r1);
translate(v=[-5.703*d1,-0.133*d1, 0.944*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.703*d1,-0.133*d1, 0.944*d1])sphere(r=r1);
translate(v=[-5.757*d1, 0.072*d1, 0.986*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.757*d1, 0.072*d1, 0.986*d1])sphere(r=r1);
translate(v=[-5.765*d1, 0.105*d1, 0.986*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.765*d1, 0.105*d1, 0.986*d1])sphere(r=r1);
translate(v=[-5.907*d1, 0.376*d1, 0.857*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.907*d1, 0.376*d1, 0.857*d1])sphere(r=r1);
translate(v=[-6.037*d1, 0.583*d1, 0.739*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.037*d1, 0.583*d1, 0.739*d1])sphere(r=r1);
translate(v=[-6.165*d1, 0.789*d1, 0.576*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.165*d1, 0.789*d1, 0.576*d1])sphere(r=r1);
translate(v=[-6.231*d1, 0.939*d1, 0.441*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.231*d1, 0.939*d1, 0.441*d1])sphere(r=r1);
translate(v=[-6.264*d1, 1.098*d1, 0.282*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.264*d1, 1.098*d1, 0.282*d1])sphere(r=r1);
translate(v=[-6.268*d1, 1.148*d1, 0.217*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.268*d1, 1.148*d1, 0.217*d1])sphere(r=r1);
translate(v=[-6.309*d1, 1.151*d1,-0.053*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.309*d1, 1.151*d1,-0.053*d1])sphere(r=r1);
translate(v=[-6.317*d1, 1.145*d1,-0.110*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.317*d1, 1.145*d1,-0.110*d1])sphere(r=r1);
translate(v=[-6.431*d1, 0.939*d1,-0.337*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.431*d1, 0.939*d1,-0.337*d1])sphere(r=r1);
translate(v=[-6.640*d1, 0.614*d1,-0.671*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.640*d1, 0.614*d1,-0.671*d1])sphere(r=r1);
translate(v=[-6.757*d1, 0.442*d1,-0.897*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.757*d1, 0.442*d1,-0.897*d1])sphere(r=r1);
translate(v=[-6.812*d1, 0.306*d1,-1.075*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.812*d1, 0.306*d1,-1.075*d1])sphere(r=r1);
translate(v=[-6.836*d1, 0.178*d1,-1.217*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.836*d1, 0.178*d1,-1.217*d1])sphere(r=r1);
translate(v=[-6.892*d1, 0.010*d1,-1.228*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.892*d1, 0.010*d1,-1.228*d1])sphere(r=r1);
translate(v=[-6.973*d1,-0.163*d1,-1.207*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.973*d1,-0.163*d1,-1.207*d1])sphere(r=r1);
translate(v=[-6.994*d1,-0.194*d1,-1.193*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.994*d1,-0.194*d1,-1.193*d1])sphere(r=r1);
translate(v=[-7.298*d1,-0.516*d1,-0.882*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.298*d1,-0.516*d1,-0.882*d1])sphere(r=r1);
translate(v=[-7.460*d1,-0.733*d1,-0.721*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.460*d1,-0.733*d1,-0.721*d1])sphere(r=r1);
translate(v=[-7.584*d1,-0.946*d1,-0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.584*d1,-0.946*d1,-0.581*d1])sphere(r=r1);
translate(v=[-7.650*d1,-1.114*d1,-0.462*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.650*d1,-1.114*d1,-0.462*d1])sphere(r=r1);
translate(v=[-7.683*d1,-1.294*d1,-0.309*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.683*d1,-1.294*d1,-0.309*d1])sphere(r=r1);
translate(v=[-7.681*d1,-1.457*d1,-0.151*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.681*d1,-1.457*d1,-0.151*d1])sphere(r=r1);
translate(v=[-7.679*d1,-1.485*d1,-0.111*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.679*d1,-1.485*d1,-0.111*d1])sphere(r=r1);
translate(v=[-7.696*d1,-1.530*d1, 0.108*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.696*d1,-1.530*d1, 0.108*d1])sphere(r=r1);
translate(v=[-7.699*d1,-1.541*d1, 0.320*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.699*d1,-1.541*d1, 0.320*d1])sphere(r=r1);
translate(v=[-7.703*d1,-1.535*d1, 0.394*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.703*d1,-1.535*d1, 0.394*d1])sphere(r=r1);
translate(v=[-7.880*d1,-1.296*d1, 0.800*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.880*d1,-1.296*d1, 0.800*d1])sphere(r=r1);
translate(v=[-7.976*d1,-1.208*d1, 1.043*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.976*d1,-1.208*d1, 1.043*d1])sphere(r=r1);
translate(v=[-8.059*d1,-1.107*d1, 1.324*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.059*d1,-1.107*d1, 1.324*d1])sphere(r=r1);
translate(v=[-8.104*d1,-0.997*d1, 1.557*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.104*d1,-0.997*d1, 1.557*d1])sphere(r=r1);
translate(v=[-8.121*d1,-0.869*d1, 1.765*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.121*d1,-0.869*d1, 1.765*d1])sphere(r=r1);
translate(v=[-8.110*d1,-0.722*d1, 1.957*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.110*d1,-0.722*d1, 1.957*d1])sphere(r=r1);
translate(v=[-8.071*d1,-0.560*d1, 2.128*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.071*d1,-0.560*d1, 2.128*d1])sphere(r=r1);
translate(v=[-8.003*d1,-0.382*d1, 2.278*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.003*d1,-0.382*d1, 2.278*d1])sphere(r=r1);
translate(v=[-7.980*d1,-0.330*d1, 2.315*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.980*d1,-0.330*d1, 2.315*d1])sphere(r=r1);
translate(v=[-8.062*d1,-0.073*d1, 2.307*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.062*d1,-0.073*d1, 2.307*d1])sphere(r=r1);
translate(v=[-8.180*d1, 0.399*d1, 2.251*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.180*d1, 0.399*d1, 2.251*d1])sphere(r=r1);
translate(v=[-8.289*d1, 0.674*d1, 2.234*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.289*d1, 0.674*d1, 2.234*d1])sphere(r=r1);
translate(v=[-8.430*d1, 0.974*d1, 2.242*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.430*d1, 0.974*d1, 2.242*d1])sphere(r=r1);
translate(v=[-8.645*d1, 1.414*d1, 2.305*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.645*d1, 1.414*d1, 2.305*d1])sphere(r=r1);
translate(v=[-8.790*d1, 1.764*d1, 2.376*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.790*d1, 1.764*d1, 2.376*d1])sphere(r=r1);
translate(v=[-8.870*d1, 2.004*d1, 2.447*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.870*d1, 2.004*d1, 2.447*d1])sphere(r=r1);
translate(v=[-8.931*d1, 2.241*d1, 2.551*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.931*d1, 2.241*d1, 2.551*d1])sphere(r=r1);
translate(v=[-8.983*d1, 2.509*d1, 2.707*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.983*d1, 2.509*d1, 2.707*d1])sphere(r=r1);
translate(v=[-9.009*d1, 2.668*d1, 2.817*d1])sphere(r=r1);}
 hull(){
translate(v=[-9.009*d1, 2.668*d1, 2.817*d1])sphere(r=r1);
translate(v=[-9.011*d1, 2.676*d1, 2.862*d1])sphere(r=r1);}
 hull(){
translate(v=[-9.011*d1, 2.676*d1, 2.862*d1])sphere(r=r1);
translate(v=[-8.836*d1, 2.632*d1, 3.253*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.836*d1, 2.632*d1, 3.253*d1])sphere(r=r1);
translate(v=[-8.623*d1, 2.575*d1, 3.637*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.623*d1, 2.575*d1, 3.637*d1])sphere(r=r1);
translate(v=[-8.375*d1, 2.506*d1, 4.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.375*d1, 2.506*d1, 4.009*d1])sphere(r=r1);
translate(v=[-8.093*d1, 2.426*d1, 4.362*d1])sphere(r=r1);}
 hull(){
translate(v=[-8.093*d1, 2.426*d1, 4.362*d1])sphere(r=r1);
translate(v=[-7.779*d1, 2.335*d1, 4.693*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.779*d1, 2.335*d1, 4.693*d1])sphere(r=r1);
translate(v=[-7.438*d1, 2.235*d1, 4.998*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.438*d1, 2.235*d1, 4.998*d1])sphere(r=r1);
translate(v=[-7.072*d1, 2.126*d1, 5.275*d1])sphere(r=r1);}
 hull(){
translate(v=[-7.072*d1, 2.126*d1, 5.275*d1])sphere(r=r1);
translate(v=[-6.684*d1, 2.010*d1, 5.522*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.684*d1, 2.010*d1, 5.522*d1])sphere(r=r1);
translate(v=[-6.278*d1, 1.887*d1, 5.738*d1])sphere(r=r1);}
 hull(){
translate(v=[-6.278*d1, 1.887*d1, 5.738*d1])sphere(r=r1);
translate(v=[-5.857*d1, 1.759*d1, 5.925*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.857*d1, 1.759*d1, 5.925*d1])sphere(r=r1);
translate(v=[-5.369*d1, 1.611*d1, 6.099*d1])sphere(r=r1);}
 hull(){
translate(v=[-5.369*d1, 1.611*d1, 6.099*d1])sphere(r=r1);
translate(v=[-4.873*d1, 1.459*d1, 6.237*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.873*d1, 1.459*d1, 6.237*d1])sphere(r=r1);
translate(v=[-4.373*d1, 1.305*d1, 6.340*d1])sphere(r=r1);}
 hull(){
translate(v=[-4.373*d1, 1.305*d1, 6.340*d1])sphere(r=r1);
translate(v=[-3.819*d1, 1.135*d1, 6.417*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.819*d1, 1.135*d1, 6.417*d1])sphere(r=r1);
translate(v=[-3.220*d1, 0.952*d1, 6.462*d1])sphere(r=r1);}
 hull(){
translate(v=[-3.220*d1, 0.952*d1, 6.462*d1])sphere(r=r1);
translate(v=[-2.586*d1, 0.758*d1, 6.472*d1])sphere(r=r1);}
 hull(){
translate(v=[-2.586*d1, 0.758*d1, 6.472*d1])sphere(r=r1);
translate(v=[-1.887*d1, 0.547*d1, 6.445*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.887*d1, 0.547*d1, 6.445*d1])sphere(r=r1);
translate(v=[-1.110*d1, 0.317*d1, 6.373*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.110*d1, 0.317*d1, 6.373*d1])sphere(r=r1);
translate(v=[-0.207*d1, 0.058*d1, 6.249*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.207*d1, 0.058*d1, 6.249*d1])sphere(r=r1);
translate(v=[-0.034*d1, 0.009*d1, 6.221*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.034*d1, 0.009*d1, 6.221*d1])sphere(r=r1);
translate(v=[ 0.034*d1,-0.009*d1, 6.244*d1])sphere(r=r1);}
