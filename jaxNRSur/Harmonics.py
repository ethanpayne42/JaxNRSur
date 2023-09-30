import jax.numpy as jnp
from jaxtyping import Array, Float
import equinox as eqx


# factorial function
def fac(n: int):  # -> int:
    result = 1

    for i in range(2, n + 1):
        result *= i

    return result


# coefficient function
def Cslm(s: int, l_mode: int, m_mode: int) -> Float[Array, str("1")]:
    return jnp.sqrt(
        l_mode
        * l_mode
        * (4.0 * l_mode * l_mode - 1.0)
        / ((l_mode * l_mode - m_mode * m_mode) * (l_mode * l_mode - s * s))
    )


# recursion function
def s_lambda_lm(
    s_mode: int, l_mode: int, m_mode: int, theta: Float[Array, str("1")]
) -> Float[Array, str("1")]:
    Pm = pow(-0.5, m_mode)

    if m_mode != s_mode:
        Pm = Pm * pow(1.0 + theta, (m_mode - s_mode) * 1.0 / 2)
    if m_mode != -s_mode:
        Pm = Pm * pow(1.0 - theta, (m_mode + s_mode) * 1.0 / 2)

    Pm = Pm * jnp.sqrt(
        fac(2 * m_mode + 1)
        * 1.0
        / (4.0 * jnp.pi * fac(m_mode + s_mode) * fac(m_mode - s_mode))
    )

    if l_mode == m_mode:
        return Pm

    Pm1 = (theta + s_mode * 1.0 / (m_mode + 1)) * Cslm(s_mode, m_mode + 1, m_mode) * Pm

    if l_mode == m_mode + 1:
        return Pm1
    else:
        Pn = jnp.array(0.0)
        for n in range(m_mode + 2, l_mode + 1):
            Pn = (theta + s_mode * m_mode * 1.0 / (n * (n - 1.0))) * Cslm(
                s_mode, n, m_mode
            ) * Pm1 - Cslm(s_mode, n, m_mode) * 1.0 / Cslm(s_mode, n - 1, m_mode) * Pm
            Pm = Pm1
            Pm1 = Pn
        return Pn


class SpinWeightedSphericalHarmonics(eqx.Module):
    Pm_coeff: float
    s_mode: int
    l_mode: int
    m_mode: int

    def __init__(
        self,
        s_mode: int,
        l_mode: int,
        m_mode: int,
    ) -> None:
        Pm = 1.0

        if l_mode < 0:
            raise ValueError("l must be non-negative")
        if abs(m_mode) > l_mode or l_mode < abs(s_mode):
            raise ValueError("l must be greater than or equal to |s| and |m|")

        if abs(m_mode) < abs(s_mode):
            s_mode = m_mode
            m_mode = s_mode
            if (m_mode + s_mode) % 2:
                Pm = -Pm

        if m_mode < 0:
            s_mode = -s_mode
            m_mode = -m_mode
            if (m_mode + s_mode) % 2:
                Pm = -Pm

        self.Pm_coeff = Pm
        self.s_mode = s_mode
        self.l_mode = l_mode
        self.m_mode = m_mode

    def __call__(self, theta: float, phi: float) -> Float[Array, str("1")]:
        result = self.Pm_coeff * s_lambda_lm(
            self.s_mode, self.l_mode, self.m_mode, jnp.cos(theta)
        )
        return result * jnp.cos(self.m_mode * phi) + 1j * (
            result * jnp.sin(self.m_mode * phi)
        )
