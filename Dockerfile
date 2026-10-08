FROM python:3.12-slim-bookworm
RUN sed -i s,http://deb.debian.org,https://deb.debian.org,g /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y --no-install-recommends ca-certificates libfontconfig1 libx11-6 libxcursor1 libxinerama1 libxrandr2 libxi6 libgl1 libasound2 && rm -rf /var/lib/apt/lists/*
COPY server/install_godot.py /tmp/install_godot.py
RUN python /tmp/install_godot.py && rm /tmp/install_godot.py
WORKDIR /app
COPY server/requirements.txt server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt
COPY godot godot
COPY web web
COPY server server
RUN useradd --create-home game && chown -R game:game /app
USER game
RUN godot --headless --path godot --editor --import
EXPOSE 8080
CMD ["python", "server/app.py"]
