from enum import Enum, auto


class BuldingType(Enum):
    """
    Building types present in the simulation.
    """

    SHOP = "shop"
    HOUSE = "house"
    LIBRARY = "library"
    FASTFOOD = "fastfood"
    HOSPITAL = "hospital"


class IllnessStates(Enum):
    """
    Illness states of the agent.
    """

    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RECOVERED = auto()


class SocialDistancingStates(Enum):
    """
    Social distancing options.
    """

    NO_SOCIAL_DISTANCING = auto()
    AVERAGE_SOCIAL_DISTANCING = auto()
    NORMAL_SOCIAL_DISTANCING = auto()
    EXTREME_SOCIAL_DISTANCING = auto()


class AgeGroups(Enum):
    """
    Age groups that the agent is a part of.
    """

    CHILD = auto()
    YOUNG = auto()
    ADULT = auto()
    ELDERLY = auto()


class ActivityLikelihoods(Enum):
    """
    Wheter the agent will go out a lot or stay at home.
    """

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class HumanAgentActions(Enum):
    """
    Actions that the agent can take.
    """

    STAY_IN_PLACE = auto()
    GO_OUT = auto()
