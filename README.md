# EMSTS(embedded system test software)

## RUN
```
sudo su
apt update
apt install python3-pip python3-mraa  python3-upm python3-dev
cd EMSTS
./start
```

### lib->display:
```
sudo su
apt install libfreetype6-dev libsdl1.2-dev libsdl-image1.2-dev \
fontconfig fonts-freefont-ttf libsdl-ttf2.0-dev libsmpeg-dev  libportmidi-dev \
libsdl-mixer1.2-dev

python3 -m pip install -U pygame --user
```
### lib->recorder:
```
sudo su
apt install python3-pyaudio
```
### modules->console->apa102
```
sudo su 
git clone --depth 1 https://github.com/respeaker/pixel_ring.git
cd pixel_ring
pip3 install -U -e .
```

### modules->microphone:
```
sudo su
pip3 install evdev
```

### modules->bluetooth:
```
apt install python3-pexpect
```
### modules->uart
```
pip3 install pyserial
```


## RaspberryPi
### mraa library
```
apt-get install cmake swig
cd;git clone https://github.com/intel-iot-devkit/mraa.git
mkdir mraa/build; cd mraa/build
cmake -D CMAKE_INSTALL_PREFIX=/usr ..
make && make install
```
### seeed-voicecard
```
cd; git clone https://github.com/respeaker/seeed-voicecard.git
./install.sh
cp ~/EMSTS/scripts/seeed-voicecard /usr/bin/
```
### lib->snowboy
```
apt-get install python-pyaudio python3-pyaudio sox
apt-get install libatlas-base-dev
pip3 install pyaudio
# snowboy library for python3
git clone https://github.com/Kitt-AI/snowboy.git
cd swig/Python3; make
```

