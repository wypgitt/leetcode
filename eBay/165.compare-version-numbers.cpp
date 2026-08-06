#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int compareVersion(string version1, string version2) {
        /*
        Approach: parse integer revisions separated by dots from both strings.
        Missing trailing revisions are treated as zero. Return at the first
        unequal revision.

        Complexity: O(m+n) time, O(1) extra space.
        */
        int i = 0, j = 0;
        while (i < (int)version1.size() || j < (int)version2.size()) {
            long long a = 0, b = 0;
            while (i < (int)version1.size() && version1[i] != '.') a = a * 10 + version1[i++] - '0';
            while (j < (int)version2.size() && version2[j] != '.') b = b * 10 + version2[j++] - '0';
            if (a < b) return -1;
            if (a > b) return 1;
            if (i < (int)version1.size()) ++i;
            if (j < (int)version2.size()) ++j;
        }
        return 0;
    }
};
