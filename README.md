# Sunflower Server

## setup

### Requirements

- Docker version >= 18
- docker-compose version >= 1.20
- N2YO API key

### Installation and execution

#### Installing requirements

<u>Linux only tutorial</u>

1) Install Docker CE: [installation link](https://docs.docker.com/install/#supported-platforms)
2) Install Docker-compose: [installation link](https://docs.docker.com/compose/install/#install-compose)
3) Get an API key from `N2YO`: [api link](https://www.n2yo.com/api/)

#### Executing the application

1) Export your API_KEY to your `.bashrc` by adding the following line to it (replace `X` with your real key!):

```
export N2YO_KEY=XXXXXX-XXXXXX-XXXXXX-XXXX
```

The `.bashrc` is usually located at `~/.bashrc`

2) Clone and open this project repository:

```
$ git clone https://github.com/PI2-sunflower/sunflower_server.git
$ cd sunflower_server/
```

3) Build the docker images

```
$ sudo -E docker-compose build
```

4) Run the application

```
$ sudo -E docker-compose up
```

5) On your browser, access one of the available endpoints on the local server (click on the words [Link]() below)

[Link](http://localhost:8000/api/track_eci/25544/2018/05/17/13/50/59/3/30) for tracking satellite's `(x, y, z)` positions.

[Link]( http://localhost:8000/api/track_azimuth_elevation/25544/-15.989620/-48.044411/500/2018/05/17/13/50/59/3/30) for tracking satellite's azimuth, elevation for an observer

[Link]( http://localhost:8000/plotter/plot_azimuth_elevation/25544/-15.989620/-48.044411/500/2018/05/17/13/50/59/1000/2) for a polar plot for a sequence of azimuth, elevation points
