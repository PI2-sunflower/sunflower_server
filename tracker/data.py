from tracker.models import ArmData

_arm_data_instance = None


def arm_data_instance():
    global _arm_data_instance

    if _arm_data_instance is None:
        arm_data = ArmData.objects.first()

        if arm_data is None:
            arm_data = ArmData()

        _arm_data_instance = arm_data

    return _arm_data_instance


def serialize_arm_data(arm_data: ArmData):
    return {
        "operation": arm_data.operation,
        "error_angle_1": arm_data.error_angle_1,
        "error_angle_2": arm_data.error_angle_2,
        "error_angle_3": arm_data.error_angle_3,
    }
