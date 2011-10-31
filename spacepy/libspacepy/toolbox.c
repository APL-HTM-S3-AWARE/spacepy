/*Library providing C support to toolbox

Copyright ©2011 Los Alamos National Security, LLC.
*/


/********
 * Given an array of doubles compute the hypot math.sqrt(sum((v ** 2 for v in vals[0])))
 * Brian Larsen
 * 31 Oct 2011
********/

#include <math.h>

double hypot_tb(double *data, long len) {
    double sm=0.0;
    long i;
    for (i=0;i<len;i++) {
        sm += data[i]*data[i];
    }
    return (sqrt(sm));
}

