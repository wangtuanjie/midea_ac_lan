import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStart,
    MessageDAResponse
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    start = "start"
    washing_data = "washing_data"
    program = "program"
    progress = "progress"
    time_remaining = "time_remaining"
    wash_time = "wash_time"
    soak_time = "soak_time"
    dehydration_time = "dehydration_time"
    dehydration_speed = "dehydration_speed"
    error_code = "error_code"
    rinse_count = "rinse_count"
    rinse_level = "rinse_level"
    wash_level = "wash_level"
    wash_strength = "wash_strength"
    softener = "softener"
    detergent = "detergent"
    

class MideaDADevice(MiedaDevice):
    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str,
            customize: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xDA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.start: False,
            DeviceAttributes.error_code: None,
            DeviceAttributes.washing_data: bytearray([]),
            DeviceAttributes.program: None,
            DeviceAttributes.progress: "Unknown",
            DeviceAttributes.time_remaining: None,
            DeviceAttributes.wash_time: None,
            DeviceAttributes.soak_time: None,
            DeviceAttributes.dehydration_time: None,
            DeviceAttributes.dehydration_speed: None,
            DeviceAttributes.rinse_count: None,
            DeviceAttributes.rinse_level: None,
            DeviceAttributes.wash_level: None,
            DeviceAttributes.wash_strength: None,
            DeviceAttributes.softener: None,
            DeviceAttributes.detergent: None
        }

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageDAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        progress = ["Idle", "Spin", "Rinse", "Wash",
                    "Weight", "Unknown", "Dry", "Soak"]
        program = ["Standard", "Fast", "Blanket", "Wool",
                   "embathe", "Memory", "Child", "Down Jacket",
                   "Stir", "Mute", "Bucket Self Clean", "Air Dry"]
        speed = ["-", "Low", "Medium", "High"]
        strength = ["-", "Week", "Medium", "Strong"]
        detergent = ["No", "Less", "Medium", "More", "4",
                    "5", "6", "7", "8", "Insufficient"]
        softener = ["No", "Intelligent", "Programed", "3", "4",
                    "5", "6", "7", "8", "Insufficient"]
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                if status == DeviceAttributes.progress:
                    self._attributes[status] = progress[getattr(message, status.value)]
                elif status == DeviceAttributes.program:
                    self._attributes[status] = program[getattr(message, status.value)]
                elif status == DeviceAttributes.rinse_level:
                    temp_rinse_level = getattr(message, status.value)
                    if temp_rinse_level == 15:
                        self._attributes[status] = "-"
                    else:
                        self._attributes[status] = temp_rinse_level
                elif status == DeviceAttributes.dehydration_speed:
                    temp_speed = getattr(message, status.value)
                    if temp_speed == 15:
                        self._attributes[status] = "-"
                    else:
                        self._attributes[status] = speed[temp_speed]
                elif status == DeviceAttributes.detergent:
                    self._attributes[status] = detergent[getattr(message, status.value)]
                elif status == DeviceAttributes.softener:
                    self._attributes[status] = softener[getattr(message, status.value)]
                elif status == DeviceAttributes.wash_strength:
                    self._attributes[status] = strength[getattr(message, status.value)]
                else:
                    self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower(self._device_protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.start:
            message = MessageStart(self._device_protocol_version)
            message.start = value
            message.washing_data = self._attributes[DeviceAttributes.washing_data]
            self.build_send(message)

class MideaAppliance(MideaDADevice):
    pass
