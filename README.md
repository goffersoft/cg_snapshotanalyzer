# snapshotanlyzer
project to manage volume snapshots of EC2 instances 

## About

This project uses boto3 to manage aws ec2 instance snapshots

## Configuring

```
1) create ec2 instances using the aws-console -> ec2
2) create a user using the aws-console -> iam
3) download the user credentials file
4) configure aws profile on your local machine using aws cli
   (you will need the downloaded credentials)
5) make sure you give permissions to the user created earlier
   to access ec2 resources
```

## Running
pipenv run "python analyser/snapshotanalyzer.py"
