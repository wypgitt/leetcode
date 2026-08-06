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
    pair<int, int> parse(const string& side) {
        int coeff = 0, constant = 0, i = 0, n = side.size(), sign = 1;
        while (i < n) {
            if (side[i] == '+') { sign = 1; ++i; }
            else if (side[i] == '-') { sign = -1; ++i; }
            else {
                int value = 0, start = i;
                while (i < n && isdigit(side[i])) value = value * 10 + side[i++] - '0';
                if (i < n && side[i] == 'x') {
                    coeff += sign * (i == start ? 1 : value);
                    ++i;
                } else {
                    constant += sign * value;
                }
            }
        }
        return {coeff, constant};
    }

public:
    string solveEquation(string equation) {
        int eq = equation.find('=');
        auto [lx, lc] = parse(equation.substr(0, eq));
        auto [rx, rc] = parse(equation.substr(eq + 1));
        int coeff = lx - rx;
        int constant = rc - lc;
        if (coeff == 0) return constant == 0 ? "Infinite solutions" : "No solution";
        return "x=" + to_string(constant / coeff);
    }
};

/*
Interview explanation:
Parse each side as coeff*x + constant. Move x terms left and constants right to get coeff*x=constant, then solve or detect zero-coefficient cases.

C++ data structures: pair<int,int> returns coefficient and constant; manual scanning handles implicit coefficients like x and -x.

Edge cases: identical sides have infinite solutions; contradictory constants have no solution.

Complexity: O(n) time and O(1) space.
*/
