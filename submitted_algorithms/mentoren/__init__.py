from .mark import DiagonalMultiLiner
from .nils import StateMachiner
from lennart.cao import ChaosAndOrder
from lennart.dac import DivideAndConquerOld, DivideAndConquer
from .david import Diagoliner
from .rici import ricisAlgorithmus
from .karsten import KarstensAlgorithmus


class Karsten(KarstensAlgorithmus):
    pass


class Lennart(DivideAndConquerOld):
    pass
    # def __init__(self):
    #     super().__init__(0.35)


# class Nils(StateMachiner):
#     pass


class Mark(DiagonalMultiLiner):
    pass


class David(Diagoliner):
    pass


class Rici(ricisAlgorithmus):
    pass
