# Driverless AI Python SP within a PyFlink Data Pipeline

Deploy the Driverless AI Python Scoring Pipeline to Apache Flink Python Table by using the Scorer from the scoring_h2oai_experiment API and a custom Python Flink TableFunction. This will be a Cloudera Integration point for Cloudera Data Flow (CDF), particulary Cloudera Streaming Analytics(CSA). CSA is powered by Apache Flink. Apache Flink cluster is able to take Flink python jobs.

## Prerequisites

- Driverless AI Environment (Tested with Driverless AI 1.9.0.1)
- Launch Ubuntu 18.04 Linux EC2 instance
    - Instance Type: t2.2xlarge
    - Storage: 256GB
    - Open custom TCP port 8081 and source on 0.0.0.0/0

## Task 1: Set Up Environment

### Connect to EC2 from Local Machine

1\. Move the EC2 Pivate Key File (Pem Key) to the .ssh folder

~~~bash
mv $HOME/Downloads/{private-key-filename}.pem $HOME/.ssh/
chmod 400 $HOME/.ssh/{private-key-filename}.pem
~~~

2\. Set EC2 Public DNS and EC2 Pem Key as permanent environment variables

~~~bash
# For Mac OS X, set permanent environment variables 
tee -a $HOME/.bash_profile << EOF
# Set EC2 Public DNS
export DAI_PYSP_FLINK_INSTANCE={EC2 Public DNS}.compute.amazon.com
# Set EC2 Pem Key
export DAI_PYSP_FLINK_PEM=$HOME/.ssh/{private-key-filename}.pem
EOF

# For Linux, set permanent environment variables
tee -a $HOME/.profile << EOF
# Set EC2 Public DNS
export DAI_PYSP_FLINK_INSTANCE={EC2 Public DNS}.compute.amazon.com
# Set EC2 Pem Key
export DAI_PYSP_FLINK_PEM=$HOME/.ssh/{private-key-filename}.pem
EOF

source $HOME/.bash_profile
~~~

3\. Connect to EC2 via SSH

~~~bash
# Connect to EC2 instance using SSH
ssh -i $DAI_PYSP_FLINK_PEM ubuntu@$DAI_PYSP_FLINK_INSTANCE
~~~

### Create Environment Directory Structure

