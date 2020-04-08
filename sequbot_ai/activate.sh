# Run this from your bash using source
source .env/bin/activate
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
export PYTHONPATH=$PYTHONPATH:$(dirname "$(pwd)")
