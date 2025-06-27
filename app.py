from flask import Flask, render_template, request, jsonify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

def load_private_key(key_data: str):
    try:
        return serialization.load_ssh_private_key(
            key_data.encode(), password=None, backend=default_backend()
        )
    except Exception:
        return None

def load_public_key(key_data: str):
    try:
        return serialization.load_ssh_public_key(
            key_data.encode(), backend=default_backend()
        )
    except Exception:
        return None

def public_keys_match(private_key, public_key):
    # Serialize both to OpenSSH format for comparison
    try:
        priv_pub = private_key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        pub_key_bytes = public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        return priv_pub == pub_key_bytes
    except Exception:
        return False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    input_method = request.form.get("input_method", "text")

    private_key_str = ""
    public_key_str = ""

    if input_method == "file":
        priv_file = request.files.get("private_key_file")
        pub_file = request.files.get("public_key_file")
        if not priv_file or not pub_file or not priv_file.filename or not pub_file.filename:
            return jsonify({"verified": False, "message": "Both files are required."})
        try:
            private_key_str = priv_file.read().decode("utf-8").strip()
            public_key_str = pub_file.read().decode("utf-8").strip()
        except Exception:
            return jsonify({"verified": False, "message": "Could not read file content."})
    else:
        private_key_str = request.form.get("private_key", "").strip()
        public_key_str = request.form.get("public_key", "").strip()
        if not private_key_str or not public_key_str:
            return jsonify({"verified": False, "message": "Both key texts are required."})

    private_key = load_private_key(private_key_str)
    public_key = load_public_key(public_key_str)

    if not private_key or not public_key:
        return jsonify({"verified": False, "message": "Invalid private or public key format."})

    if public_keys_match(private_key, public_key):
        return jsonify({"verified": True, "message": "✅ Verified: Keys match!"})
    else:
        return jsonify({"verified": False, "message": "❌ Not Verified: Keys do not match."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)