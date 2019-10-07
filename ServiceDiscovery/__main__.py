import time
import _thread

from Webservice.Webservice import Webservice
from OPCUA.OPCUAServer import OPCUAServer

check_threads_sleep_time = 5
thread_list = []

# Starting OPCUAServer
opcua_server = OPCUAServer()
opcua_server.start_server()
thread_list.append(opcua_server.thread)

# Starting Webservice
thread_list.append(_thread.start_new_thread(Webservice.start_webservice(), ()))

# Run till every thread has finished
while thread_list:
    time.sleep(check_threads_sleep_time)
    for thread in thread_list:
        if not thread.isAlive():
            thread_list.remove(thread)
