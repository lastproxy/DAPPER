# Misc math

from common import *

def ismat(x):
  return (type(x) is np.matrixlib.defmatrix.matrix)

def vec2list2(vec):
  return [[x] for x in vec]

def isScal(x):
  """ Works for list and row/column arrays and matrices"""
  return np.atleast_1d(x).size == 1

def is1d(a):
  """ Works for list and row/column arrays and matrices"""
  return np.sum(asarray(asarray(a).shape) > 1) <= 1

def tp(a):
  """Tranpose 1d vector"""
  return a[np.newaxis].T

def atmost_2d(func):
  """
  Decorator to make functions that work on 2-dim input
  work for (all of) 0,1, or 2-dim input.
  Requires that the 1st argument be the one of interest.
  It does not work in every case (typically not recursively),
  and should be used with caution.
  """
  def wrapr(x,*kargs,**kwargs):
    answer = func(np.atleast_2d(x),*kargs,**kwargs)
    if answer is not None: return answer.squeeze()
  return wrapr

def pad0(arr,length,val=0):
  return np.append(arr,val*zeros(length-len(arr)))


        
def anom(E,axis=0):
  if axis==0:
    mu = mean(E,0)
    A  = E - mu
  elif axis==1:
    mu = mean(E,1)
    A  = E - tp(mu)
  else: raise ValueError
  return A, mu

# Center sample (but maintain its (expected) variance)
def center(E,rescale=True):
  N = E.shape[0]
  A = E - mean(E,0)
  if rescale:
    A *= sqrt(N/(N-1))
  return A

def inflate_ens(E,factor):
  A, mu = anom(E)
  return mu + A*factor

def mrdiv(b,A):
  return nla.solve(A.T,b.T).T

def mldiv(A,b):
  return nla.solve(A,b)

def rk4(f, x0, t, dt):
  k1 = dt * f(t      , x0)
  k2 = dt * f(t+dt/2., x0+k1/2.)
  k3 = dt * f(t+dt/2., x0+k2/2.)
  k4 = dt * f(t+dt   , x0+k3)
  return x0 + (k1 + 2.*(k2 + k3) + k4)/6.0

def round2(num,prec=1.0):
  """Round with specific precision.
  Returns int if prec is int."""
  return np.multiply(prec,np.rint(np.divide(num,prec)))

def round2sigfig(x,nfig=1):
  if x == 0:
    return x
  signs = np.sign(x)
  x *= signs
  return signs*round2(x,10**np.floor(np.log10(x)-nfig+1))

def validate_int(x):
  x_int = int(x)
  assert np.isclose(x,x_int)
  return x_int

def find_1st_ind(xx):
  try:
    return next(k for k in range(len(xx)) if xx[k])
  except StopIteration:
    return None

def equi_spaced_integers(m,p):
  """Provide a range of p equispaced integers between 0 and m-1"""
  return np.round(linspace(floor(m/p/2),ceil(m-m/p/2-1),p)).astype(int)


def tsvd(A, threshold=0.99, avoid_pathological=False):
  """Truncated svd"""
  m,n    = A.shape
  U,s,VT = sla.svd(A, full_matrices = False)

  if not avoid_pathological:
    r = sum(np.cumsum(s)/sum(s) <= threshold)
  else:
    raise NotImplementedError
    # Consider the pathological case of A = Id(400).
    # Then, if using tsvd(A,0.99), then
    # A_reconstruced will be Id(400) except with zeros on last 4 diags.
    # This should typically be avoided.
    # TODO: How? In Datum, I used:
    #r = sum(np.cumsum(s)/sum(s) < (1 - (1-threshold)/sqrt(m*n)))
    #r+= 1 # Hence use strict inequality above
  
  U  = U[:,:r]
  VT = VT[:r]
  s  = s[:r]
  return U,s,VT
  
def recompose(U,s,VT):
  """
  A == recompose(tsvd(A,1)).
  Also see: sla.diagsvd().
  """
  return (U * s) @ VT

def tinv(A,*kargs,**kwargs):
  U,s,VT = tsvd(A,*kargs,**kwargs)
  return (VT.T * s**(-1.0)) @ U.T

