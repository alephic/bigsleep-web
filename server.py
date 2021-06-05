
from aiohttp import web
import asyncio
import signal
import subprocess

bigsleep_process = None

def get_filename_from_prompt(prompt):
    return prompt.replace("-", "_").replace(",", "").replace(" ", "_").replace("|", "--").strip('-_')[:255] + '.png'

async def serve_interface(req):
    return web.FileResponse('interface.html')

async def handle_prompt(req):
    global bigsleep_process
    if bigsleep_process is not None:
        bigsleep_process.send_signal(signal.SIGINT)
        bigsleep_process.wait()
    params = req.rel_url.query
    bigsleep_process = subprocess.Popen(["dream", params['prompt']])

async def handle_poll(req):
    params = req.rel_url.query
    return web.FileResponse(get_filename_from_prompt(params['prompt']))