rm -rf layer/
rm -f requirements.txt
mkdir -p layer/python
poetry install --only layer
poetry export --without-hashes --without-urls --only layer -o requirements.txt
pip install \
	--platform manylinux2014_x86_64 \
	--target=layer/python \
	--implementation cp \
	--python-version 3.11 \
	--only-binary=:all: --upgrade \
	-r requirements.txt
cd layer
zip -r layer.zip python
