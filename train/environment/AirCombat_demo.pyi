#
# Automatically generated file, do not edit!
#

"""Air combat simulation module"""
from __future__ import annotations
import AirCombat_demo
import typing

__all__ = [
    "EnvInit",
    "EnvStep_PathTomonitor",
    "EnvStep_YingFei",
    "PlaneOut_0",
    "PlaneOut_1",
    "PlaneState_S",
    "Planes",
    "PrintState",
    "SetPlanePosition0",
    "SetPlanePosition1",
    "SetTargetPositon",
    "State",
    "States",
    "TargetDone",
    "UpdateState"
]


class PlaneState_S():
    def __init__(self) -> None: ...
    @property
    def _altitude(self) -> float:
        """
        :type: float
        """
    @property
    def _battleTime(self) -> float:
        """
        :type: float
        """
    @property
    def _latitude(self) -> float:
        """
        :type: float
        """
    @property
    def _longitude(self) -> float:
        """
        :type: float
        """
    @property
    def _pitch(self) -> float:
        """
        :type: float
        """
    @property
    def _raderCapture(self) -> int:
        """
        :type: int
        """
    @property
    def _roll(self) -> float:
        """
        :type: float
        """
    @property
    def _yaw(self) -> float:
        """
        :type: float
        """
    pass
class State():
    def __init__(self) -> None: ...
    @property
    def V(self) -> float:
        """
        :type: float
        """
    @property
    def altitude(self) -> float:
        """
        :type: float
        """
    @property
    def capture(self) -> bool:
        """
        :type: bool
        """
    @property
    def captureTime(self) -> float:
        """
        :type: float
        """
    @property
    def latitude(self) -> float:
        """
        :type: float
        """
    @property
    def longitude(self) -> float:
        """
        :type: float
        """
    @property
    def pitch(self) -> float:
        """
        :type: float
        """
    @property
    def roll(self) -> float:
        """
        :type: float
        """
    @property
    def targetDir(self) -> float:
        """
        :type: float
        """
    @property
    def targetDis(self) -> float:
        """
        :type: float
        """
    @property
    def yaw(self) -> float:
        """
        :type: float
        """
    pass
def EnvInit(arg0: int, arg1: list[int]) -> None:
    """
    Initialize the drone environment
    """
def EnvStep_PathTomonitor(arg0: list[int], arg1: bool) -> None:
    """
    Execute one EnvStep_PathTomonitor in the environment given actions
    """
def EnvStep_YingFei(arg0: list[list[float]], arg1: bool) -> None:
    """
    Execute one EnvStep_YingFei in the environment given actions
    """
def PlaneOut_0() -> bool:
    """
    Estimate the PlaneOut_0 state
    """
def PlaneOut_1() -> bool:
    """
    Estimate the PlaneOut_1 state
    """
def Planes() -> list[PlaneState_S]:
    pass
def PrintState() -> None:
    """
    Print the planes state
    """
def SetPlanePosition0(arg0: float, arg1: float, arg2: float) -> None:
    """
    Set the Plane_0 position
    """
def SetPlanePosition1(arg0: float, arg1: float, arg2: float) -> None:
    """
    Set the Plane_1 position
    """
def SetTargetPositon(arg0: float, arg1: float, arg2: float) -> None:
    """
    Set the target position
    """
def States() -> list[State]:
    pass
def TargetDone() -> bool:
    """
    Estimate the task state
    """
def UpdateState() -> None:
    """
    Update the planes state
    """
