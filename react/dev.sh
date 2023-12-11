#!/bin/bash

IMAGE_NAME="coffee_react_tag_watcher"

run_docker() {
  local working_dir=$1

  if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY is not set."
    exit 1
  fi
  local abs_working_dir=$(realpath "$working_dir")
  docker run -it -v "${abs_working_dir}":/mount -v "$(pwd)":/app -e OPENAI_API_KEY=$OPENAI_API_KEY $IMAGE_NAME
}

usage() {
  echo "===================="
  echo "Usage: ./dev [build|lint] WORKING_DIR"
  echo "Options:"
  echo "  build: Build Docker image"
  echo "  lint: Run linter"
  echo "WORKING_DIR is the path to the frontend directory to be mounted when running the container"
  echo "===================="
}

if [ "$1" = "build" ]; then
  docker build -t $IMAGE_NAME .
  exit 0
fi

if [ "$1" = "lint" ]; then
  docker run -it --init -v "$(pwd)":/app $IMAGE_NAME ruff check . --fix --watch
  exit 0
fi


if [ -z "$1" ]; then
  echo "Error: WORKING_DIR is mandatory for running the container."
  usage
  exit 1
fi

run_docker $1
