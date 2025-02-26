
# used by the PREPROCESS class and specified by the MISFIT parameter


import sys
import numpy as np
import cmath
from scipy.signal import hilbert as _analytic
from scipy.fftpack import fft, fftfreq
from seisflows.tools.array import loadnpy

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

def Waveform(syn, obs, nt, dt):
    # waveform difference
    wrsd = syn-obs
    return np.sqrt(np.sum(wrsd*wrsd*dt))


def Envelope(syn, obs, nt, dt, eps=0.05):
    # envelope difference
    # (Yuan et al 2015, eq 9)
    esyn = abs(_analytic(syn))
    eobs = abs(_analytic(obs))
    ersd = esyn-eobs
    return np.sqrt(np.sum(ersd*ersd*dt))


def InstantaneousPhase(syn, obs, nt, dt, eps=0.05):
    # instantaneous phase 
    # from Bozdag et al. 2011

    r = np.real(_analytic(syn))
    i = np.imag(_analytic(syn))
    phi_syn = np.arctan2(i,r)

    r = np.real(_analytic(obs))
    i = np.imag(_analytic(obs))
    phi_obs = np.arctan2(i,r)

    phi_rsd = phi_syn - phi_obs
    return np.sqrt(np.sum(phi_rsd*phi_rsd*dt))


def Traveltime(syn, obs, nt, dt):
    cc = abs(np.convolve(obs, np.flipud(syn)))
    return (np.argmax(cc)-nt+1)*dt


def TraveltimeInexact(syn, obs, nt, dt):
    # much faster but possibly inaccurate
    it = np.argmax(syn)
    jt = np.argmax(obs)
    return (jt-it)*dt


def Amplitude(syn,obs,nt,dt):

    A_obs = np.sqrt(np.sum(obs*obs*dt))
    A_syn = np.sqrt(np.sum(syn*syn*dt))

    return np.log(A_obs/A_syn)



def Envelope3(syn, obs, nt, dt, eps=0.):
    # envelope cross-correlation lag
    # (Yuan et al 2015, eqs B-4)
    esyn = abs(_analytic(syn))
    eobs = abs(_analytic(obs))
    return Traveltime(esyn, eobs, nt, dt)


def InstantaneousPhase2(syn, obs, nt, dt, eps=0.):
    esyn = abs(_analytic(syn))
    eobs = abs(_analytic(obs))

    esyn1 = esyn + eps*max(esyn)
    eobs1 = eobs + eps*max(eobs)

    diff = syn/esyn1 - obs/eobs1

    return np.sqrt(np.sum(diff*diff*dt))



def Displacement(syn, obs, nt, dt):
    return Exception('This function can only used for migration.')

def Velocity(syn, obs, nt, dt):
    return Exception('This function can only used for migration.')

def Acceleration(syn, obs, nt, dt):
    return Exception('This function can only used for migration.')


def Phase2_se(syn, nt, dt,ft_obs, freq_mask):
    # waveform difference in the frequency domain, considering orthogonal frequencies
    nstep = len(syn)
    wadj = 0.0 #np.zeros(nstep)
    ntpss = PAR.NTPSS
    #create a frequential mask
    m = loadnpy(PATH.ORTHO + '/freq_idx')
    ft_syn = fft(syn[-ntpss:])[m]
    obs = ft_syn / ft_obs

    phase = np.vectorize(cmath.phase)
    phase_obs = phase(obs)

    wadj = (freq_mask * phase_obs**2).sum()
    return wadj

