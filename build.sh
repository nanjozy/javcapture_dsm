source venv/bin/activate
rm -rf dist/lib
python setup.py build -b ./dist
rm -rf build/
rm -rf javcapture.egg-info/
cp ./entry_web.py ./dist/lib/
cp ./requirements.txt ./dist/lib/
cp ./gunicorn_cfg.py ./dist/lib/
docker build --rm -f ./dockerfile -t nanjozy/javcapture:v1.0 .
rm -f ./deploy/javcapture.tar
docker save -o ./dist/javcapture.tar nanjozy/javcapture:latest