import docker
import uuid
import os
from flask import Flask, jsonify, make_response, redirect, request

NGINX_URL = 'http://localhost:7000'

client = docker.from_env()
app = Flask(__name__)

@app.route('/')
def register():
    return jsonify({"message": "Hello World!"}), 201


@app.route('/container', methods=['GET'])
def get_container():
    container_id = request.cookies.get('docker_container_id')

    if not container_id:
        container_id = 'some-random-id'

    try:
        container = client.containers.get(container_id)
        if (container.status == "paused"):
            container.unpause()
        elif (container.status != "running"):
            container.start()

        container.reload()
        port = container.ports["8080/tcp"][0]['HostPort']
        resp = make_response(redirect(NGINX_URL + '/container'))
        resp.set_cookie('docker_container_port', port)
        return resp

    except docker.errors.NotFound:
        container = client.containers.create(
            image="codercom/code-server:latest",
            name=f"user-code-server-{str(uuid.uuid4())}",
            volumes={
                 os.path.join(os.getcwd(), 'config.yaml'): {
                    'bind': '/home/coder/.config/code-server/config.yaml',
                    'mode': 'ro'
                },
                os.path.join(os.getcwd(), 'coder.json'): {
                    'bind': '/home/coder/.local/share/code-server/coder.json',
                    'mode': 'ro'
                }
            },
            auto_remove=True,
            detach=True,
            ports={8080:0}
        )
        container.start()
        container.exec_run("sudo mkdir /home/my-project")
        container.reload()
        resp = make_response(redirect(NGINX_URL + '/container'))
        port = container.ports["8080/tcp"][0]['HostPort']
        resp.set_cookie('docker_container_id', container.id)
        resp.set_cookie('docker_container_port', port)
        return resp

    except docker.errors.APIError as e:
        print(f"APIError: {e}")
        return jsonify({"error": "Please try again later"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)