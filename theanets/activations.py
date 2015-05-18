# -*- coding: utf-8 -*-

r'''Activation functions for network layers.
'''

import functools
import theano
import theano.tensor as TT

from . import util

FLOAT = theano.config.floatX


def build(name, **kwargs):
    '''Construct an activation function by name.

    Parameters
    ----------
    name : str or :class:`Activation`
        The name of the type of activation function to build, or an
        already-created instance of an activation function.
    kwargs : dict
        Named arguments to pass to the activation constructor.

    Returns
    -------
    activation : :class:`Activation`
        A neural network activation function instance.
    '''
    if isinstance(name, Activation):
        return name
    def compose(a, b):
        c = lambda z: b(a(z))
        c.name = ['%s(%s)' % (b.name, a.name)]
        return c
    if '+' in name:
        return functools.reduce(compose, (build(n) for n in name.split('+')))
    return Activation.build(name, name=name, **kwargs)


class Activation(util.Registrar(str('Base'), (), {})):
    '''
    '''

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.params = []

    def __call__(self, x):
        '''Compute a symbolic expression for this activation function.

        Parameters
        ----------
        x : Theano expression
            A Theano expression representing the input to this activation
            function.

        Returns
        -------
        y : Theano expression
            A Theano expression representing the output from this activation
            function.
        '''
        raise NotImplementedError


class Linear(Activation):
    def __call__(self, x):
        return x


class Tanh(Activation):
    def __call__(self, x):
        return TT.tanh(x)

class Logistic(Activation):
    __extra_registration_keys__ = ['sigmoid']
    def __call__(self, x):
        return TT.nnet.sigmoid(x)


class Softmax(Activation):
    def __call__(self, x):
        z = TT.exp(x - x.max(axis=-1, keepdims=True))
        return z / z.sum(axis=-1, keepdims=True)


class Softplus(Activation):
    def __call__(self, x):
        return TT.nnet.softplus(x)

class Relu(Activation):
    __extra_registration_keys__ = ['rect:min']
    def __call__(self, x):
        return (x + abs(x)) / 2

class RectMax(Activation):
    __extra_registration_keys__ = ['rect:max']
    def __call__(self, x):
        return (1 + x - abs(x - 1)) / 2

class TruncatedRelu(Activation):
    __extra_registration_keys__ = ['trelu', 'rect:minmax']
    def __call__(self, x):
        return (1 + abs(x) - abs(x - 1)) / 2


class NormMean(Activation):
    __extra_registration_keys__ = ['norm:mean']
    def __call__(self, x):
        return x - x.mean(axis=-1, keepdims=True)

class NormMax(Activation):
    __extra_registration_keys__ = ['norm:max']
    def __call__(self, x):
        s = abs(x).max(axis=-1, keepdims=True)
        return x / (s + TT.cast(1e-6, FLOAT))

class NormStd(Activation):
    __extra_registration_keys__ = ['norm:std']
    def __call__(self, x):
        s = x.std(axis=-1, keepdims=True)
        return x / (s + TT.cast(1e-6, FLOAT))

class NormZ(Activation):
    __extra_registration_keys__ = ['norm:z']
    def __call__(self, x):
        c = (x - x.mean(axis=-1, keepdims=True))
        s = x.std(axis=-1, keepdims=True)
        return c / (s + TT.cast(1e-6, FLOAT))