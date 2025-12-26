
# Hyperion

![License](https://img.shields.io/badge/license-GPLv3%2B-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Frontend](https://img.shields.io/badge/frontend-Svelte-orange)
![Status](https://img.shields.io/badge/status-Alpha-red)

**Hyperion** is a modern, web-based DMX control system designed to bridge the gap between professional consoles and hobbyist tools.

It features a distributed architecture, separating the "Brain" (server logic) from the "Node" (DMX output), allowing for flexible deployments on Raspberry Pis, generic PCs, or servers.

## ✨ Features

* **Modern Interface:** Touch-first web UI built with Svelte & Vite.
* **Distributed Architecture:** Run the backend on your laptop and the DMX output on a Raspberry Pi over the network.
* **Hardware Agnostic:** Supports ArtNet, sACN, USB-DMX (Enttec/uDMX), and direct GPIO (Raspberry Pi).
* **API First:** Full control via REST API and WebSockets (FastAPI).

## 🚀 Architecture

Hyperion consists of two main components:

1.  **Core (Brain):** Manages the database, API, and lighting logic.
2.  **Node (Runner):** A lightweight service that receives frame data and outputs DMX signals.

## 🛠️ Installation (Development)

### Prerequisites
* Python 3.14+
* Node.js & npm
* uv or standard pip

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install .

```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev

```

## 📄 License

Hyperion is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License version 3** or (at your option) any later version.

See [LICENSE](https://www.google.com/search?q=LICENSE) for more details.

## 💬 Community & Support

* **Found a bug?** Open an [Issue](https://github.com/Arian-Ott/hyperion/issues).
* **Have a feature request?** Start a [Discussion](https://github.com/Arian-Ott/hyperion/discussions).
* **Security vulnerability?** See [SECURITY.md](SECURITY.md).