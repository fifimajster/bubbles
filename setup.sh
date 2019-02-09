#!/usr/bin/env bash -e

echo "Downloading Neo4j..."
neo4j_url="https://neo4j.com/artifact.php?name="
tar_filename="neo4j-community-3.5.2-unix.tar.gz"
wget ${neo4j_url}${tar_filename} -O ${tar_filename}
tar -xf ${tar_filename}
rm ${tar_filename}