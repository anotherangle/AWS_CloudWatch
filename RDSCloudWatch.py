class RDS:
   def create_global_variable(self):
       self.ALARM_TYPES = ['CPUUtilization', 'NetworkIn']
   def __init__(self, ec2_client, cloudwatch_client):
       self.rds_client = rds_client
       self.cloudwatch_client = cloudwatch_client
       self.reservations = rds_client.describe_db_instances()["DBInstances"]
   def _readTags(self):
       #print self.arn
       tags = self.rds_client.list_tags_for_resource(ResourceName=self.arn,)
       #print tags["TagList"]
       self.tagsMap = dict([(tag["Key"], tag["Value"]) for tag in tags["TagList"] ])
       print self.tagsMap
       return self.tagsMap
   def manageAlarms(self):
       self.create_global_variable()
       for reservation in self.reservations:
           #print self.reservation["Instances"][0]["InstanceId"]
           self.instanceId =  reservation["DBInstanceIdentifier"]
           self.arn=reservation["DBInstanceArn"]
           print "Working on cloudwatch alarms of Instance %s" % (self.instanceId)
           self._readTags()
           for alarmType in self.ALARM_TYPES:
               self.manageAlarm(alarmType)
   def manageAlarm(self, alarmType):
       print "Managing alarm for %s" % (alarmType)
       if alarmType in self.tagsMap:
           self._createAlarm(alarmType)
       else:
           self._deleteAlarm(alarmType)
   def _getAlarmName(self, alarmType):
       return self.instanceId+'_' + alarmType
   def _deleteAlarm(self, alarmType):
       alarmName = self._getAlarmName(alarmType)
       print "Deleting alarm %s" % (alarmName)
       self.cloudwatch_client.delete_alarms(AlarmNames=[alarmName])
   def _createAlarm(self, alarmType):
       alarmName = self._getAlarmName(alarmType)
       print "Creating alarm %s" % (alarmName)
       threshold = float(self.tagsMap[alarmType])
       self.cloudwatch_client.put_metric_alarm(
           AlarmName=alarmName,
           ComparisonOperator='GreaterThanThreshold',
           EvaluationPeriods=1,
           MetricName=alarmType,
           Namespace='AWS/RDS',
           Period=60,
           Statistic='Average',
           Threshold=threshold,
           ActionsEnabled=False,
           AlarmDescription='Alarm when server CPU exceeds %',
           Dimensions=[
               {
                 'Name': 'InstanceId',
                 'Value': self.instanceId
               },
           ],
           Unit='Seconds'
       )


import boto3
region='us-east-1'
rds_client = boto3.client('rds',region_name='us-east-1',aws_access_key_id='*****',aws_secret_access_key='*****')
cloudwatch_client = boto3.client('cloudwatch',region_name='us-east-1',aws_access_key_id='******',aws_secret_access_key='*****')
print 'test'
r = RDS( rds_client, cloudwatch_client)
r.manageAlarms()
