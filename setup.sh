#!/usr/bin/env bash -e

echo "Downloading Neo4j..."
neo4j_dir="neo4j-community-3.5.2"
tar_filename="${neo4j_dir}-unix.tar.gz"
wget "https://neo4j.com/artifact.php?name="${tar_filename} -O ${tar_filename}

tar -xf ${tar_filename}
rm ${tar_filename}

echo "Setup database"
default_password="myyyk"
${neo4j_dir}/bin/neo4j-admin set-initial-password ${default_password}
