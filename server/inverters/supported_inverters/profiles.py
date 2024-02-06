"""
Maybe the get function below should return a class object? 
"""

from .inverters.sungrow import profile as sungrow
from .inverters.sungrow_hybrid import profile as sungrow_hybrid
from .inverters.solaredge import profile as solaredge
from .inverters.growatt import profile as growatt
from .inverters.huawei import profile as huawei
from .inverters.lqt40s import profile as lqt40s

inverters = [sungrow, sungrow_hybrid, solaredge, growatt, huawei, lqt40s]

def get_inverter_profile(inverter_name):

    try:
        for inverter in inverters:
            if inverter["name"] == inverter_name:
                return inverter
    except Exception as e:
        print(f"Error: {e}")

    return None

    