#/usr/bin/python3

#Original code can be found at https://github.com/damiafuentes/DJITelloPy
#I just modified it to be async

import functools
import logging
import socket
import time
import asyncio

# Decorator to check method param type, raise needed exception type
# http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/
def accepts(**types):
    def check_accepts(f):
        fun_code = f.__code__
        fun_name = f.__name__

        argcount = fun_code.co_argcount
        if 'self' in fun_code.co_varnames:
            argcount -= 1

        s = "accept number of arguments not equal with function number of arguments in ", fun_name, ", argcount ", \
            argcount
        assert len(types) == argcount, s

        @functools.wraps(f)
        def new_f(*args, **kwds):
            for i, v in enumerate(args):
                if fun_code.co_varnames[i] in types and \
                        not isinstance(v, types[fun_code.co_varnames[i]]):
                    raise TypeError("arg '%s'=%r does not match %s" % (fun_code.co_varnames[i], v,
                                                                       types[fun_code.co_varnames[i]]))

            for k, v in kwds.items():
                if k in types and not isinstance(v, types[k]):
                    raise TypeError("arg '%s'=%r does not match %s" % (k, v, types[k]))

            return f(*args, **kwds)

        new_f.__name__ = fun_name
        return new_f

    return check_accepts

class DataProtocol(asyncio.DatagramProtocol):
    def __init__(self, drone):
        self.drone = drone

    def datagram_received(self, data, addr):
        try:
            self.drone.response = data[:1024]
        except TypeError as e:
            self.drone.LOGGER.error(e)

class StateProtocol(DataProtocol):
    def datagram_received(self, data, addr):
        self.drone.response_state = data
        self.drone.check_state()

