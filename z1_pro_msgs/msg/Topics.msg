string GIMBAL_CMD_TOPIC = "gimbal_camera/gimbal_cmd"
string GIMBAL_FB_TOPIC = "gimbal_camera/gimbal_fb"
string GIMBAL_GCU_FB_TOPIC = "gimbal_camera/gimbal_gcu_fb"
string GIMBAL_CAMERA_CMD_TOPIC = "gimbal_camera/camera_settings"

# Action server names for camera recording control.
# Centralised here so both the action server (gimbal_action.py) and
# the action client (gimbal_action_client.py) import the same strings.
string GIMBAL_RECORD_ON_ACTION = "gimbal_record_on"
string GIMBAL_RECORD_OFF_ACTION = "gimbal_record_off"
