from __future__ import print_function
import time

import serial

from telemetry.parser import TelemetrySerial, TelemetrySocket

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Telemetry packet parser example.')

  parser.add_argument('--hostname', metavar='h', help='network hostname')
  parser.add_argument('--port', metavar='p', help='network port', default=1234)

  parser.add_argument('--serial', metavar='s', help='serial port to receive on')
  parser.add_argument('--baud', metavar='b', type=int, default=38400,
                      help='serial baud rate')
  args = parser.parse_args()

  telemetry = None
  if args.serial is not None:
    assert telemetry is None, "multiple comms methods defined in arguments"
    telemetry = TelemetrySerial(serial.Serial(args.serial, baudrate=args.baud))
    print(f"Opened serial port on {args.serial}: {args.baud}")
  if args.hostname is not None:
    assert telemetry is None, "multiple comms methods defined in arguments"
    telemetry = TelemetrySocket(args.hostname, args.port)
    print(f"Opened network socket on {args.hostname}: {args.port}")

  while True:
    telemetry.process_rx()
    time.sleep(0.1)

    while True:
      next_packet = telemetry.next_rx_packet()
      if not next_packet:
        break
      print('')
      print(next_packet)
    
    while True:
      next_byte = telemetry.next_rx_byte()
      if next_byte is None:
        break
      try:
        print(chr(next_byte), end='')
      except UnicodeEncodeError:
        pass
