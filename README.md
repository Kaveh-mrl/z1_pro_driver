# z1_pro_driver
ROS2 driver for the XF Z-1 Pro 3-axis gimbal camera.

This repo contains two packages: `z1_pro_driver`, where all the source code for 
controlling the camera and it's gimbal live, and `z1_pro_msgs` where we have defined
a couple of messages for smooth operation of the system.

To run:
```
ros2 launch z1_pro_driver z1_pro_driver_launch.py \
        robot_name:=$ROBOT_NAME \
        camera_ip:=$GIMBAL_IP \
        camera_port:=$GIMBAL_PORT \
        camera_below_base:=True"
```
This lanuches:
- `read_and_publish`: Low level script that reads the raw packets from the camera and pubs them nicely into ROS
- `gimbal_joint_publisher` + `robot_state_publisher`: Gets you the TF tree of the camera.
- `global_gimbal_pose_pub`: Publishes the orientation of just the camera head as measured by the IMU/Gyro inside it. TF's are named like `../global_X`.  
- You can publish a Vector3 into `gimbal_camera/gimbal_cmd` to move the gimbal around in RPY. Roll and Pitch are relative to gravity and Yaw is relative to the base of the camera. 
- You can echo `gimbal_camera/gimbal_gcu_fb` to see the raw values coming form the cam.
- Set `camera_below_base` to true if the camera module is below the base (like a drone) at runtime. The gimbal reports it's pose differently depending on its starting orientation, so this is required.

```
ros2 launch z1_pro_driver z1_pro_action_launch.py \
        robot_name:=$ROBOT_NAME \
        use_sim_time:=$USE_SIM_TIME"        
```
- This launches the action servers that allow setting angles, tracking etc.


The dimensions for the `urdf` are shown in the drawings under the `fig` directory.

![Gimbal TF tree.](fig/tf_frames_rviz.png)


