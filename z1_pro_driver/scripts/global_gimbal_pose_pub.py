#!/usr/bin/env python3
import math

import rclpy
from rclpy.time import Time
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import tf2_ros
from tf_transformations import quaternion_from_euler

from geometry_msgs.msg import TransformStamped
from z1_pro_msgs.msg import Gcudata, Topics

class GlobalPubber:
    
    def __init__(self, node):
        self.node = node

        node.declare_parameter("robot_name", "FC30")
        robot_name = node.get_parameter("robot_name").get_parameter_value().string_value

        node.declare_parameter("map_link", "map")
        map_frame = node.get_parameter("map_link").get_parameter_value().string_value
        
        self._map_link = f"{robot_name}/{map_frame}"
        self._local_camera_link = f"{robot_name}/z1_camera_link"
        self._global_camera_link = f"{robot_name}/z1_global_camera_link"
        global_optical_link = f"{robot_name}/z1_global_optical_frame"

        node.get_logger().info(f"Global gimbal pose publisher initialized with map link: {self._map_link}, local camera link: {self._local_camera_link}, global camera link: {self._global_camera_link}, global optical link: {global_optical_link}")

        self._gcu_sub = self.node.create_subscription(Gcudata, Topics.GIMBAL_GCU_FB_TOPIC, self.gcu_cb, 10)

        self._tf_buffer = tf2_ros.Buffer()
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self.node)
        self._tf_broadcaster = tf2_ros.TransformBroadcaster(self.node)

        self._abs_rpy : tuple[float, float, float]|None = None
        freq = 10.0
        self._timer = self.node.create_timer(1/freq, self.pub_global)

        # following the usual optical frame convention of x right y down, z forward.
        optical_rpy = (-1.57079632679, 0, -1.57079632679)
        q_optical = quaternion_from_euler(*optical_rpy)
        global_optical = TransformStamped()
        global_optical.transform.rotation.x = q_optical[0]
        global_optical.transform.rotation.y = q_optical[1]
        global_optical.transform.rotation.z = q_optical[2]
        global_optical.transform.rotation.w = q_optical[3]
        global_optical.transform.translation.x = 0.0
        global_optical.transform.translation.y = 0.0
        global_optical.transform.translation.z = 0.0
        global_optical.header.frame_id = self._global_camera_link
        global_optical.child_frame_id = global_optical_link
        def pub_optical():
            global_optical.header.stamp = self.node.get_clock().now().to_msg()
            self._tf_broadcaster.sendTransform(global_optical)

        self._optical_timer = self.node.create_timer(1.0, pub_optical)


        
    def gcu_cb(self, msg : Gcudata):
        r = math.radians(msg.absolute_roll)
        p = math.radians(msg.absolute_pitch)
        y = math.radians(90-msg.absolute_yaw) # the raw value is compass heading, not really "yaw" in ENU
        self._abs_rpy = (r,p,y)
        
        
    def pub_global(self):
        if self._abs_rpy is None:
            return
        try:
            rp = self._tf_buffer.lookup_transform(self._map_link, self._local_camera_link, Time(), Duration(seconds=1))
        except Exception as e:
            self.node.get_logger().error(f"Failed to get transform: {e}")
            return
        
        q = quaternion_from_euler(*self._abs_rpy)
        gp = TransformStamped()
        gp.transform.rotation.x = q[0]
        gp.transform.rotation.y = q[1]
        gp.transform.rotation.z = q[2]
        gp.transform.rotation.w = q[3]
        gp.transform.translation.x = rp.transform.translation.x
        gp.transform.translation.y = rp.transform.translation.y
        gp.transform.translation.z = rp.transform.translation.z
        gp.header.stamp = rp.header.stamp
        gp.header.frame_id = self._map_link
        gp.child_frame_id = self._global_camera_link

        self._tf_broadcaster.sendTransform(gp)
        


def main():
    rclpy.init()
    
    node = Node("global_gimbal_pose_pub_node")
    GlobalPubber(node)
    
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()