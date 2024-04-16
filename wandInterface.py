# get the coordinates of want tip from mocap system 
# perform scaling operations 
# prepare to send instructions to drone

from pymavlink import mavutil
from Custom_Mocap_Commands import *
from Custom_Drone_Commands import *
#from Custom_Drone_Commands_Gazebo import *
import time
import threading

class mocap_streaming_thread(threading.Thread):
    def __init__(self, thread_name, thread_ID, mocap_connection, init_time):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.mocap_connection = mocap_connection
        self.init_time = init_time
        self.wand_pos = None
        self.wand_rot = None

    def run(self):
        while True:
            time.sleep(.1)

            [self.wand_pos, self.wand_rot] = self.mocap_connection.rigid_body_dict[2]

            #print(f"Current y (m): {self.wand_pos[1]}")
            #print(f"Current z (m): {self.wand_pos[0]}")
            #print(f"Current x (m): {self.wand_pos[2]}")


        return



#Main thread:


def check_for_movement(threshold = 0.1, interval_ms = 10):
    initial_position = wand_stream.wand_pos[0]
    initial_time = time.time() * 1000 # time in ms

    while True:
        current_time = time.time()*1000
        current_position = wand_stream.wand_pos[0]

        time_elapsed = current_time - initial_time
        position_change = abs(current_position - initial_position)

        if((position_change < threshold) and (time_elapsed < interval_ms)):
            return True

        elif(time_elapsed > interval_ms):
            print("no wand movement detected")
            return False

def reset_wand_position_origin():
    initial_position_offset_x = wand_stream.wand_pos[2]
    initial_position_offset_y = wand_stream.wand_pos[0]
    initial_position_offset_z = wand_stream.wand_pos[1]

    
init_time = time.time()
drone_streaming_id = 2
wand_streaming_id = 1

streaming_client = mocap_connect()
is_running = streaming_client.run()

drone_connection = drone_connect(14550)
set_drone_gps_global_origin(drone_connection)

wand_stream = mocap_streaming_thread("stream1", wand_streaming_id, streaming_client, init_time)
wand_stream.start()

initial_position_offset_x = 0
initial_position_offset_y = 0
initial_position_offset_z = 0

reset_wand_position_origin()

time.sleep(1)

drone_stream = threaded_mocap_streaming("stream2", drone_streaming_id, drone_connection, streaming_client, init_time)
drone_stream.start()

#time.sleep(3)
#takeoff(drone_connection, streaming_client, init_time, .5)
time.sleep(1)

while(is_running):
    if(check_for_movement(threshold = 0.01, interval_ms = 10)):
        #print(f"current pos (m): {stream.wand_pos}")
        x = 0
        y = 0
        z = 0
        box_length = 3
        scale = 1

        scaled_wand_pos_x = scale * (wand_stream.wand_pos[2] - initial_position_offset_x)
        scaled_wand_pos_y = scale * (wand_stream.wand_pos[0] - initial_position_offset_y)
        scaled_wand_pos_z = scale * (wand_stream.wand_pos[1] - initial_position_offset_z)

        if (scaled_wand_pos_x < box_length and scaled_wand_pos_x > -box_length):
            x = scaled_wand_pos_x
        if (scaled_wand_pos_y < box_length and scaled_wand_pos_y > -box_length):
            y = scaled_wand_pos_y
        #if (-1 * stream.wand_pos[1] < 3):
        #    x = 2 * stream.wand_pos[2]

        print(f"going to {x}, {y}")
        goto_NED_point(drone_connection, x, -y, -.5, init_time, accuracy=.5)

        time.sleep(.8)
    else:
        print("no wand detected - return to home in:")
        for i in range(10, 0, -1):
            print(i + "seconds")
            time.sleep(1)
        print("no wand detected - returning home")
        goto_NED_point(drone_connection, 0, 0, -1, init_time, accuracy=.05)
        land(drone_connection)

time.sleep(30)