package main

type FizzBuzz struct {
	n           int
	fizzCh      chan struct{}
	buzzCh      chan struct{}
	fizzbuzzCh  chan struct{}
	acknowledge chan struct{}
}

func Constructor(n int) FizzBuzz {
	return FizzBuzz{
		n:           n,
		fizzCh:      make(chan struct{}),
		buzzCh:      make(chan struct{}),
		fizzbuzzCh:  make(chan struct{}),
		acknowledge: make(chan struct{}),
	}
}

func (fb *FizzBuzz) fizz(printFizz func()) {
	for range fb.fizzCh {
		printFizz()
		fb.acknowledge <- struct{}{}
	}
}

func (fb *FizzBuzz) buzz(printBuzz func()) {
	for range fb.buzzCh {
		printBuzz()
		fb.acknowledge <- struct{}{}
	}
}

func (fb *FizzBuzz) fizzbuzz(printFizzBuzz func()) {
	for range fb.fizzbuzzCh {
		printFizzBuzz()
		fb.acknowledge <- struct{}{}
	}
}

func (fb *FizzBuzz) number(printNumber func(int)) {
	for value := 1; value <= fb.n; value++ {
		switch {
		case value%15 == 0:
			fb.fizzbuzzCh <- struct{}{}
			<-fb.acknowledge
		case value%3 == 0:
			fb.fizzCh <- struct{}{}
			<-fb.acknowledge
		case value%5 == 0:
			fb.buzzCh <- struct{}{}
			<-fb.acknowledge
		default:
			printNumber(value)
		}
	}
	close(fb.fizzCh)
	close(fb.buzzCh)
	close(fb.fizzbuzzCh)
}

func (fb *FizzBuzz) Fizz(printFizz func()) {
	fb.fizz(printFizz)
}

func (fb *FizzBuzz) Buzz(printBuzz func()) {
	fb.buzz(printBuzz)
}

func (fb *FizzBuzz) Fizzbuzz(printFizzBuzz func()) {
	fb.fizzbuzz(printFizzBuzz)
}

func (fb *FizzBuzz) Number(printNumber func(int)) {
	fb.number(printNumber)
}
