
from aiohttp import web
import signal
import subprocess
import sys
import os.path
import os

bigsleep_process = None
active_prompt = ""

def get_filename_from_prompt(prompt):
    return prompt.replace("-", "_").replace(",", "").replace(" ", "_").replace("|", "--").strip('-_')[:255] + '.png'

async def serve_interface(req):
    return web.FileResponse('interface.html')

async def handle_prompt(req):
    global bigsleep_process, active_prompt
    print("updating prompt")
    if bigsleep_process is not None:
        print("cancelling existing dream")
        bigsleep_process.send_signal(signal.SIGINT)
        bigsleep_process.wait()
    params = req.rel_url.query
    os.chdir('outputs')
    bigsleep_process = subprocess.Popen(["dream", params['prompt'], "--open_folder", "False", "--save_every", "10", "--overwrite", "True"])
    os.chdir('..')
    active_prompt = params['prompt']
    print('setting prompt to:', repr(active_prompt))
    return web.Response(text='ok')

async def handle_poll(req):
    global active_prompt
    print("poll")
    image_file = get_filename_from_prompt(active_prompt)
    if os.path.exists(image_file):
        return web.FileResponse(image_file)
    else:
        return web.Response(status=404)

async def report_active_prompt(req):
    global active_prompt
    print("reporting active prompt:", repr(active_prompt))
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
    if not os.path.exists('outputs'):
        os.mkdir('outputs')
    start_server(port=int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
