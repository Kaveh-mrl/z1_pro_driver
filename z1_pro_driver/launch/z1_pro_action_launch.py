from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

try:
    from smarc_msgs.msg import Topics as SmarcTopics
except ImportError:
    # If smarc_msgs is not available, define a placeholder Topics class.
    class SmarcTopics:
        ODOM_TOPIC = "odom"

from z1_pro_msgs.msg import Topics as Z1ProTopics


def generate_launch_description():
    # Namespace as command line argument.
    robot_name_arg = DeclareLaunchArgument(
        "robot_name", default_value="", description="Namespace for the nodes.")
    robot_name = LaunchConfiguration("robot_name")

    sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value='False', description="Use simulation time.")
    use_sim_time = LaunchConfiguration("use_sim_time")

    odom_topic_arg = DeclareLaunchArgument(
        "odom_topic", default_value=SmarcTopics.ODOM_TOPIC, description="Topic for odometry data.")
    odom_topic = LaunchConfiguration("odom_topic")

    img_poi_topic_arg = DeclareLaunchArgument(
        "img_poi_topic", default_value=Z1ProTopics.IMAGE_POI_TOPIC, description="Topic for image POI data.")
    img_poi_topic = LaunchConfiguration("img_poi_topic")


    # And finally, launch the action server for gimbal control.
    gimbal_action_server_node = Node(
        package="z1_pro_driver",
        executable="gimbal_action.py",
        name="gimbal_camera_action_server",
        namespace=robot_name,
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "odom_topic": odom_topic,
            "img_poi_topic": img_poi_topic
        }]
    )

    return LaunchDescription([
        robot_name_arg,
        sim_time_arg,
        odom_topic_arg,
        img_poi_topic_arg,
        gimbal_action_server_node 
    ])
