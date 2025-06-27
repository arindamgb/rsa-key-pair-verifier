#!/bin/bash
docker rm -f rsa-key-pair-verifier
COMMIT_HASH=$(git rev-parse --short HEAD)
docker build -t arindamgb/rsa-key-pair-verifier:$COMMIT_HASH .
docker run -itd --name rsa-key-pair-verifier -p 5000:5000 arindamgb/rsa-key-pair-verifier:$COMMIT_HASH
