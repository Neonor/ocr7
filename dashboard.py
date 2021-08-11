from bokeh.server.server import Server
from json import load

from dashboard import Dashboard

with open("config.json","r") as f_conf:
    config = load(f_conf)

if __name__ == "__main__":
    svr = Server({'/': Dashboard,
                              },
                              num_procs=1,
                              address=config["host"],
                              port=config["port_bokeh"],
                              allow_websocket_origin=[f'{config.get("dns",config["host"])}:{config["port_bokeh"]}'])
    svr.run_until_shutdown()