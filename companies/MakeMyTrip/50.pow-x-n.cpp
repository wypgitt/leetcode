#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    double myPow(double x, int n) {
        /*
        Approach:
        Binary exponentiation repeatedly squares the base and consumes bits of
        the exponent. Negative exponents invert x and use the positive magnitude
        of n.

        C++ notes:
        Cast n to long long before negating so INT_MIN is handled safely.

        Complexity: O(log |n|) time and O(1) space.
        */
        long long exp = n;
        if (exp < 0) {
            x = 1.0 / x;
            exp = -exp;
        }
        double ans = 1.0;
        while (exp > 0) {
            if (exp & 1LL) ans *= x;
            x *= x;
            exp >>= 1;
        }
        return ans;
    }
};
