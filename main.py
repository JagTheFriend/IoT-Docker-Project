import docker
import uuid
from flask import Flask, jsonify, make_response, request

client = docker.from_env()
app = Flask(__name__)

@app.route('/')
def register():
    return jsonify({"message": "Hello World!"}), 201


@app.route('/container', methods=['POST'])
def get_container():
    container_id = request.cookies.get('docker_container_id')

    try:
        container = client.containers.get(container_id)
        container.start()
        return jsonify({"message": "Container Started!"}), 200

    except docker.errors.NotFound:
        container = client.containers.create(
            image="codercom/code-server:latest",
            name=f"user-code-server-{str(uuid.uuid4())}",
            command=["code-server --auth none"],
            auto_remove=True,
            detach=True,
            ports={8080:0}
        )
        container.start()
        resp = make_response(jsonify({"message": "Container Created!"}), 201)
        resp.set_cookie('docker_container_id', container.id)
        return resp

    except docker.errors.APIError:
        return jsonify({"error": "Please try again later"}), 400

    return 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)