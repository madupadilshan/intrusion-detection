# Lab network (guide Step 5 output)

Fill this in when the hardware lab is built. Keep it up to date: tests are only valid on the network written here.
Setup instructions: `lab_hardware/README.md`.

## 1. Devices and addresses

| Device | Make / model | Lab IP | MAC | Switch port | Notes |
| --- | --- | --- | --- | --- | --- |
| Lab router (LAN) | | 192.168.50.1 | | | OpenWrt version / Linux version: |
| Lab router (outside) | | 10.10.10.1 | | — | |
| Sensor, management port | | 192.168.50.5 | | | Ubuntu version: |
| Sensor, mirror port | | (no IP) | | | interface name: |
| Admin workstation | | 192.168.50.10 | | | |
| NVR / recording PC | | 192.168.50.20 | | | |
| IP camera | | 192.168.50.30 | | | firmware version: |
| Camera-side lab computer | | 192.168.50.31 | | | used only in scenarios 4 and 5 |
| Attack test computer | | 10.10.10.50 | | — (router outside port) | |

## 2. Diagram

(Draw it or paste a photo. Label every cable and port.)

## 3. Switch mirror settings

- Switch make / model / firmware:
- Mirror destination port (to the sensor's mirror port):
- Mirrored source ports and direction (ingress of all used ports is preferred):
- Screenshot(s):

## 4. Checks (guide Step 5 "Done when")

| Check | Date | Result |
| --- | --- | --- |
| The camera streams video to the NVR | | |
| `sudo tcpdump -i <mirror port> -c 20` on the sensor shows camera traffic | | |
| The attack computer reaches the camera through the router | | |
| No lab device reaches the university or public internet (`hwlab.py check`) | | |
| `hwlab.py check` report (all PASS) | | file: |

## 5. Bypass plan for inline mode (proposal Table 11)

If the sensor fails during an inline test, unplug both cables from the sensor and plug the switch cable straight into the router's LAN port. The network then works again at once.

| Bypass tested on | By | Time until the camera stream came back |
| --- | --- | --- |
| | | |
