 //% Knot 4_1d (DHF, based on Wikipedia)
 //% adjusted with knotadjust.f
 //% shortened with knotshorten.f
 //% adjusted with knotadjust.f
 //% shortened with knotshorten.f
// make with infill 80%, support angle 10 deg
r1 = 3;  d1 = 10;
// Path length     29.20*d1
// tube diameter 2*r1, closest approach d1-2*r1
 hull(){
translate(v=[-0.112*d1, 0.496*d1,-0.139*d1])sphere(r=r1);
translate(v=[-0.223*d1, 0.452*d1,-0.272*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.223*d1, 0.452*d1,-0.272*d1])sphere(r=r1);
translate(v=[-0.330*d1, 0.381*d1,-0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.330*d1, 0.381*d1,-0.391*d1])sphere(r=r1);
translate(v=[-0.432*d1, 0.286*d1,-0.491*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.432*d1, 0.286*d1,-0.491*d1])sphere(r=r1);
translate(v=[-0.526*d1, 0.170*d1,-0.567*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.526*d1, 0.170*d1,-0.567*d1])sphere(r=r1);
translate(v=[-0.613*d1, 0.038*d1,-0.618*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.613*d1, 0.038*d1,-0.618*d1])sphere(r=r1);
translate(v=[-0.689*d1,-0.104*d1,-0.640*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.689*d1,-0.104*d1,-0.640*d1])sphere(r=r1);
translate(v=[-0.755*d1,-0.253*d1,-0.635*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.755*d1,-0.253*d1,-0.635*d1])sphere(r=r1);
translate(v=[-0.809*d1,-0.403*d1,-0.604*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.809*d1,-0.403*d1,-0.604*d1])sphere(r=r1);
translate(v=[-0.851*d1,-0.550*d1,-0.551*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.851*d1,-0.550*d1,-0.551*d1])sphere(r=r1);
translate(v=[-0.880*d1,-0.691*d1,-0.478*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.880*d1,-0.691*d1,-0.478*d1])sphere(r=r1);
translate(v=[-0.895*d1,-0.823*d1,-0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.895*d1,-0.823*d1,-0.391*d1])sphere(r=r1);
translate(v=[-0.897*d1,-0.943*d1,-0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.897*d1,-0.943*d1,-0.295*d1])sphere(r=r1);
translate(v=[-0.884*d1,-1.051*d1,-0.193*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.884*d1,-1.051*d1,-0.193*d1])sphere(r=r1);
translate(v=[-0.858*d1,-1.148*d1,-0.090*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.858*d1,-1.148*d1,-0.090*d1])sphere(r=r1);
translate(v=[-0.816*d1,-1.233*d1, 0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.816*d1,-1.233*d1, 0.011*d1])sphere(r=r1);
translate(v=[-0.761*d1,-1.309*d1, 0.107*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.761*d1,-1.309*d1, 0.107*d1])sphere(r=r1);
translate(v=[-0.691*d1,-1.376*d1, 0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.691*d1,-1.376*d1, 0.197*d1])sphere(r=r1);
translate(v=[-0.608*d1,-1.437*d1, 0.281*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.608*d1,-1.437*d1, 0.281*d1])sphere(r=r1);
translate(v=[-0.511*d1,-1.493*d1, 0.357*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.511*d1,-1.493*d1, 0.357*d1])sphere(r=r1);
translate(v=[-0.401*d1,-1.546*d1, 0.426*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.401*d1,-1.546*d1, 0.426*d1])sphere(r=r1);
translate(v=[-0.280*d1,-1.597*d1, 0.490*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.280*d1,-1.597*d1, 0.490*d1])sphere(r=r1);
translate(v=[-0.006*d1,-1.694*d1, 0.601*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.006*d1,-1.694*d1, 0.601*d1])sphere(r=r1);
translate(v=[ 0.297*d1,-1.779*d1, 0.694*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.297*d1,-1.779*d1, 0.694*d1])sphere(r=r1);
translate(v=[ 0.612*d1,-1.842*d1, 0.767*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.612*d1,-1.842*d1, 0.767*d1])sphere(r=r1);
translate(v=[ 0.769*d1,-1.860*d1, 0.793*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.769*d1,-1.860*d1, 0.793*d1])sphere(r=r1);
translate(v=[ 0.922*d1,-1.866*d1, 0.811*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.922*d1,-1.866*d1, 0.811*d1])sphere(r=r1);
translate(v=[ 1.068*d1,-1.858*d1, 0.819*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.068*d1,-1.858*d1, 0.819*d1])sphere(r=r1);
translate(v=[ 1.206*d1,-1.836*d1, 0.816*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.206*d1,-1.836*d1, 0.816*d1])sphere(r=r1);
translate(v=[ 1.334*d1,-1.797*d1, 0.803*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.334*d1,-1.797*d1, 0.803*d1])sphere(r=r1);
translate(v=[ 1.450*d1,-1.741*d1, 0.778*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.450*d1,-1.741*d1, 0.778*d1])sphere(r=r1);
translate(v=[ 1.553*d1,-1.669*d1, 0.742*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.553*d1,-1.669*d1, 0.742*d1])sphere(r=r1);
translate(v=[ 1.643*d1,-1.582*d1, 0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.643*d1,-1.582*d1, 0.696*d1])sphere(r=r1);
translate(v=[ 1.719*d1,-1.479*d1, 0.642*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.719*d1,-1.479*d1, 0.642*d1])sphere(r=r1);
translate(v=[ 1.783*d1,-1.363*d1, 0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.783*d1,-1.363*d1, 0.581*d1])sphere(r=r1);
translate(v=[ 1.833*d1,-1.236*d1, 0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.833*d1,-1.236*d1, 0.516*d1])sphere(r=r1);
translate(v=[ 1.873*d1,-1.099*d1, 0.448*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.873*d1,-1.099*d1, 0.448*d1])sphere(r=r1);
translate(v=[ 1.924*d1,-0.802*d1, 0.311*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.924*d1,-0.802*d1, 0.311*d1])sphere(r=r1);
translate(v=[ 1.949*d1,-0.487*d1, 0.181*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.949*d1,-0.487*d1, 0.181*d1])sphere(r=r1);
translate(v=[ 1.960*d1, 0.000*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.960*d1, 0.000*d1, 0.000*d1])sphere(r=r1);
translate(v=[ 1.949*d1, 0.487*d1,-0.181*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.949*d1, 0.487*d1,-0.181*d1])sphere(r=r1);
translate(v=[ 1.924*d1, 0.802*d1,-0.311*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.924*d1, 0.802*d1,-0.311*d1])sphere(r=r1);
translate(v=[ 1.873*d1, 1.099*d1,-0.448*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.873*d1, 1.099*d1,-0.448*d1])sphere(r=r1);
translate(v=[ 1.833*d1, 1.236*d1,-0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.833*d1, 1.236*d1,-0.516*d1])sphere(r=r1);
translate(v=[ 1.783*d1, 1.363*d1,-0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.783*d1, 1.363*d1,-0.581*d1])sphere(r=r1);
translate(v=[ 1.719*d1, 1.479*d1,-0.642*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.719*d1, 1.479*d1,-0.642*d1])sphere(r=r1);
translate(v=[ 1.643*d1, 1.582*d1,-0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.643*d1, 1.582*d1,-0.696*d1])sphere(r=r1);
translate(v=[ 1.553*d1, 1.669*d1,-0.742*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.553*d1, 1.669*d1,-0.742*d1])sphere(r=r1);
translate(v=[ 1.450*d1, 1.741*d1,-0.778*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.450*d1, 1.741*d1,-0.778*d1])sphere(r=r1);
translate(v=[ 1.334*d1, 1.797*d1,-0.803*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.334*d1, 1.797*d1,-0.803*d1])sphere(r=r1);
translate(v=[ 1.206*d1, 1.836*d1,-0.816*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.206*d1, 1.836*d1,-0.816*d1])sphere(r=r1);
translate(v=[ 1.068*d1, 1.858*d1,-0.819*d1])sphere(r=r1);}
 hull(){
translate(v=[ 1.068*d1, 1.858*d1,-0.819*d1])sphere(r=r1);
translate(v=[ 0.922*d1, 1.866*d1,-0.811*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.922*d1, 1.866*d1,-0.811*d1])sphere(r=r1);
translate(v=[ 0.769*d1, 1.860*d1,-0.793*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.769*d1, 1.860*d1,-0.793*d1])sphere(r=r1);
translate(v=[ 0.612*d1, 1.842*d1,-0.767*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.612*d1, 1.842*d1,-0.767*d1])sphere(r=r1);
translate(v=[ 0.297*d1, 1.779*d1,-0.694*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.297*d1, 1.779*d1,-0.694*d1])sphere(r=r1);
translate(v=[-0.006*d1, 1.694*d1,-0.601*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.006*d1, 1.694*d1,-0.601*d1])sphere(r=r1);
translate(v=[-0.280*d1, 1.597*d1,-0.490*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.280*d1, 1.597*d1,-0.490*d1])sphere(r=r1);
translate(v=[-0.401*d1, 1.546*d1,-0.426*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.401*d1, 1.546*d1,-0.426*d1])sphere(r=r1);
translate(v=[-0.511*d1, 1.493*d1,-0.357*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.511*d1, 1.493*d1,-0.357*d1])sphere(r=r1);
translate(v=[-0.608*d1, 1.437*d1,-0.281*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.608*d1, 1.437*d1,-0.281*d1])sphere(r=r1);
translate(v=[-0.691*d1, 1.376*d1,-0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.691*d1, 1.376*d1,-0.197*d1])sphere(r=r1);
translate(v=[-0.761*d1, 1.309*d1,-0.107*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.761*d1, 1.309*d1,-0.107*d1])sphere(r=r1);
translate(v=[-0.816*d1, 1.233*d1,-0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.816*d1, 1.233*d1,-0.011*d1])sphere(r=r1);
translate(v=[-0.858*d1, 1.148*d1, 0.090*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.858*d1, 1.148*d1, 0.090*d1])sphere(r=r1);
translate(v=[-0.884*d1, 1.051*d1, 0.193*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.884*d1, 1.051*d1, 0.193*d1])sphere(r=r1);
translate(v=[-0.897*d1, 0.943*d1, 0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.897*d1, 0.943*d1, 0.295*d1])sphere(r=r1);
translate(v=[-0.895*d1, 0.823*d1, 0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.895*d1, 0.823*d1, 0.391*d1])sphere(r=r1);
translate(v=[-0.880*d1, 0.691*d1, 0.478*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.880*d1, 0.691*d1, 0.478*d1])sphere(r=r1);
translate(v=[-0.851*d1, 0.550*d1, 0.551*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.851*d1, 0.550*d1, 0.551*d1])sphere(r=r1);
translate(v=[-0.809*d1, 0.403*d1, 0.604*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.809*d1, 0.403*d1, 0.604*d1])sphere(r=r1);
translate(v=[-0.755*d1, 0.253*d1, 0.635*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.755*d1, 0.253*d1, 0.635*d1])sphere(r=r1);
translate(v=[-0.689*d1, 0.104*d1, 0.640*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.689*d1, 0.104*d1, 0.640*d1])sphere(r=r1);
translate(v=[-0.613*d1,-0.038*d1, 0.618*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.613*d1,-0.038*d1, 0.618*d1])sphere(r=r1);
translate(v=[-0.526*d1,-0.170*d1, 0.567*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.526*d1,-0.170*d1, 0.567*d1])sphere(r=r1);
translate(v=[-0.432*d1,-0.286*d1, 0.491*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.432*d1,-0.286*d1, 0.491*d1])sphere(r=r1);
translate(v=[-0.330*d1,-0.381*d1, 0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.330*d1,-0.381*d1, 0.391*d1])sphere(r=r1);
translate(v=[-0.223*d1,-0.452*d1, 0.272*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.223*d1,-0.452*d1, 0.272*d1])sphere(r=r1);
translate(v=[-0.112*d1,-0.496*d1, 0.139*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.112*d1,-0.496*d1, 0.139*d1])sphere(r=r1);
translate(v=[ 0.000*d1,-0.511*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.000*d1,-0.511*d1, 0.000*d1])sphere(r=r1);
translate(v=[ 0.112*d1,-0.496*d1,-0.139*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.112*d1,-0.496*d1,-0.139*d1])sphere(r=r1);
translate(v=[ 0.223*d1,-0.452*d1,-0.272*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.223*d1,-0.452*d1,-0.272*d1])sphere(r=r1);
translate(v=[ 0.330*d1,-0.381*d1,-0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.330*d1,-0.381*d1,-0.391*d1])sphere(r=r1);
translate(v=[ 0.432*d1,-0.286*d1,-0.491*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.432*d1,-0.286*d1,-0.491*d1])sphere(r=r1);
translate(v=[ 0.526*d1,-0.170*d1,-0.567*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.526*d1,-0.170*d1,-0.567*d1])sphere(r=r1);
translate(v=[ 0.613*d1,-0.038*d1,-0.618*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.613*d1,-0.038*d1,-0.618*d1])sphere(r=r1);
translate(v=[ 0.689*d1, 0.104*d1,-0.640*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.689*d1, 0.104*d1,-0.640*d1])sphere(r=r1);
translate(v=[ 0.755*d1, 0.253*d1,-0.635*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.755*d1, 0.253*d1,-0.635*d1])sphere(r=r1);
translate(v=[ 0.809*d1, 0.403*d1,-0.604*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.809*d1, 0.403*d1,-0.604*d1])sphere(r=r1);
translate(v=[ 0.851*d1, 0.550*d1,-0.551*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.851*d1, 0.550*d1,-0.551*d1])sphere(r=r1);
translate(v=[ 0.880*d1, 0.691*d1,-0.478*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.880*d1, 0.691*d1,-0.478*d1])sphere(r=r1);
translate(v=[ 0.895*d1, 0.823*d1,-0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.895*d1, 0.823*d1,-0.391*d1])sphere(r=r1);
translate(v=[ 0.897*d1, 0.943*d1,-0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.897*d1, 0.943*d1,-0.295*d1])sphere(r=r1);
translate(v=[ 0.884*d1, 1.051*d1,-0.193*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.884*d1, 1.051*d1,-0.193*d1])sphere(r=r1);
translate(v=[ 0.858*d1, 1.148*d1,-0.090*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.858*d1, 1.148*d1,-0.090*d1])sphere(r=r1);
translate(v=[ 0.816*d1, 1.233*d1, 0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.816*d1, 1.233*d1, 0.011*d1])sphere(r=r1);
translate(v=[ 0.761*d1, 1.309*d1, 0.107*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.761*d1, 1.309*d1, 0.107*d1])sphere(r=r1);
translate(v=[ 0.691*d1, 1.376*d1, 0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.691*d1, 1.376*d1, 0.197*d1])sphere(r=r1);
translate(v=[ 0.608*d1, 1.437*d1, 0.281*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.608*d1, 1.437*d1, 0.281*d1])sphere(r=r1);
translate(v=[ 0.511*d1, 1.493*d1, 0.357*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.511*d1, 1.493*d1, 0.357*d1])sphere(r=r1);
translate(v=[ 0.401*d1, 1.546*d1, 0.426*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.401*d1, 1.546*d1, 0.426*d1])sphere(r=r1);
translate(v=[ 0.280*d1, 1.597*d1, 0.490*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.280*d1, 1.597*d1, 0.490*d1])sphere(r=r1);
translate(v=[ 0.006*d1, 1.694*d1, 0.601*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.006*d1, 1.694*d1, 0.601*d1])sphere(r=r1);
translate(v=[-0.297*d1, 1.779*d1, 0.694*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.297*d1, 1.779*d1, 0.694*d1])sphere(r=r1);
translate(v=[-0.612*d1, 1.842*d1, 0.767*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.612*d1, 1.842*d1, 0.767*d1])sphere(r=r1);
translate(v=[-0.769*d1, 1.860*d1, 0.793*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.769*d1, 1.860*d1, 0.793*d1])sphere(r=r1);
translate(v=[-0.922*d1, 1.866*d1, 0.811*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.922*d1, 1.866*d1, 0.811*d1])sphere(r=r1);
translate(v=[-1.068*d1, 1.858*d1, 0.819*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.068*d1, 1.858*d1, 0.819*d1])sphere(r=r1);
translate(v=[-1.206*d1, 1.836*d1, 0.816*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.206*d1, 1.836*d1, 0.816*d1])sphere(r=r1);
translate(v=[-1.334*d1, 1.797*d1, 0.803*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.334*d1, 1.797*d1, 0.803*d1])sphere(r=r1);
translate(v=[-1.450*d1, 1.741*d1, 0.778*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.450*d1, 1.741*d1, 0.778*d1])sphere(r=r1);
translate(v=[-1.553*d1, 1.669*d1, 0.742*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.553*d1, 1.669*d1, 0.742*d1])sphere(r=r1);
translate(v=[-1.643*d1, 1.582*d1, 0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.643*d1, 1.582*d1, 0.696*d1])sphere(r=r1);
translate(v=[-1.719*d1, 1.479*d1, 0.642*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.719*d1, 1.479*d1, 0.642*d1])sphere(r=r1);
translate(v=[-1.783*d1, 1.363*d1, 0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.783*d1, 1.363*d1, 0.581*d1])sphere(r=r1);
translate(v=[-1.833*d1, 1.236*d1, 0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.833*d1, 1.236*d1, 0.516*d1])sphere(r=r1);
translate(v=[-1.873*d1, 1.099*d1, 0.448*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.873*d1, 1.099*d1, 0.448*d1])sphere(r=r1);
translate(v=[-1.924*d1, 0.802*d1, 0.311*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.924*d1, 0.802*d1, 0.311*d1])sphere(r=r1);
translate(v=[-1.949*d1, 0.487*d1, 0.181*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.949*d1, 0.487*d1, 0.181*d1])sphere(r=r1);
translate(v=[-1.960*d1, 0.000*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.960*d1, 0.000*d1, 0.000*d1])sphere(r=r1);
translate(v=[-1.949*d1,-0.487*d1,-0.181*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.949*d1,-0.487*d1,-0.181*d1])sphere(r=r1);
translate(v=[-1.924*d1,-0.802*d1,-0.311*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.924*d1,-0.802*d1,-0.311*d1])sphere(r=r1);
translate(v=[-1.873*d1,-1.099*d1,-0.448*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.873*d1,-1.099*d1,-0.448*d1])sphere(r=r1);
translate(v=[-1.833*d1,-1.236*d1,-0.516*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.833*d1,-1.236*d1,-0.516*d1])sphere(r=r1);
translate(v=[-1.783*d1,-1.363*d1,-0.581*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.783*d1,-1.363*d1,-0.581*d1])sphere(r=r1);
translate(v=[-1.719*d1,-1.479*d1,-0.642*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.719*d1,-1.479*d1,-0.642*d1])sphere(r=r1);
translate(v=[-1.643*d1,-1.582*d1,-0.696*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.643*d1,-1.582*d1,-0.696*d1])sphere(r=r1);
translate(v=[-1.553*d1,-1.669*d1,-0.742*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.553*d1,-1.669*d1,-0.742*d1])sphere(r=r1);
translate(v=[-1.450*d1,-1.741*d1,-0.778*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.450*d1,-1.741*d1,-0.778*d1])sphere(r=r1);
translate(v=[-1.334*d1,-1.797*d1,-0.803*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.334*d1,-1.797*d1,-0.803*d1])sphere(r=r1);
translate(v=[-1.206*d1,-1.836*d1,-0.816*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.206*d1,-1.836*d1,-0.816*d1])sphere(r=r1);
translate(v=[-1.068*d1,-1.858*d1,-0.819*d1])sphere(r=r1);}
 hull(){
translate(v=[-1.068*d1,-1.858*d1,-0.819*d1])sphere(r=r1);
translate(v=[-0.922*d1,-1.866*d1,-0.811*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.922*d1,-1.866*d1,-0.811*d1])sphere(r=r1);
translate(v=[-0.769*d1,-1.860*d1,-0.793*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.769*d1,-1.860*d1,-0.793*d1])sphere(r=r1);
translate(v=[-0.612*d1,-1.842*d1,-0.767*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.612*d1,-1.842*d1,-0.767*d1])sphere(r=r1);
translate(v=[-0.297*d1,-1.779*d1,-0.694*d1])sphere(r=r1);}
 hull(){
translate(v=[-0.297*d1,-1.779*d1,-0.694*d1])sphere(r=r1);
translate(v=[ 0.006*d1,-1.694*d1,-0.601*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.006*d1,-1.694*d1,-0.601*d1])sphere(r=r1);
translate(v=[ 0.280*d1,-1.597*d1,-0.490*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.280*d1,-1.597*d1,-0.490*d1])sphere(r=r1);
translate(v=[ 0.401*d1,-1.546*d1,-0.426*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.401*d1,-1.546*d1,-0.426*d1])sphere(r=r1);
translate(v=[ 0.511*d1,-1.493*d1,-0.357*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.511*d1,-1.493*d1,-0.357*d1])sphere(r=r1);
translate(v=[ 0.608*d1,-1.437*d1,-0.281*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.608*d1,-1.437*d1,-0.281*d1])sphere(r=r1);
translate(v=[ 0.691*d1,-1.376*d1,-0.197*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.691*d1,-1.376*d1,-0.197*d1])sphere(r=r1);
translate(v=[ 0.761*d1,-1.309*d1,-0.107*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.761*d1,-1.309*d1,-0.107*d1])sphere(r=r1);
translate(v=[ 0.816*d1,-1.233*d1,-0.011*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.816*d1,-1.233*d1,-0.011*d1])sphere(r=r1);
translate(v=[ 0.858*d1,-1.148*d1, 0.090*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.858*d1,-1.148*d1, 0.090*d1])sphere(r=r1);
translate(v=[ 0.884*d1,-1.051*d1, 0.193*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.884*d1,-1.051*d1, 0.193*d1])sphere(r=r1);
translate(v=[ 0.897*d1,-0.943*d1, 0.295*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.897*d1,-0.943*d1, 0.295*d1])sphere(r=r1);
translate(v=[ 0.895*d1,-0.823*d1, 0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.895*d1,-0.823*d1, 0.391*d1])sphere(r=r1);
translate(v=[ 0.880*d1,-0.691*d1, 0.478*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.880*d1,-0.691*d1, 0.478*d1])sphere(r=r1);
translate(v=[ 0.851*d1,-0.550*d1, 0.551*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.851*d1,-0.550*d1, 0.551*d1])sphere(r=r1);
translate(v=[ 0.809*d1,-0.403*d1, 0.604*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.809*d1,-0.403*d1, 0.604*d1])sphere(r=r1);
translate(v=[ 0.755*d1,-0.253*d1, 0.635*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.755*d1,-0.253*d1, 0.635*d1])sphere(r=r1);
translate(v=[ 0.689*d1,-0.104*d1, 0.640*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.689*d1,-0.104*d1, 0.640*d1])sphere(r=r1);
translate(v=[ 0.613*d1, 0.038*d1, 0.618*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.613*d1, 0.038*d1, 0.618*d1])sphere(r=r1);
translate(v=[ 0.526*d1, 0.170*d1, 0.567*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.526*d1, 0.170*d1, 0.567*d1])sphere(r=r1);
translate(v=[ 0.432*d1, 0.286*d1, 0.491*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.432*d1, 0.286*d1, 0.491*d1])sphere(r=r1);
translate(v=[ 0.330*d1, 0.381*d1, 0.391*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.330*d1, 0.381*d1, 0.391*d1])sphere(r=r1);
translate(v=[ 0.223*d1, 0.452*d1, 0.272*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.223*d1, 0.452*d1, 0.272*d1])sphere(r=r1);
translate(v=[ 0.112*d1, 0.496*d1, 0.139*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.112*d1, 0.496*d1, 0.139*d1])sphere(r=r1);
translate(v=[ 0.000*d1, 0.511*d1, 0.000*d1])sphere(r=r1);}
 hull(){
translate(v=[ 0.000*d1, 0.511*d1, 0.000*d1])sphere(r=r1);
translate(v=[-0.112*d1, 0.496*d1,-0.139*d1])sphere(r=r1);}
