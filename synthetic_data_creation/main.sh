#!/bin/bash

# Define a cleanup function to kill the server
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
    fi
}

# Set the trap to call cleanup on script exit
trap cleanup EXIT

# Echo the path to the python executable
echo "Using python executable:"
which python

# Launch the server in the background
cd ../web-boardimage
pipenv run server &
SERVER_PID=$!
cd -

# Wait until the server is up
while ! curl -s http://127.0.0.1:8080 >/dev/null; do
    sleep 1
done

# Run your script that makes the request to localhost and pass all arguments to it
python main.py "$@"
