python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo cp autolight.service /etc/systemd/user
systemctl --user enable autolight
systemctl --user start autolight