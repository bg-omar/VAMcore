 //% Knot 4_1rid4
 //%mns=100
 //%+RID4
 //%process with  doknotscad.rid4
 //% adjusted with knotadjust.ri.f
 //%0  1  0
 //% shortened with knotshorten.f
// make with infill 80%, support angle 10 deg
r1 = 3;  d1 = 10;
// Path length     23.42*d1
// tube diameter 2*r1, closest approach d1-2*r1
 hull(){
translate(v=[ 0.003*d1,-0.001*d1, 1.303*d1])sphere(r=r1);
translate(v=[ 0.087*d1,-0.032*d1, 1.357*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.087*d1,-0.032*d1, 1.357*d1])sphere(r=r1);
translate(v=[ 0.319*d1,-0.118*d1, 1.457*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.319*d1,-0.118*d1, 1.457*d1])sphere(r=r1);
translate(v=[ 0.535*d1,-0.198*d1, 1.506*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.535*d1,-0.198*d1, 1.506*d1])sphere(r=r1);
translate(v=[ 0.713*d1,-0.267*d1, 1.513*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.713*d1,-0.267*d1, 1.513*d1])sphere(r=r1);
translate(v=[ 0.787*d1,-0.306*d1, 1.505*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.787*d1,-0.306*d1, 1.505*d1])sphere(r=r1);
translate(v=[ 0.888*d1,-0.477*d1, 1.468*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.888*d1,-0.477*d1, 1.468*d1])sphere(r=r1);
translate(v=[ 0.986*d1,-0.623*d1, 1.401*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.986*d1,-0.623*d1, 1.401*d1])sphere(r=r1);
translate(v=[ 1.082*d1,-0.748*d1, 1.306*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.082*d1,-0.748*d1, 1.306*d1])sphere(r=r1);
translate(v=[ 1.192*d1,-0.870*d1, 1.164*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.192*d1,-0.870*d1, 1.164*d1])sphere(r=r1);
translate(v=[ 1.287*d1,-0.957*d1, 1.014*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.287*d1,-0.957*d1, 1.014*d1])sphere(r=r1);
translate(v=[ 1.364*d1,-1.009*d1, 0.846*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.364*d1,-1.009*d1, 0.846*d1])sphere(r=r1);
translate(v=[ 1.418*d1,-1.031*d1, 0.684*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.418*d1,-1.031*d1, 0.684*d1])sphere(r=r1);
translate(v=[ 1.460*d1,-1.025*d1, 0.493*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.460*d1,-1.025*d1, 0.493*d1])sphere(r=r1);
translate(v=[ 1.475*d1,-0.992*d1, 0.321*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.475*d1,-0.992*d1, 0.321*d1])sphere(r=r1);
translate(v=[ 1.471*d1,-0.938*d1, 0.158*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.471*d1,-0.938*d1, 0.158*d1])sphere(r=r1);
translate(v=[ 1.445*d1,-0.850*d1,-0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.445*d1,-0.850*d1,-0.003*d1])sphere(r=r1);
translate(v=[ 1.401*d1,-0.745*d1,-0.132*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.401*d1,-0.745*d1,-0.132*d1])sphere(r=r1);
translate(v=[ 1.338*d1,-0.620*d1,-0.233*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.338*d1,-0.620*d1,-0.233*d1])sphere(r=r1);
translate(v=[ 1.198*d1,-0.386*d1,-0.365*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.198*d1,-0.386*d1,-0.365*d1])sphere(r=r1);
translate(v=[ 1.094*d1,-0.257*d1,-0.435*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.094*d1,-0.257*d1,-0.435*d1])sphere(r=r1);
translate(v=[ 0.949*d1,-0.105*d1,-0.493*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.949*d1,-0.105*d1,-0.493*d1])sphere(r=r1);
translate(v=[ 0.830*d1, 0.057*d1,-0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.830*d1, 0.057*d1,-0.516*d1])sphere(r=r1);
translate(v=[ 0.715*d1, 0.254*d1,-0.505*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.715*d1, 0.254*d1,-0.505*d1])sphere(r=r1);
translate(v=[ 0.623*d1, 0.438*d1,-0.463*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.623*d1, 0.438*d1,-0.463*d1])sphere(r=r1);
translate(v=[ 0.552*d1, 0.600*d1,-0.394*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.552*d1, 0.600*d1,-0.394*d1])sphere(r=r1);
translate(v=[ 0.491*d1, 0.740*d1,-0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.491*d1, 0.740*d1,-0.295*d1])sphere(r=r1);
translate(v=[ 0.442*d1, 0.863*d1,-0.169*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.442*d1, 0.863*d1,-0.169*d1])sphere(r=r1);
translate(v=[ 0.260*d1, 1.082*d1,-0.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.260*d1, 1.082*d1,-0.096*d1])sphere(r=r1);
translate(v=[ 0.097*d1, 1.227*d1,-0.036*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.097*d1, 1.227*d1,-0.036*d1])sphere(r=r1);
translate(v=[-0.058*d1, 1.342*d1, 0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.058*d1, 1.342*d1, 0.022*d1])sphere(r=r1);
translate(v=[-0.286*d1, 1.445*d1, 0.105*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.286*d1, 1.445*d1, 0.105*d1])sphere(r=r1);
translate(v=[-0.497*d1, 1.500*d1, 0.183*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.497*d1, 1.500*d1, 0.183*d1])sphere(r=r1);
translate(v=[-0.683*d1, 1.515*d1, 0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.683*d1, 1.515*d1, 0.254*d1])sphere(r=r1);
translate(v=[-0.787*d1, 1.505*d1, 0.306*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.787*d1, 1.505*d1, 0.306*d1])sphere(r=r1);
translate(v=[-0.888*d1, 1.468*d1, 0.477*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.888*d1, 1.468*d1, 0.477*d1])sphere(r=r1);
translate(v=[-0.986*d1, 1.401*d1, 0.623*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.986*d1, 1.401*d1, 0.623*d1])sphere(r=r1);
translate(v=[-1.082*d1, 1.306*d1, 0.748*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.082*d1, 1.306*d1, 0.748*d1])sphere(r=r1);
translate(v=[-1.192*d1, 1.164*d1, 0.870*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.192*d1, 1.164*d1, 0.870*d1])sphere(r=r1);
translate(v=[-1.287*d1, 1.014*d1, 0.957*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.287*d1, 1.014*d1, 0.957*d1])sphere(r=r1);
translate(v=[-1.364*d1, 0.846*d1, 1.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.364*d1, 0.846*d1, 1.009*d1])sphere(r=r1);
translate(v=[-1.418*d1, 0.684*d1, 1.031*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.418*d1, 0.684*d1, 1.031*d1])sphere(r=r1);
translate(v=[-1.460*d1, 0.493*d1, 1.025*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.460*d1, 0.493*d1, 1.025*d1])sphere(r=r1);
translate(v=[-1.475*d1, 0.321*d1, 0.992*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.475*d1, 0.321*d1, 0.992*d1])sphere(r=r1);
translate(v=[-1.471*d1, 0.158*d1, 0.938*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.471*d1, 0.158*d1, 0.938*d1])sphere(r=r1);
translate(v=[-1.445*d1,-0.003*d1, 0.850*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.445*d1,-0.003*d1, 0.850*d1])sphere(r=r1);
translate(v=[-1.401*d1,-0.132*d1, 0.745*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.401*d1,-0.132*d1, 0.745*d1])sphere(r=r1);
translate(v=[-1.338*d1,-0.233*d1, 0.620*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.338*d1,-0.233*d1, 0.620*d1])sphere(r=r1);
translate(v=[-1.198*d1,-0.365*d1, 0.386*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.198*d1,-0.365*d1, 0.386*d1])sphere(r=r1);
translate(v=[-1.094*d1,-0.435*d1, 0.257*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.094*d1,-0.435*d1, 0.257*d1])sphere(r=r1);
translate(v=[-0.949*d1,-0.493*d1, 0.105*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.949*d1,-0.493*d1, 0.105*d1])sphere(r=r1);
translate(v=[-0.830*d1,-0.516*d1,-0.057*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.830*d1,-0.516*d1,-0.057*d1])sphere(r=r1);
translate(v=[-0.715*d1,-0.505*d1,-0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.715*d1,-0.505*d1,-0.254*d1])sphere(r=r1);
translate(v=[-0.623*d1,-0.463*d1,-0.438*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.623*d1,-0.463*d1,-0.438*d1])sphere(r=r1);
translate(v=[-0.552*d1,-0.394*d1,-0.600*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.552*d1,-0.394*d1,-0.600*d1])sphere(r=r1);
translate(v=[-0.491*d1,-0.295*d1,-0.740*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.491*d1,-0.295*d1,-0.740*d1])sphere(r=r1);
translate(v=[-0.442*d1,-0.169*d1,-0.863*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.442*d1,-0.169*d1,-0.863*d1])sphere(r=r1);
translate(v=[-0.260*d1,-0.096*d1,-1.082*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.260*d1,-0.096*d1,-1.082*d1])sphere(r=r1);
translate(v=[-0.097*d1,-0.036*d1,-1.227*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.097*d1,-0.036*d1,-1.227*d1])sphere(r=r1);
translate(v=[ 0.058*d1, 0.022*d1,-1.342*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.058*d1, 0.022*d1,-1.342*d1])sphere(r=r1);
translate(v=[ 0.286*d1, 0.105*d1,-1.445*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.286*d1, 0.105*d1,-1.445*d1])sphere(r=r1);
translate(v=[ 0.497*d1, 0.183*d1,-1.500*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.497*d1, 0.183*d1,-1.500*d1])sphere(r=r1);
translate(v=[ 0.683*d1, 0.254*d1,-1.515*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.683*d1, 0.254*d1,-1.515*d1])sphere(r=r1);
translate(v=[ 0.787*d1, 0.306*d1,-1.505*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.787*d1, 0.306*d1,-1.505*d1])sphere(r=r1);
translate(v=[ 0.888*d1, 0.477*d1,-1.468*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.888*d1, 0.477*d1,-1.468*d1])sphere(r=r1);
translate(v=[ 0.986*d1, 0.623*d1,-1.401*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.986*d1, 0.623*d1,-1.401*d1])sphere(r=r1);
translate(v=[ 1.082*d1, 0.748*d1,-1.306*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.082*d1, 0.748*d1,-1.306*d1])sphere(r=r1);
translate(v=[ 1.192*d1, 0.870*d1,-1.164*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.192*d1, 0.870*d1,-1.164*d1])sphere(r=r1);
translate(v=[ 1.287*d1, 0.957*d1,-1.014*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.287*d1, 0.957*d1,-1.014*d1])sphere(r=r1);
translate(v=[ 1.364*d1, 1.009*d1,-0.846*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.364*d1, 1.009*d1,-0.846*d1])sphere(r=r1);
translate(v=[ 1.418*d1, 1.031*d1,-0.684*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.418*d1, 1.031*d1,-0.684*d1])sphere(r=r1);
translate(v=[ 1.460*d1, 1.025*d1,-0.493*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.460*d1, 1.025*d1,-0.493*d1])sphere(r=r1);
translate(v=[ 1.475*d1, 0.992*d1,-0.321*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.475*d1, 0.992*d1,-0.321*d1])sphere(r=r1);
translate(v=[ 1.471*d1, 0.938*d1,-0.158*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.471*d1, 0.938*d1,-0.158*d1])sphere(r=r1);
translate(v=[ 1.445*d1, 0.850*d1, 0.003*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.445*d1, 0.850*d1, 0.003*d1])sphere(r=r1);
translate(v=[ 1.401*d1, 0.745*d1, 0.132*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.401*d1, 0.745*d1, 0.132*d1])sphere(r=r1);
translate(v=[ 1.338*d1, 0.620*d1, 0.233*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.338*d1, 0.620*d1, 0.233*d1])sphere(r=r1);
translate(v=[ 1.198*d1, 0.386*d1, 0.365*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.198*d1, 0.386*d1, 0.365*d1])sphere(r=r1);
translate(v=[ 1.094*d1, 0.257*d1, 0.435*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.094*d1, 0.257*d1, 0.435*d1])sphere(r=r1);
translate(v=[ 0.949*d1, 0.105*d1, 0.493*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.949*d1, 0.105*d1, 0.493*d1])sphere(r=r1);
translate(v=[ 0.830*d1,-0.057*d1, 0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.830*d1,-0.057*d1, 0.516*d1])sphere(r=r1);
translate(v=[ 0.715*d1,-0.254*d1, 0.505*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.715*d1,-0.254*d1, 0.505*d1])sphere(r=r1);
translate(v=[ 0.623*d1,-0.438*d1, 0.463*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.623*d1,-0.438*d1, 0.463*d1])sphere(r=r1);
translate(v=[ 0.552*d1,-0.600*d1, 0.394*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.552*d1,-0.600*d1, 0.394*d1])sphere(r=r1);
translate(v=[ 0.491*d1,-0.740*d1, 0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.491*d1,-0.740*d1, 0.295*d1])sphere(r=r1);
translate(v=[ 0.442*d1,-0.863*d1, 0.169*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.442*d1,-0.863*d1, 0.169*d1])sphere(r=r1);
translate(v=[ 0.260*d1,-1.082*d1, 0.096*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.260*d1,-1.082*d1, 0.096*d1])sphere(r=r1);
translate(v=[ 0.097*d1,-1.227*d1, 0.036*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.097*d1,-1.227*d1, 0.036*d1])sphere(r=r1);
translate(v=[-0.058*d1,-1.342*d1,-0.022*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.058*d1,-1.342*d1,-0.022*d1])sphere(r=r1);
translate(v=[-0.286*d1,-1.445*d1,-0.105*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.286*d1,-1.445*d1,-0.105*d1])sphere(r=r1);
translate(v=[-0.497*d1,-1.500*d1,-0.183*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.497*d1,-1.500*d1,-0.183*d1])sphere(r=r1);
translate(v=[-0.683*d1,-1.515*d1,-0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.683*d1,-1.515*d1,-0.254*d1])sphere(r=r1);
translate(v=[-0.787*d1,-1.505*d1,-0.306*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.787*d1,-1.505*d1,-0.306*d1])sphere(r=r1);
translate(v=[-0.888*d1,-1.468*d1,-0.477*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.888*d1,-1.468*d1,-0.477*d1])sphere(r=r1);
translate(v=[-0.986*d1,-1.401*d1,-0.623*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.986*d1,-1.401*d1,-0.623*d1])sphere(r=r1);
translate(v=[-1.082*d1,-1.306*d1,-0.748*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.082*d1,-1.306*d1,-0.748*d1])sphere(r=r1);
translate(v=[-1.192*d1,-1.164*d1,-0.870*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.192*d1,-1.164*d1,-0.870*d1])sphere(r=r1);
translate(v=[-1.287*d1,-1.014*d1,-0.957*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.287*d1,-1.014*d1,-0.957*d1])sphere(r=r1);
translate(v=[-1.364*d1,-0.846*d1,-1.009*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.364*d1,-0.846*d1,-1.009*d1])sphere(r=r1);
translate(v=[-1.418*d1,-0.684*d1,-1.031*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.418*d1,-0.684*d1,-1.031*d1])sphere(r=r1);
translate(v=[-1.460*d1,-0.493*d1,-1.025*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.460*d1,-0.493*d1,-1.025*d1])sphere(r=r1);
translate(v=[-1.475*d1,-0.321*d1,-0.992*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.475*d1,-0.321*d1,-0.992*d1])sphere(r=r1);
translate(v=[-1.471*d1,-0.158*d1,-0.938*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.471*d1,-0.158*d1,-0.938*d1])sphere(r=r1);
translate(v=[-1.445*d1, 0.003*d1,-0.850*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.445*d1, 0.003*d1,-0.850*d1])sphere(r=r1);
translate(v=[-1.401*d1, 0.132*d1,-0.745*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.401*d1, 0.132*d1,-0.745*d1])sphere(r=r1);
translate(v=[-1.338*d1, 0.233*d1,-0.620*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.338*d1, 0.233*d1,-0.620*d1])sphere(r=r1);
translate(v=[-1.198*d1, 0.365*d1,-0.386*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.198*d1, 0.365*d1,-0.386*d1])sphere(r=r1);
translate(v=[-1.094*d1, 0.435*d1,-0.257*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.094*d1, 0.435*d1,-0.257*d1])sphere(r=r1);
translate(v=[-0.949*d1, 0.493*d1,-0.105*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.949*d1, 0.493*d1,-0.105*d1])sphere(r=r1);
translate(v=[-0.830*d1, 0.516*d1, 0.057*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.830*d1, 0.516*d1, 0.057*d1])sphere(r=r1);
translate(v=[-0.715*d1, 0.505*d1, 0.254*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.715*d1, 0.505*d1, 0.254*d1])sphere(r=r1);
translate(v=[-0.623*d1, 0.463*d1, 0.438*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.623*d1, 0.463*d1, 0.438*d1])sphere(r=r1);
translate(v=[-0.552*d1, 0.394*d1, 0.600*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.552*d1, 0.394*d1, 0.600*d1])sphere(r=r1);
translate(v=[-0.491*d1, 0.295*d1, 0.740*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.491*d1, 0.295*d1, 0.740*d1])sphere(r=r1);
translate(v=[-0.442*d1, 0.169*d1, 0.863*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.442*d1, 0.169*d1, 0.863*d1])sphere(r=r1);
translate(v=[-0.260*d1, 0.096*d1, 1.082*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.260*d1, 0.096*d1, 1.082*d1])sphere(r=r1);
translate(v=[-0.097*d1, 0.036*d1, 1.227*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.097*d1, 0.036*d1, 1.227*d1])sphere(r=r1);
translate(v=[-0.003*d1, 0.001*d1, 1.298*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.003*d1, 0.001*d1, 1.298*d1])sphere(r=r1);
translate(v=[ 0.003*d1,-0.001*d1, 1.303*d1])sphere(r=r1);}