class Tello:
    """Python wrapper to interact with the Ryze Tello drone using the official Tello api.
    Tello API documentation:
    https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
    """
    # Send and receive commands, client socket
    UDP_PORT = 8889
    RESPONSE_TIMEOUT = 7  # in seconds
    TIME_BTW_COMMANDS = 0.5  # in seconds
    TIME_BTW_RC_CONTROL_COMMANDS = 0.5  # in seconds
    RETRY_COUNT = 3
    last_received_command = time.time()

    HANDLER = logging.StreamHandler()
    HANDLER.setFormatter(logging.Formatter('%(filename)s - %(lineno)d - %(message)s'))

    LOGGER = logging.getLogger('djitellopy')

    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.WARNING)
    # use logging.getLogger('djitellopy').setLevel(logging.<LEVEL>) in YOUR CODE
    # to only receive logs of the desired level and higher

    STATE_UDP_PORT = 8890

    is_flying = False

    # Tello state
    pitch = -1
    roll = -1
    yaw = -1
    speed_x = -1
    speed_y = -1
    speed_z = -1
    temperature_lowest = -1
    temperature_highest = -1
    distance_tof = -1
    height = -1
    battery = -1
    barometer = -1.0
    flight_time = -1.0
    acceleration_x = -1.0
    acceleration_y = -1.0
    acceleration_z = -1.0
    attitude = {'pitch': -1, 'roll': -1, 'yaw': -1}

    def __init__(self,
                 host='192.168.10.1',
                 port=8889,
                 enable_exceptions=True,
                 retry_count=3):

        self.address = (host, port)
        self.response = None
        self.response_state = None  # to attain the response of the states
        self.enable_exceptions = enable_exceptions
        self.retry_count = retry_count

    def check_state(self):
        """This runs to recieve the state of Tello"""
        try:
            if self.response_state != 'ok':
                self.response_state = self.response_state.decode('ASCII')
                ls = self.response_state.replace(';', ':').split(':')
                self.pitch = int(ls[1])
                self.roll = int(ls[3])
                self.yaw = int(ls[5])
                self.speed_x = int(ls[7])
                self.speed_y = int(ls[9])
                self.speed_z = int(ls[11])
                self.temperature_lowest = int(ls[13])
                self.temperature_highest = int(ls[15])
                self.distance_tof = int(ls[17])
                self.height = int(ls[19])
                self.battery = int(ls[21])
                self.barometer = float(ls[23])
                self.flight_time = float(ls[25])
                self.acceleration_x = float(ls[27])
                self.acceleration_y = float(ls[29])
                self.acceleration_z = float(ls[31])
                self.attitude = {'pitch': int(ls[1]), 'roll': int(ls[3]), 'yaw': int(ls[5])}
        except (ValueError, AttributeError, IndexError) as e:
            self.LOGGER.error(e)
            self.LOGGER.error("Response was %s", self.response_state)

    @accepts(command=str, timeout=int)
    async def send_command_with_return(self, command, timeout=RESPONSE_TIMEOUT):
        """Send command to Tello and wait for its response.
        Return:
            bool: True for successful, False for unsuccessful
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds
        diff = time.time() - self.last_received_command
        if diff < self.TIME_BTW_COMMANDS:
            await asyncio.sleep(diff)

        self.LOGGER.info('Send command: %s', command)
        timestamp = time.time()

        self.clientSocket.sendto(command.encode('utf-8'), self.address)

        while self.response is None:
            await asyncio.sleep(0.1)
            if time.time() - timestamp > timeout:
                self.LOGGER.warning('Timeout exceed on command %s', command)
                return False

        try:
            response = self.response.decode('utf-8').rstrip("\r\n")
        except UnicodeDecodeError as e:
            self.LOGGER.error(e)
            return None

        self.LOGGER.info('Response %s: %s', command, response)

        self.response = None

        self.last_received_command = time.time()

        return response

    @accepts(command=str)
    def send_command_without_return(self, command):
        """Send command to Tello without expecting a response. Use this method when you want to send a command
        continuously
            - go x y z speed: Tello fly to x y z in speed (cm/s)
                x: 20-500
                y: 20-500
                z: 20-500
                speed: 10-100
            - curve x1 y1 z1 x2 y2 z2 speed: Tello fly a curve defined by the current and two given coordinates with
                speed (cm/s). If the arc radius is not within the range of 0.5-10 meters, it responses false.
                x/y/z can’t be between -20 – 20 at the same time .
                x1, x2: 20-500
                y1, y2: 20-500
                z1, z2: 20-500
                speed: 10-60
            - rc a b c d: Send RC control via four channels.
                a: left/right (-100~100)
                b: forward/backward (-100~100)
                c: up/down (-100~100)
                d: yaw (-100~100)
        """

        self.LOGGER.info('Send command (no expect response): %s', command)
        self.clientSocket.sendto(command.encode('utf-8'), self.address)

    @accepts(command=str, timeout=int)
    async def send_control_command(self, command, timeout=RESPONSE_TIMEOUT):
        """Send control command to Tello and wait for its response. Possible control commands:
            - command: entry SDK mode
            - takeoff: Tello auto takeoff
            - land: Tello auto land
            - streamon: Set video stream on
            - streamoff: Set video stream off
            - emergency: Stop all motors immediately
            - up x: Tello fly up with distance x cm. x: 20-500
            - down x: Tello fly down with distance x cm. x: 20-500
            - left x: Tello fly left with distance x cm. x: 20-500
            - right x: Tello fly right with distance x cm. x: 20-500
            - forward x: Tello fly forward with distance x cm. x: 20-500
            - back x: Tello fly back with distance x cm. x: 20-500
            - cw x: Tello rotate x degree clockwise x: 1-3600
            - ccw x: Tello rotate x degree counter- clockwise. x: 1-3600
            - flip x: Tello fly flip x
                l (left)
                r (right)
                f (forward)
                b (back)
            - speed x: set speed to x cm/s. x: 10-100
            - wifi ssid pass: Set Wi-Fi with SSID password

        Return:
            bool: True for successful, False for unsuccessful
        """
        response = None
        for _ in range(0, self.retry_count):
            response = await self.send_command_with_return(command, timeout=timeout)

            if type(response) == str and response.lower() == 'ok':
                return True

        return self.return_error_on_send_command(command, response, self.enable_exceptions)

    @accepts(command=str)
    async def send_read_command(self, command):
        """Send set command to Tello and wait for its response. Possible set commands:
            - speed?: get current speed (cm/s): x: 1-100
            - battery?: get current battery percentage: x: 0-100
            - time?: get current fly time (s): time
            - height?: get height (cm): x: 0-3000
            - temp?: get temperature (°C): x: 0-90
            - attitude?: get IMU attitude data: pitch roll yaw
            - baro?: get barometer value (m): x
            - tof?: get distance value from TOF (cm): x: 30-1000
            - wifi?: get Wi-Fi SNR: snr

        Return:
            bool: The requested value for successful, False for unsuccessful
        """

        response = await self.send_command_with_return(command)

        try:
            response = str(response)
        except TypeError as e:
            self.LOGGER.error(e)

        if ('error' not in response) and ('ERROR' not in response) and ('False' not in response):
            if response.isdigit():
                return int(response)
            try:
                return float(response)  # isdigit() is False when the number is a float(barometer)
            except ValueError:
                return response
        return self.return_error_on_send_command(command, response, self.enable_exceptions)

    def return_error_on_send_command(self, command, response, enable_exceptions):
        """Returns False and print an informative result code to show unsuccessful response"""
        msg = 'Command ' + command + ' was unsuccessful. Message: ' + str(response)
        if enable_exceptions:
            raise Exception(msg)
        self.LOGGER.error(msg)
        return False

    async def connect(self, client_socket=None):
        """Entry SDK mode
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if client_socket:
            self.clientSocket = client_socket
        else:
            self.clientSocket = socket.socket(socket.AF_INET,  # Internet
                                              socket.SOCK_DGRAM)  # UDP
            self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.clientSocket.bind(('', self.UDP_PORT))  # For UDP response (receiving data)
        self._oldSock = self.clientSocket
        self.clientSocket = (await asyncio.get_event_loop().create_datagram_endpoint(lambda: DataProtocol(self),
                                                                                     sock=self.clientSocket))[0]

        self.stateSocket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM)
        self.stateSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.stateSocket.bind(('', self.STATE_UDP_PORT))  # for accessing the states of Tello
        self.stateSocket = (await asyncio.get_event_loop().create_datagram_endpoint(lambda: StateProtocol(self),
                                                                                    sock=self.stateSocket))[0]
        return await self.send_control_command("command")

    async def takeoff(self):
        """Tello auto takeoff
        Returns:
            bool: True for successful, False for unsuccessful
            False: Unsuccessful
        """
        # Something it takes a looooot of time to take off and return a succesful take off. So we better wait. If not, is going to give us error on the following calls.
        if await self.send_control_command("takeoff", timeout=20):
            self.is_flying = True
            return True
        return False

    async def land(self):
        """Tello auto land
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if await self.send_control_command("land"):
            self.is_flying = False
            return True
        return False

    async def emergency(self):
        """Stop all motors immediately
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command("emergency")

    @accepts(direction=str, x=int)
    async def move(self, direction, x):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments:
            direction: up, down, left, right, forward or back
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command(direction + ' ' + str(x))

    @accepts(x=int)
    async def move_up(self, x):
        """Tello fly up with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("up", x)

    @accepts(x=int)
    async def move_down(self, x):
        """Tello fly down with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("down", x)

    @accepts(x=int)
    async def move_left(self, x):
        """Tello fly left with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("left", x)

    @accepts(x=int)
    async def move_right(self, x):
        """Tello fly right with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("right", x)

    @accepts(x=int)
    async def move_forward(self, x):
        """Tello fly forward with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("forward", x)

    @accepts(x=int)
    async def move_back(self, x):
        """Tello fly back with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.move("back", x)

    @accepts(x=int)
    async def rotate_clockwise(self, x):
        """Tello rotate x degree clockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command("cw " + str(x))

    @accepts(x=int)
    async def rotate_counter_clockwise(self, x):
        """Tello rotate x degree counter-clockwise.
        Arguments:
            x: 1-3600

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command("ccw " + str(x))

    @accepts(x=str)
    async def flip(self, direction):
        """Tello fly flip.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command("flip " + direction)

    async def flip_left(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.flip("l")

    async def flip_right(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.flip("r")

    async def flip_forward(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.flip("f")

    async def flip_back(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.flip("b")

    @accepts(x=int, y=int, z=int, speed=int)
    def go_xyz_speed(self, x, y, z, speed):
        """Tello fly to x y z in speed (cm/s)
        Arguments:
            x: 20-500
            y: 20-500
            z: 20-500
            speed: 10-100
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('go %s %s %s %s' % (x, y, z, speed))

    @accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int)
    def curve_xyz_speed(self, x1, y1, z1, x2, y2, z2, speed):
        """Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
            - If the arc radius is not within the range of 0.5-10 meters, it responses false.
            - x/y/z can’t be between -20 – 20 at the same time.
        Arguments:
            x1: 20-500
            x2: 20-500
            y1: 20-500
            y2: 20-500
            z1: 20-500
            z2: 20-500
            speed: 10-60
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('curve %s %s %s %s %s %s %s' % (x1, y1, z1, x2, y2, z2, speed))

    @accepts(x=int, y=int, z=int, speed=int, mid=int)
    async def go_xyz_speed_mid(self, x, y, z, speed, mid):
        """Tello fly to x y z in speed (cm/s) relative to mission pad iwth id mid
        Arguments:
            x: -500-500
            y: -500-500
            z: -500-500
            speed: 10-100
            mid: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command('go %s %s %s %s m%s' % (x, y, z, speed, mid))

    @accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int, mid=int)
    async def curve_xyz_speed_mid(self, x1, y1, z1, x2, y2, z2, speed, mid):
        """Tello fly to x2 y2 z2 over x1 y1 z1 in speed (cm/s) relative to mission pad with id mid
        Arguments:
            x1: -500-500
            y1: -500-500
            z1: -500-500
            x2: -500-500
            y2: -500-500
            z2: -500-500
            speed: 10-60
            mid: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command('curve %s %s %s %s %s %s %s m%s' % (x1, y1, z1, x2, y2, z2, speed, mid))

    @accepts(x=int, y=int, z=int, speed=int, yaw=int, mid1=int, mid2=int)
    async def go_xyz_speed_yaw_mid(self, x, y, z, speed, yaw, mid1, mid2):
        """Tello fly to x y z in speed (cm/s) relative to mid1
        Then fly to 0 0 z over mid2 and rotate to yaw relative to mid2's rotation
        Arguments:
            x: -500-500
            y: -500-500
            z: -500-500
            speed: 10-100
            yaw: -360-360
            mid1: 1-8
            mid2: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command('jump %s %s %s %s %s m%s m%s' % (x, y, z, speed, yaw, mid1, mid2))

    async def enable_mission_pads(self):
        return await self.send_control_command("mon")

    async def disable_mission_pads(self):
        return await self.send_control_command("moff")

    async def set_mission_pad_detection_direction(self, x):
        return await self.send_control_command("mdirection " + str(x))

    @accepts(x=int)
    async def set_speed(self, x):
        """Set speed to x cm/s.
        Arguments:
            x: 10-100

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return await self.send_control_command("speed " + str(x))

    last_rc_control_sent = 0

    @accepts(left_right_velocity=int, forward_backward_velocity=int, up_down_velocity=int, yaw_velocity=int)
    def send_rc_control(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if int(time.time() * 1000) - self.last_rc_control_sent < self.TIME_BTW_RC_CONTROL_COMMANDS:
            return True
        left_right_velocity = min(max(left_right_velocity, -100), 100)
        forward_backward_velocity = min(max(forward_backward_velocity, -100), 100)
        up_down_velocity = min(max(up_down_velocity, -100), 100)
        yaw_velocity = min(max(yaw_velocity, -100), 100)
        self.last_rc_control_sent = int(time.time() * 1000)
        return self.send_command_without_return('rc %s %s %s %s' % (left_right_velocity,
                                                                    forward_backward_velocity,
                                                                    up_down_velocity,
                                                                    yaw_velocity))

    async def set_wifi_credentials(self, ssid, password):
        """Set the Wi-Fi SSID and password. The Tello will reboot afterwords.
        You will have to reconnect.
        """
        await self.send_command_without_return('wifi %s %s' % (ssid, password))
        await self.end()

    async def get_speed(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        return await self.send_read_command('speed?')

    async def get_battery(self):
        """Get current battery percentage
        Returns:
            False: Unsuccessful
            int: -100
        """
        return await self.send_read_command('battery?')

    async def get_flight_time(self):
        """Get current fly time (s)
        Returns:
            False: Unsuccessful
            int: Seconds elapsed during flight.
        """
        return await self.send_read_command('time?')

    async def get_height(self):
        """Get height (cm)
        Returns:
            False: Unsuccessful
            int: 0-3000
        """
        return await self.send_read_command('height?')

    async def get_temperature(self):
        """Get temperature (°C)
        Returns:
            False: Unsuccessful
            int: 0-90
        """
        return await self.send_read_command('temp?')

    async def get_attitude(self):
        """Get IMU attitude data
        Returns:
            False: Unsuccessful
            int: pitch roll yaw
        """
        r = (await self.send_read_command('attitude?')).replace(';', ':').split(':')
        return dict(zip(r[::2], [int(i) for i in r[1::2]]))  # {'pitch': xxx, 'roll': xxx, 'yaw': xxx}

    async def get_barometer(self):
        """Get barometer value (m)
        Returns:
            False: Unsuccessful
            int: 0-100
        """
        return await self.send_read_command('baro?')

    async def get_distance_tof(self):
        """Get distance value from TOF (cm)
        Returns:
            False: Unsuccessful
            int: 30-1000
        """
        return await self.send_read_command('tof?')

    async def get_wifi(self):
        """Get Wi-Fi SNR
        Returns:
            False: Unsuccessful
            str: snr
        """
        return await self.send_read_command('wifi?')

    def end(self, override=False):
        """Call this method when you want to end the tello object"""
        if self.is_flying and not override:
            raise Exception('Drone is still flying!')
        if self.response:
            self.clientSocket.close()
            self.stateSocket.close()

    def __del__(self):
        self.end(True)
