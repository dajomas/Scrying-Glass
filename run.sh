VDIR=~/dnd
if [[ ! -d ${VDIR} && ! -d ${VDIR}/bin ]]
then
	python3.14 -m venv ${VDIR}
	. ${VDIR}/bin/activate
	pip3 install pip --upgrade
	pip3 install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
else
	. ~/dnd/bin/activate
fi

python3.14 scrying_glass_server.py --config config.yaml
