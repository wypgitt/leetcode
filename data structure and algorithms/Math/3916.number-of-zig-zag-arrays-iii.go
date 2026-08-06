package leetcode

//
// @lc app=leetcode id=3916 lang=golang
//
// [3916] Number of Zig Zag Arrays III
//
// Correctness (odd length exponent): v·T^(2k+1) is NOT vd·(LR)^(k+1)+vu·(RL)^(k+1).
// With T=[[0,L],[R,0]], one gets new D-block = vu·(RL)^k·R and new U-block = vd·(LR)^k·L.
//
// Performance (CP Python):
// - Block reduction: (2m)×(2m) → m×m matrices LR=L·R, RL=R·L (LR[i,j]=min(i,j),
//   RL[i,j]=m−1−max(i,j)).
// - Flat row-major int lists (lower overhead than list-of-lists).
// - Symmetric squaring: if M is symmetric, (M²)[i,j]=Σ_k M[i,k]M[j,k]; fill only
//   i≤j and mirror → ~2× fewer ops when computing cur·cur in binary exponentiation.
// - General multiply kept for nonsymmetric R·cur.
//
// NumPy is intentionally NOT used: modular integer matmul needs big integers or
// per-step `%`, and object-dtype loops are slower than tight Python int loops here.
//
// =============================================================================

// @lc code=start

const mod3916 int64 = 1000000007

// ZigZagArrays3916 returns the number of zig-zag arrays III modulo 1e9+7.
func ZigZagArrays3916(n int, l int, r int) int {
	m := r - l + 1
	if n == 1 {
		return int(int64(m) % mod3916)
	}
	if n == 2 {
		return int((int64(m) * int64(m-1)) % mod3916)
	}

	ex := n - 2

	Ls := buildLFlat3916(m)
	Rs := buildRFlat3916(m)
	LR := buildMinMatrixFlat3916(m)
	RL := buildMaxMatrixFlat3916(m)

	vd := make([]int64, m)
	vu := make([]int64, m)
	for j := 0; j < m; j++ {
		vd[j] = int64(j)
		vu[j] = int64(m - 1 - j)
	}

	var a, b []int64
	if ex%2 == 0 {
		k := ex / 2
		Plr := matPowSymmetricBase3916(LR, m, k)
		Prl := matPowSymmetricBase3916(RL, m, k)
		a = vecMatFlat3916(vd, Plr, m)
		b = vecMatFlat3916(vu, Prl, m)
	} else {
		k := ex / 2
		Plr := matPowSymmetricBase3916(LR, m, k)
		Prl := matPowSymmetricBase3916(RL, m, k)
		// T^(2k+1) has blocks (LR)^k·L on U<-D and (RL)^k·R on D<-U :
		//   new(D-part) = vu · (RL)^k · R ,   new(U-part) = vd · (LR)^k · L
		tmpU := matMulFlat3916(Prl, Rs, m)
		tmpD := matMulFlat3916(Plr, Ls, m)
		a = vecMatFlat3916(vu, tmpU, m)
		b = vecMatFlat3916(vd, tmpD, m)
	}

	sum := int64(0)
	for _, x := range a {
		sum += x
	}
	for _, x := range b {
		sum += x
	}
	return int(sum % mod3916)
}

func buildLFlat3916(m int) []int64 {
	// D_i → U_j: L[i,j]=1 iff j<i (strict lower 1s in value index).
	M := make([]int64, m*m)
	for i := 0; i < m; i++ {
		base := i * m
		for j := 0; j < i; j++ {
			M[base+j] = 1
		}
	}
	return M
}

func buildRFlat3916(m int) []int64 {
	// U_i → D_j: R[i,j]=1 iff j>i.
	M := make([]int64, m*m)
	for i := 0; i < m; i++ {
		base := i * m
		for j := i + 1; j < m; j++ {
			M[base+j] = 1
		}
	}
	return M
}

func buildMinMatrixFlat3916(m int) []int64 {
	M := make([]int64, m*m)
	for i := 0; i < m; i++ {
		row := i * m
		for j := 0; j < m; j++ {
			if i < j {
				M[row+j] = int64(i)
			} else {
				M[row+j] = int64(j)
			}
		}
	}
	return M
}

func buildMaxMatrixFlat3916(m int) []int64 {
	M := make([]int64, m*m)
	for i := 0; i < m; i++ {
		row := i * m
		for j := 0; j < m; j++ {
			mx := i
			if j > mx {
				mx = j
			}
			M[row+j] = int64(m - 1 - mx)
		}
	}
	return M
}

func matPowSymmetricBase3916(M []int64, m int, p int) []int64 {
	// Binary exponentiation; base matrix M is symmetric so use symmetric squaring.
	R := make([]int64, m*m)
	for i := 0; i < m; i++ {
		R[i*m+i] = 1
	}
	cur := make([]int64, len(M))
	copy(cur, M)
	for p > 0 {
		if (p & 1) == 1 {
			R = matMulFlat3916(R, cur, m)
		}
		cur = symmetricSquareFlat3916(cur, m)
		p >>= 1
	}
	return R
}

func symmetricSquareFlat3916(M []int64, m int) []int64 {
	// For symmetric M: C[i,j]=Σ_k M[i,k]M[j,k]; compute i≤j only.
	C := make([]int64, m*m)
	for i := 0; i < m; i++ {
		ib := i * m
		for j := i; j < m; j++ {
			jb := j * m
			var s int64
			for k := 0; k < m; k++ {
				s += (M[ib+k] * M[jb+k]) % mod3916
			}
			v := s % mod3916
			C[ib+j] = v
			if i != j {
				C[j*m+i] = v
			}
		}
	}
	return C
}

func matMulFlat3916(A []int64, B []int64, m int) []int64 {
	// ikj order (good cache); one `%` per output cell after summing all k.
	C := make([]int64, m*m)
	for i := 0; i < m; i++ {
		ib := i * m
		for k := 0; k < m; k++ {
			aik := A[ib+k]
			if aik == 0 {
				continue
			}
			kb := k * m
			for j := 0; j < m; j++ {
				C[ib+j] += aik * B[kb+j]
			}
		}
		for j := 0; j < m; j++ {
			C[ib+j] %= mod3916
		}
	}
	return C
}

func vecMatFlat3916(v []int64, M []int64, m int) []int64 {
	out := make([]int64, m)
	for j := 0; j < m; j++ {
		var s int64
		for i := 0; i < m; i++ {
			vi := v[i]
			if vi != 0 {
				s = (s + (vi*M[i*m+j])%mod3916) % mod3916
			}
		}
		out[j] = s
	}
	return out
}

// @lc code=end

