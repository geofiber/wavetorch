import torch
from torch.nn.functional import conv2d
import numpy as np
from .absorber import BoundaryAbsorber

KERNEL_LPF = [[1/9, 1/9, 1/9],
              [1/9, 1/9, 1/9],
              [1/9, 1/9, 1/9]]

class Geometry(object):
    """
    Defines the geometry to be used by one of the physics cells
    """
    def __init__(self, Nx, Ny, h, c0=1.0, c1=0.9, design_region = None, init : str = 'half', eta : float = 0.5, beta: float = 100.0):

        super(Geometry, self).__init__()

        self.h    = h
        self.Nx   = Nx 
        self.Ny   = Ny
        self.eta  = eta
        self.beta = beta
        self.c0   = c0
        self.c1   = c1

        self.sources = []
        self.probes = []

        self.boundary_absorber = None

        self._init_design_region(design_region, Nx, Ny)
        self._init_rho(init, Nx, Ny)
        self.clip_to_design_region()

    def _init_design_region(self, design_region, Nx, Ny):
        if design_region is not None:
            # Use the specified design region
            assert design_region.shape == (Nx, Ny), "Design region mask dims must match spatial dims"
            if type(design_region) is np.ndarray:
                design_region = torch.from_numpy(design_region)
            self.design_region = design_region
        else:
            # Just use the whole domain as the design region
            self.design_region = torch.ones(Nx, Ny)

    def _init_rho(self, init, Nx, Ny):
        if init == 'rand':
            self.rho = torch.nn.Parameter( torch.round(torch.rand(Nx, Ny)) )
        elif init == 'half':
            self.rho = torch.nn.Parameter( torch.ones(Nx, Ny) * 0.5 )
        elif init == 'blank':
            self.rho = torch.nn.Parameter( torch.zeros(Nx, Ny) )
        else:
            raise ValueError('The geometry initialization defined by `init = %s` is invalid' % init)

    def clip_to_design_region(self):
        """Clip the wave speed to its background value outside of the design region."""
        with torch.no_grad():
            self.rho[self.design_region==0] = 0.0
            if self.boundary_absorber is not None:
                self.rho[self.boundary_absorber.b>0] = 0.0

    def _project_rho(self):
        """Perform the projection of the density, rho"""
        eta = self.eta
        beta = self.beta
        LPF_rho = torch.nn.functional.conv2d(self.rho.unsqueeze(0).unsqueeze(0), torch.tensor([[KERNEL_LPF]]), padding=1).squeeze()
        return (np.tanh(beta*eta) + torch.tanh(beta*(LPF_rho-eta))) / (np.tanh(beta*eta) + np.tanh(beta*(1-eta)))

    @property
    def c(self):
        return self.c0 + (self.c1-self.c0)*self._project_rho()

    def get_cmax(self):
        """Helper function for getting the maximum wave speed for calculating CFL"""
        return np.max([self.c0, self.c1])

    def __repr__(self):
        return "Geometry\n   Nx={}, Ny={}, h={}".format(self.Nx, self.Ny, self.h)

    def add_boundary_absorber(self, N=20, p=3.0, sigma=11.1):
        self.boundary_absorber = BoundaryAbsorber(self.Nx, self.Ny, N, p, sigma)

    def add_source(self, source):
        self.sources.append(source)

    def add_probe(self, probe):
        self.probes.append(probe)
