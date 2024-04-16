# get the coordinates of want tip from mocap system 
# perform scaling operations 
# prepare to send instructions to drone

from pymavlink import mavutil
from Custom_Mocap_Commands import *
#from Custom_Drone_Commands import *
from Custom_Drone_Commands_Gazebo import *
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
    initial_position = stream.wand_pos[0]
    initial_time = time.time() * 1000 # time in ms

    while True:
        current_time = time.time()*1000
        current_position = stream.wand_pos[0]

        time_elapsed = current_time - initial_time
        position_change = abs(current_position - initial_position)

        if((position_change < threshold) and (time_elapsed < interval_ms)):
            return True

        elif(time_elapsed > interval_ms):
            print("no wand movement detected")
            return False

    
init_time = time.time()

streaming_client = mocap_connect()
is_running = streaming_client.run()

stream = mocap_streaming_thread("stream1", 1, streaming_client, init_time)
stream.start()

drone_connection = connect(14551)
takeoff(drone_connection, 1)

while(is_running):
    if(check_for_movement(threshold = 0.1, interval_ms = 10)):
        #print(f"current pos (m): {stream.wand_pos}")
        send_waypoint_local(drone_connection, 5 * stream.wand_pos[2], -5 * stream.wand_pos[0], -1 * stream.wand_pos[1])
        time.sleep(.7)
    else:
        print("no wand detected - return to home in:")
        for i in range(10, 0, -1):
            print(i + "seconds")
            time.sleep(1)
        print("no wand detected - returning home")
        send_waypoint_local(drone_connection, 0, 0, -1)
        land(drone_connection)
