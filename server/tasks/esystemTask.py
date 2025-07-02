from typing import List, Union
from server.app.blackboard import BlackBoard
from server.devices.ICom import DeviceMode
from server.e_system.e_system import ESystemTemplate, ESystemState, ESystem
from server.tasks.itask import ITask
from server.tasks.task import Task


class ESystemTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, esystem: ESystemTemplate):
        super().__init__(event_time, bb)
        self.esystem = esystem
        self.state = ESystemState.STOP

    def handle_stop(self):
        for device in self.bb.devices.lst:
            device.set_esystem_data([])

    def execute(self, event_time: int) -> Union[List[ITask], ITask, None]:
        if self.esystem.state == ESystemState.STOP:
            self.handle_stop()
            return None
        
        if self.state == ESystemState.STOP and self.esystem.state == ESystemState.SELF_CONSUMPTION:
            if self.handle_init() == False:
                # TODO: something went wrong, we should handle this send message?
                return None

        
        unique_serial_numbers = self.esystem.sn_list()
        unique_devices = [device for device in self.bb.devices.lst if device.get_SN() in unique_serial_numbers]
        data = [device.get_esystem_data() for device in unique_devices]

        initial_state = ESystem(self.esystem, data)

        self_consumption_state = initial_state.self_consumption_battery()

        for device in unique_devices:
            device.set_esystem_data(self_consumption_state.get_esystem_data())


        self.adjust_time(self.bb.time_ms() + 1000)  # TODO: go faster?

        return self
    
    def handle_init(self):
        # set all battery devices in control mode
        for device in self.bb.devices.lst:
            if device.get_SN() in self.esystem.battery_sn_list:
                device.set_control_mode(DeviceMode.CONTROL)
        return True