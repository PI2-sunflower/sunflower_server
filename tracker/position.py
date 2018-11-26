from tracker.models import ArmPosition

_arm_position_instance = None


def arm_position_instance():
    global _arm_position_instance

    if _arm_position_instance is None:
        position = ArmPosition.objects.first()

        if position is None:
            position = ArmPosition()

        _arm_position_instance = position

    return _arm_position_instance


def serialize_arm_position(position):
    return {
        "latitude": position.latitude,
        "longitude": position.longitude,
        "altitude": position.altitude,
        "magnetometer": position.magnetometer,
        "engine_speed": position.engine_speed,
    }
