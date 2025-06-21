'''
Black Scholes Exploration

Inputs:
–>Current stock price S
–>Exercise price X
–>Maturity in years T
–>Continuously compounded risk free rate r
–>Volatility of the underlying stock sigma
'''

from math import *

#first define these 2 functions
def d1(S,X,T,r,sigma):
    return (log(S/X)+(r+sigma*sigma/2.)*T)/(sigma*sqrt(T))

def d2(S,X,T,r,sigma):
    return d1(S,X,T,r,sigma)-sigma*sqrt(T)

#define the call option price function
def bs_call(S,X,T,r,sigma):
     return S*CND(d1(S,X,T,r,sigma))-X*exp(-r*T)*CND(d2(S,X,T,r,sigma))

#define the put options price function
def bs_put(S,X,T,r,sigma):
      return X*exp(-r*T)-S + bs_call(S,X,T,r,sigma)

#define cumulative standard normal distribution
def CND(X):
     (a1,a2,a3,a4,a5)=(0.31938153,-0.356563782,1.781477937,-1.821255978,1.330274429)
     L = abs(X)
     K=1.0/(1.0+0.2316419*L)
     w=1.0-1.0/sqrt(2*pi)*exp(-L*L/2.)*(a1*K+a2*K*K+a3*pow(K,3)+a4*pow(K,4)+a5*pow(K,5))
     if X<0:
        w=1.0-w
     return w


### main

# inputs
currentStockPrice = 40
exercisePrice = 42
maturityInYears = .5
riskFreeRate = .1
sigma = .2

# get bs call price option
callPrice = bs_call(currentStockPrice, exercisePrice, maturityInYears, riskFreeRate, sigma)


# get bs put price option
putPrice = bs_put(currentStockPrice, exercisePrice, maturityInYears, riskFreeRate, sigma)



print(callPrice)
print(putPrice)