1\. Run the following commands that will create the directories where you could store the **input data**, **scoring-pipeline/** folder.

~~~bash
# Create directory structure for DAI Python Scoring Pipeline PyFlink Projects

# Create directory where the scoring-pipeline/ folder will be stored
mkdir $HOME/daipysp-pyflink/

# Create input directory used for batch scoring or real-time scoring
mkdir -p $HOME/daipysp-pyflink/test-data/{test-batch-data,test-real-time-data}
~~~

### Set Up Driverless AI Python Scoring Pipeline in EC2

1\. Build a Driverless AI Experiment

- 1a\. Upload your dataset or use the **S3 URL** to import the **Algorithm Generated Malicious Domains dataset**.

~~~bash
# S3 URL
https://s3.amazonaws.com/data.h2o.ai/dai-deployment-examples/maliciousdomains.csv

# S3 URL
s3://data.h2o.ai/dai-deployment-examples/maliciousdomains.csv
~~~

- 1b\. Split the data **75% for training** and **25% for testing**.

- 1c\. Run predict on your **training data**.

- 1d\. Name the experiment **model_deployment**. Choose the **target column** for scoring. Choose the **test data**. Launch the experiment.

2\. Click **Download MOJO Scoring Pipeline** in Driverless AI Experiment Dashboard since we will be using the **example.csv** data that comes with it later.

- 2a\. Select **Python**, click **Download MOJO Scoring Pipeline** and send **mojo.zip** to EC2.

~~~bash
# Move Driverless AI MOJO Scoring Pipeline to EC2 instance
scp -i $DAI_PYSP_FLINK_PEM $HOME/Downloads/mojo.zip ubuntu@$DAI_PYSP_FLINK_INSTANCE:/home/ubuntu/daipysp-pyflink/
~~~

- 2b\. Unzip **mojo.zip**. We will be using the **mojo-pipeline/** folder for it's **example.csv** data.

~~~bash
cd /home/ubuntu/daipysp-pyflink/
unzip mojo.zip
~~~

3. Click **Download Python Scoring Pipeline** in Driverless AI Experiment Dashboard
- 3a\. Send **scorer.zip** to EC2.

~~~bash
# Move Driverless AI Python Scoring Pipeline to EC2 instance
scp -i $DAI_PYSP_FLINK_PEM $HOME/Downloads/scorer.zip ubuntu@$DAI_PYSP_FLINK_INSTANCE:/home/ubuntu/daipysp-pyflink/
~~~

- 3b\. Unzip **scorer.zip**.

~~~bash

# Install Unzip for access to individual files in scoring pipeline folder
sudo apt-get -y install unzip
cd /home/ubuntu/daipysp-pyflink/
unzip scorer.zip
~~~

4. Install **Python Runtime Dependencies** in EC2

- 4a\. Download and install Anaconda

~~~bash
# Download Anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh

# Install Anaconda
bash Anaconda3-2020.02-Linux-x86_64.sh

source $HOME/.bashrc
~~~

- 4b\. Install the required packages:

~~~bash
# Make all packages available on EC2 instance
sudo apt-get -y update

# Install Python 3.6 and related packages
sudo apt-get -y install python3.6 python-virtualenv python3.6-dev python3-pip python3-dev python3-virtualenv

# Install OpenBLAS for linear algebra calculations
sudo apt-get -y install libopenblas-dev

# Install Java to include open source H2O-3 algorithms
sudo apt-get -y install openjdk-8-jdk

# Install tree for displaying environment directory structure
sudo apt-get -y install tree

# Install the thrift-compiler
sudo apt-get install automake bison flex g++ git libevent-dev \
  libssl-dev libtool make pkg-config libboost-all-dev ant

wget https://github.com/apache/thrift/archive/0.10.0.tar.gz
tar -xvf 0.10.0.tar.gz
cd thrift-0.10.0
./bootstrap.sh
./configure
make
sudo make install

# Refresh runtime after installing thrift
sudo ldconfig /usr/local/lib
~~~

4c\. Create **model-deployment** virtual environment and install env requirements

~~~bash
conda create -y -n model-deployment python=3.6
conda activate model-deployment

# Go to scoring-pipeline/ folder with requirements.txt
cd $HOME/daipysp-pyflink/scoring-pipeline

# Install gitdb2 and gitdb into env
pip install --upgrade gitdb2==2.0.6 gitdb==0.6.4

# Install dependencies
pip install -r requirements.txt
~~~

5\. Set the **Driverless AI License Key** as a **temporary environment variable**

~~~bash
# Set Driverless AI License Key
export DRIVERLESS_AI_LICENSE_KEY="{license-key}"
~~~

### Prepare Malicious Domains Test Data For PySp PyFlink Scoring

Make sure there is **input test data** in the input directory Flink will be pulling data from.

1\. For **batch scoring**, you should make sure there is one or more files with multiple rows of csv data in the following directory:

~~~bash
# go to mojo-pipeline/ directory with batch data example.csv
cd $HOME/daipysp-pyflink/mojo-pipeline/

# copy this batch data to the input dir where Flink pulls the batch data
cp example.csv $HOME/daipysp-pyflink/test-data/test-batch-data/
~~~

2\. For **real-time scoring**, you should make sure there are files with a single row of csv data in the following directory:

~~~bash
# go to real-time input dir where we will store real-time data
cd $HOME/daipysp-pyflink/test-data/test-real-time-data/

# copy example.csv to the input dir where Flink pulls the real-time data
cp $HOME/daipysp-pyflink/mojo-pipeline/example.csv .

# remove file's 1st line, the header
echo -e "$(sed '1d' example.csv)\n" > example.csv

# split file into multiple files having 1 row of data with numeric suffix and .csv extension
split -dl 1 --additional-suffix=.csv example.csv test_

# remove example.csv from real-time input dir
rm -rf example.csv
~~~

### Set Up Beam

1\. Download Apache Beam

~~~bash
pip install apache-beam
pip install apache-beam[test]
~~~

### Set Up Flink Local Cluster in EC2

1\. Download PyFlink

~~~bash
# Install PyFlink
python -m pip install apache-flink
~~~

2\. Download standalone Flink for Local Cluster

~~~bash
cd $HOME
# Download Flink
wget https://downloads.apache.org/flink/flink-1.11.1/flink-1.11.1-bin-scala_2.12.tgz

# Extract Flink tgz
tar -xvf flink-1.11.1-bin-scala_2.12.tgz
~~~

3\. Start the Local Flink Cluster

~~~bash
cd $HOME/flink-1.11.1

# Start Flink
./bin/start-cluster.sh

# Stop Flink
./bin/stop-cluster.sh
~~~

4\. Access the Flink UI: http://localhost:8081/#/overview

![flink-ui-overview](./assets/flink-ui-overview.jpg)

## Task 2: Deploy Python Scoring Pipeline to Flink

1\. Download **Driverless AI Deployment Examples** Repo for **PyFlink** assets

~~~bash
cd $HOME
git clone -b pysp-pyflink https://github.com/james94/dai-deployment-examples/
~~~

### Real-Time Scoring

For Driverless AI MOJO batch scoring in Flink, we will run the following PyFlink PySp ML Data Pipeline program **real-time-pred-mal-domains.py** by specifying this class as the entry point for the local Flink cluster to execute.

1\. Run the following command to submit the PyFlink PySp Stream Scoring Job for execution:

~~~bash
$HOME/flink-1.11.1/bin/flink run -py $HOME/dai-deployment-examples/pysp-pyflink/daipysp-pyflink-data-pipeline/classify-malicious-domains/real-time-pred-mal-domains.py
~~~

2\. Once the Flink job finishes running, it will transition to the Completed Job List:

3\. Check out the Data Pipeline diagram of the Flink Job **Deploy DAI Python SP within a PyFlink Streaming Pipeline**:

4\. View the Real-Time Scores for Malicious Domain Generated or Non-Generated by looking at the TaskManager's Stdout:

## Execute Flink Python Table API Program in a Local Mini Cluster

Prepare the input data in the "/tmp/input" file. 

~~~bash
echo -e  "flink\npyflink\nflink" > /tmp/input
~~~

Run this example (If the result file "/tmp/output" already exists, remove the file before running the example):

~~~bash
python WordCount.py
~~~

The command above builds and runs the Python Table API program in a local mini cluster. 

You can see the execution result:

~~~bash
cat /tmp/output
~~~

## Submit Flink Python Table API program to a Remote Cluster

Run Flink Python Table API program:

~~~bash
./bin/flink run -py path/to/word_count.py
~~~

## Execute Beam Pipeline on top of Flink

Run Apache Beam pipeline for word count on local Flink Cluster:

~~~bash
python -m apache_beam.examples.wordcount --input /path/to/inputfile \
                                         --output /path/to/write/counts \
                                         --runner FlinkRunner
~~~