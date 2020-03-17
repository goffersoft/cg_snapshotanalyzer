# snapshotanlyzer
project to manage volume snapshots of EC2 instances 

## About

This project ises boto3 to manage aws ec2 instance snapshots

## Configuring

```
1) create ec2 instances using the aws-console -> ec2
2) create user using the aws-console -> iam
3) download user crendtials file
4) configure aws profile on your local machine uses aws cli
   (you will need the downloaded credentials)
5) make sure you give permissions to the user created earlier
   to access ec2 resources
```

## Running
pipenv run "python analyser/snapshotanalyzer.py"
