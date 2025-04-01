source venv/bin/activate
export PROJECT=$(pwd)
export CLASS=$PROJECT/..
export PYTHONPATH=$CLASS/mitsuba3/build/python
export PATH=$CLASS/mitsuba3/build/:$PATH
export CC=clang-17
export CXX=clang++-17
