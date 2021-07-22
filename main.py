"""
STREAMING DRONE FOOTAGE TO OPENCV

Before running this file:
- Ensure NGINX server is up and running. Refer to commands below if needed:
    * In cmd, navigate to nginx directory using 'cd /nginx'
    - 'start nginx'     <- starts server
    - 'nginx -s stop'   <- fast shutdown
    - 'nginx -s quit'   <- graceful quit (preferred)
    - 'nginx -s reload' <- reloads server
- Ensure FPS is correct
- Ensure IP is saved in info.py as a string: IP = '[your IP]'

"""

# IMPORT LOCAL FILES
from VideoStream import VideoStream
import info


# MAIN SCRIPT
def main():
    # Addresses
    rtmp = 'rtmp://' + info.IP + ':1935/live/'
    webcam = 0  # for process testing

    strm = VideoStream(rtmp, 38)
    strm.start()


if __name__ == "__main__":
    main()
