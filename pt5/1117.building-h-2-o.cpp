#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class H2O {
private:
    mutex mtx;
    condition_variable cv;
    int hydrogenInMolecule = 0;
    int oxygenInMolecule = 0;

    void moleculeDoneIfReady() {
        if (hydrogenInMolecule == 2 && oxygenInMolecule == 1) {
            hydrogenInMolecule = 0;
            oxygenInMolecule = 0;
            cv.notify_all();
        }
    }

public:
    H2O() {}

    void hydrogen(function<void()> releaseHydrogen) {
        unique_lock<mutex> lock(mtx);
        cv.wait(lock, [&] { return hydrogenInMolecule < 2; });
        releaseHydrogen();
        ++hydrogenInMolecule;
        moleculeDoneIfReady();
    }

    void oxygen(function<void()> releaseOxygen) {
        unique_lock<mutex> lock(mtx);
        cv.wait(lock, [&] { return oxygenInMolecule < 1; });
        releaseOxygen();
        ++oxygenInMolecule;
        moleculeDoneIfReady();
    }
};

/*
Interview Explanation

Core idea:
At most two hydrogen threads and one oxygen thread may print for a molecule.
When the current molecule has 2 H and 1 O, reset counters for the next
molecule.

C++ data structures:
- mutex protects molecule counters.
- condition_variable blocks excess hydrogen or oxygen threads.
- Counters track how many H and O have joined the current molecule.

Algorithm:
Hydrogen waits while two H atoms are already present; oxygen waits while one O
is already present. After printing, the thread increments its counter. If the
counters are 2 and 1, reset them and notify waiting threads.

Correctness:
The wait predicates prevent more than two H or one O from joining the current
molecule. Reset happens only when exactly 2 H and 1 O have printed, so the
next molecule cannot start early with an invalid ratio.

Complexity:
Each thread performs O(1) synchronization work. Space is O(1).

Edge cases:
- Arrival order does not matter.
- Spurious wakeups are safe because waits use predicates.
*/
