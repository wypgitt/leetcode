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
    int countPrimes(int n) {
        /*
        Approach: Sieve of Eratosthenes. Mark multiples of each prime starting at
        p*p because smaller multiples were already marked by smaller primes.

        Complexity: O(n log log n) time, O(n) space.
        */
        if (n <= 2) return 0;
        vector<bool> prime(n, true);
        prime[0] = prime[1] = false;
        for (long long p = 2; p * p < n; ++p) {
            if (!prime[p]) continue;
            for (long long multiple = p * p; multiple < n; multiple += p) prime[multiple] = false;
        }
        return count(prime.begin(), prime.end(), true);
    }
};
