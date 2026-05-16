#!/usr/bin/env python3
import math

import rclpy
from rclpy.time import Time
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import tf2_ros
from tf_transformations import quaternion_from_euler

from geometry_msgs.msg import PoseStamped, Vector3
from z1_pro_msgs.msg import Gcudata, Topics

class GlobalPubber:
    
    def __init__(self, node):
        self.node = node

        node.declare_parameter("robot_name", "FC30")
        robot_name = node.get_parameter("robot_name").get_parameter_value().string_value

        node.declare_parameter("map_link", "map")
        map_frame = node.get_parameter("map_link").get_parameter_value().string_value
        
        self.map_frame = f"{robot_name}/{map_frame}"
        self._camera_link_name = f"{robot_name}/z1_camera_link"

        self._gcu_sub = self.node.create_subscription(Gcudata, Topics.GIMBAL_GCU_FB_TOPIC, self.gcu_cb, 10)

        self._tf_buffer = tf2_ros.Buffer()
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self.node)

        self._pose_pub = self.node.create_publisher(PoseStamped, f"/{robot_name}/rviz/global_gimbal_pose", 10)
        self._rel_pose_pub = self.node.create_publisher(PoseStamped, f"/{robot_name}/rviz/relative_gimbal_pose", 10)

        
    def gcu_cb(self, msg : Gcudata):
        rp = self.get_relative_pose_in_map()
        if rp is None:
            self.node.get_logger().error("Failed to get relative pose in map, skipping gimbal pose publish")
            return
        r = math.radians(msg.absolute_roll)
        p = math.radians(msg.absolute_pitch)
        y = math.radians(90-msg.absolute_yaw) # the raw value is compass heading, not really "yaw" in ENU
        q = quaternion_from_euler(r, p, y)
        gp = PoseStamped()
        gp.pose.orientation.x = q[0]
        gp.pose.orientation.y = q[1]
        gp.pose.orientation.z = q[2]
        gp.pose.orientation.w = q[3]
        gp.pose.position.x = rp.pose.position.x
        gp.pose.position.y = rp.pose.position.y
        gp.pose.position.z = rp.pose.position.z
        gp.header.stamp = rp.header.stamp
        gp.header.frame_id = self.map_frame
        self._pose_pub.publish(gp)
        self._rel_pose_pub.publish(rp)

    def get_relative_pose_in_map(self) -> PoseStamped|None:
        try:
            transform = self._tf_buffer.lookup_transform(self.map_frame, self._camera_link_name, Time())
            p = PoseStamped()
            p.header = transform.header
            p.pose.position.x = transform.transform.translation.x
            p.pose.position.y = transform.transform.translation.y
            p.pose.position.z = transform.transform.translation.z
            p.pose.orientation = transform.transform.rotation
            return p
        except Exception as e:
            self.node.get_logger().error(f"Failed to get transform: {e}")
            return None

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