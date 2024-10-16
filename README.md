# FPV Drone Windows Controller

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

Install python requirements

```
pip install -r requirements.txt
```

### Installing

A step by step series of examples that tell you how to get a development env running.

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo.

## Usage <a name = "usage"></a>

Boot sequence must be the following:

1. Run the drone controller script (controllerGUI.py)

```
python controllerGUI.py
```

2. Run the RX controller emulator executable (elrs-joystick-control.exe)
3. Go to http://localhost:3000 , and connect the emulator to the RX, with baudrate 400,000
4. (might be unnecessary) Go to the inputs map and click "run"
5. (might be unnecessary) Go to the tx settings and change the refresh rate to 500Hz
6. Control the drone with the controller GUI!!! 🚁🚁🚁 And Away We Go
   🤙🤙
