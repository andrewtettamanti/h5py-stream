#!/usr/bin/env python
# coding: utf-8

# In[1]:


import uhd
import numpy as np
import h5py
import rospy
from geometry_msgs.msg import PoseStamped

pose_x = None
pose_y = None


# ROS Stuff
def callback(data):
    pose_x = data.pose.position.x
    pose_y = data.pose.position.y
    

TOPIC="/car/car_pose"
rospy.init_node('listener', anonymous=True)
rospy.Subscriber(TOPIC, PoseStamped, callback)



usrp = uhd.usrp.MultiUSRP()
num_samps = 10000 # number of samples received
center_freq = 770e6 # Hz
sample_rate = 50e6 # Hz
gain = 50 # dB

usrp.set_rx_rate(sample_rate, 0)
usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(center_freq), 0)
usrp.set_rx_gain(gain, 0)

# Set up the stream and receive buffer
st_args = uhd.usrp.StreamArgs("fc32", "sc16")
st_args.channels = [0]
metadata = uhd.types.RXMetadata()
streamer = usrp.get_rx_stream(st_args)
#recv_buffer = np.zeros(streamer.get_max_num_samps, dtype=np.complex64)
recv_buffer = np.zeros((100000,1000), dtype=np.complex64)

x_pose = np.zeros((len(recv_buffer),1))
y_pose = np.zeros((len(recv_buffer),1))

# Start Stream

stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
stream_cmd.stream_now = True
streamer.issue_stream_cmd(stream_cmd)


f = h5py.File('datastream.h5', 'w')

dset = f.create_dataset("samples", data=recv_buffer)
xset = f.create_dataset("x", data=x_pose)
yset = f.create_dataset("y", data=y_pose)

for i in range(len(recv_buffer)):
    streamer.recv(recv_buffer, metadata)

    dset[i] = recv_buffer[0]
    xset[i] = pose_x
    yset[i] = pose_y

    
# Stop Stream
stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
streamer.issue_stream_cmd(stream_cmd)


f.close()


# In[ ]:




