import torch
import numpy as np

from .operators import _laplacian

KERNEL_LPF = [[1 / 9, 1 / 9, 1 / 9],
              [1 / 9, 1 / 9, 1 / 9],
              [1 / 9, 1 / 9, 1 / 9]]


def saturable_damping(u, uth, b0):
    return b0 / (1 + torch.abs(u / uth).pow(2))


def _time_step(b, c, y1, y2, dt, h):
    y = torch.mul((dt.pow(-2) + b * dt.pow(-1)).pow(-1),
                  (2 / dt.pow(2) * y1 - torch.mul((dt.pow(-2) - b * dt.pow(-1)), y2)
                   + torch.mul(c.pow(2), _laplacian(y1, h)))
                  )
    return y


class TimeStep(torch.autograd.Function):
    @staticmethod
    def forward(ctx, b, c, y1, y2, dt, h):
        ctx.save_for_backward(b, c, y1, y2, dt, h)
        return _time_step(b, c, y1, y2, dt, h)

    @staticmethod
    def backward(ctx, grad_output):
        b, c, y1, y2, dt, h = ctx.saved_tensors

        grad_b = grad_c = grad_y1 = grad_y2 = grad_dt = grad_h = None

        if ctx.needs_input_grad[0]:
            grad_b = - (dt * b + 1).pow(-2) * dt * (
                        c.pow(2) * dt.pow(2) * _laplacian(y1, h) + 2 * y1 - 2 * y2) * grad_output
        if ctx.needs_input_grad[1]:
            grad_c = (b * dt + 1).pow(-1) * (2 * c * dt.pow(2) * _laplacian(y1, h)) * grad_output
        if ctx.needs_input_grad[2]:
            # grad_y1 = ( dt.pow(2) * _laplacian(c.pow(2) *grad_output, h) + 2*grad_output) * (b*dt + 1).pow(-1)
            c2_grad = (b * dt + 1).pow(-1) * c.pow(2) * grad_output
            grad_y1 = dt.pow(2) * _laplacian(c2_grad, h) + 2 * grad_output * (b * dt + 1).pow(-1)
        if ctx.needs_input_grad[3]:
            grad_y2 = (b * dt - 1) * (b * dt + 1).pow(-1) * grad_output

        return grad_b, grad_c, grad_y1, grad_y2, grad_dt, grad_h


class WaveCell(torch.nn.Module):
    """The recurrent neural network cell implementing the scalar wave equation"""

    def __init__(self,
                 dt : float,
                 geometry,
                 satdamp_b0 : float = 0.0,
                 satdamp_uth : float = 0.0,
                 c_nl : float = 0.0):

        super().__init__()

        self.dt =dt
        self.geom = geometry
        self.satdamp_b0 = satdamp_b0
        self.satdamp_uth = satdamp_uth
        self.c_nl = c_nl

        # Validate inputs
        cmax = self.geom.get_cmax()
        h = self.geom.h

        if dt > 1 / cmax * h / np.sqrt(2):
            raise ValueError(
                'The spatial discretization defined by the geometry `h = %f` and the temporal discretization defined by the model `dt = %f` do not satisfy the CFL stability criteria' % (
                h, dt))

    def forward(self, y1, y2, c_lin, rho):
        """Take a step through time

        Parameters
        ----------
        x : 
            Input value(s) at current time step, batched in first dimension
        y1 : 
            Scalar wave field one time step ago (part of the hidden state)
        y2 : 
            Scalar wave field two time steps ago (part of the hidden state)
        c_lin :
            Scalar wave speed distribution (this gets passed in to avoid generating it on each time step, saving memory for backprop)
        rho : 
            Projected density, required for nonlinear response (this gets passed in to avoid generating it on each time step, saving memory for backprop)
        """

        if self.satdamp_b0 > 0:
            b = self.b + rho * saturable_damping(y1, uth=self.satdamp_uth, b0=self.satdamp_b0)
        else:
            b = self.b

        if self.c_nl != 0:
            c = c_lin + rho * self.c_nl * y1.pow(2)
        else:
            c = c_lin

        y = TimeStep.apply(b, c, y1, y2, self.dt, self.h)
        # y = _time_step(b, c, y1, y2, dt, h)

        return y, y1
