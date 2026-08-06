#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    string fractionAddition(string expression) {
        long long num = 0, den = 1;
        int i = 0, n = expression.size();
        while (i < n) {
            int sign = 1;
            if (expression[i] == '+' || expression[i] == '-') sign = expression[i++] == '-' ? -1 : 1;
            long long a = 0;
            while (i < n && isdigit(expression[i])) a = a * 10 + expression[i++] - '0';
            ++i;
            long long b = 0;
            while (i < n && isdigit(expression[i])) b = b * 10 + expression[i++] - '0';
            a *= sign;
            num = num * b + a * den;
            den *= b;
            long long g = gcd(llabs(num), den);
            num /= g;
            den /= g;
        }
        return to_string(num) + "/" + to_string(den);
    }
};

/*
Interview explanation:
Maintain a running reduced fraction. Adding a/b to num/den gives (num*b+a*den)/(den*b), then gcd reduction keeps values small.

C++ data structures: long long handles intermediate products; std::gcd reduces fractions.

Edge cases: signs are parsed before numerators; zero numerator reduces to 0/1.

Complexity: O(t log V) for t fractions, dominated by gcd operations; O(1) space.
*/
