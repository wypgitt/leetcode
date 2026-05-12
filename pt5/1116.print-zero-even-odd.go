package main

type ZeroEvenOdd struct {
	n        int
	zeroTurn chan struct{}
	oddTurn  chan struct{}
	evenTurn chan struct{}
}

func Constructor(n int) ZeroEvenOdd {
	zeroTurn := make(chan struct{}, 1)
	oddTurn := make(chan struct{}, 1)
	evenTurn := make(chan struct{}, 1)
	zeroTurn <- struct{}{}
	return ZeroEvenOdd{n: n, zeroTurn: zeroTurn, oddTurn: oddTurn, evenTurn: evenTurn}
}

func (z *ZeroEvenOdd) zero(printNumber func(int)) {
	for value := 1; value <= z.n; value++ {
		<-z.zeroTurn
		printNumber(0)
		if value%2 == 1 {
			z.oddTurn <- struct{}{}
		} else {
			z.evenTurn <- struct{}{}
		}
	}
}

func (z *ZeroEvenOdd) even(printNumber func(int)) {
	for value := 2; value <= z.n; value += 2 {
		<-z.evenTurn
		printNumber(value)
		z.zeroTurn <- struct{}{}
	}
}

func (z *ZeroEvenOdd) odd(printNumber func(int)) {
	for value := 1; value <= z.n; value += 2 {
		<-z.oddTurn
		printNumber(value)
		z.zeroTurn <- struct{}{}
	}
}

func (z *ZeroEvenOdd) Zero(printNumber func(int)) {
	z.zero(printNumber)
}

func (z *ZeroEvenOdd) Even(printNumber func(int)) {
	z.even(printNumber)
}

func (z *ZeroEvenOdd) Odd(printNumber func(int)) {
	z.odd(printNumber)
}
