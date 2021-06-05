
from aiohttp import web
import signal
import subprocess
import sys

bigsleep_process = None
active_prompt = ""

def get_filename_from_prompt(prompt):
    return prompt.replace("-", "_").replace(",", "").replace(" ", "_").replace("|", "--").strip('-_')[:255] + '.png'

async def serve_interface(req):
    return web.FileResponse('interface.html')

async def handle_prompt(req):
    global bigsleep_process, active_prompt
    if bigsleep_process is not None:
        bigsleep_process.send_signal(signal.SIGINT)
        bigsleep_process.wait()
    params = req.rel_url.query
    bigsleep_process = subprocess.Popen(["dream", params['prompt']])
    active_prompt = params['prompt']

async def handle_poll(req):
    global active_prompt
    return web.FileResponse(get_filename_from_prompt(active_prompt))

async def report_active_prompt(req):
    global active_prompt
    return web.Response(text=active_prompt)

def start_server(port):
    server = web.Application()
    server.add_routes([
        web.get('/image', handle_poll),
        web.get('/activeprompt', report_active_prompt),
        web.get('/', serve_interface),
        web.get('/update', handle_prompt)
    ])
    web.run_app(server, port = port)

if __name__ == "__main__":
    start_server(port=int(sys.argv[1]) if len(sys.argv) > 1 else 8080)